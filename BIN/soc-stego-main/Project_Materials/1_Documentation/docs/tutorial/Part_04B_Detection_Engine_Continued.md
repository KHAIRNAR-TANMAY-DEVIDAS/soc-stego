# Part 4B: Detection Engine (Continued) - Analysis & CLI

## Continuing from Part 4...

In Part 4, we covered:
- LSB steganography concepts
- 7 validation layers
- XOR encryption/decryption
- Encode and decode functions

Now let's cover the remaining sections:
- The main analysis function (used by GUI)
- Interactive CLI functions
- How everything ties together

---

## Section 8: The analyze_image() Function (Lines 195-310)

This is the **most important function for the GUI** - it's what gets called when a user clicks "Analyze".

```python
def analyze_image(file_path, decode_key=None):
    """
    Analyzes an image file for steganography detection and metadata extraction.
    
    Args:
        file_path (str): Path to the image file to analyze
        decode_key (str, optional): XOR decryption key if message is encrypted
    
    Returns:
        dict: Structured analysis results containing:
            - status: 'success' or 'error'
            - file_path: Original file path
            - file_hash: SHA-256 hash of the file
            - file_size: File size in bytes
            - metadata: Image metadata (dimensions, format, mode, etc.)
            - hidden_message: Extracted message (if found)
            - has_hidden_data: Boolean indicating if EOF marker was found
            - timestamp: Analysis timestamp
            - error: Error message (if status is 'error')
    """
```

**Purpose:**
- Complete analysis of an image file
- Returns structured results (dictionary)
- Includes metadata extraction
- Applies validation layers
- Handles all errors gracefully

**Parameters:**
- `file_path` - path to image to analyze
- `decode_key` - optional decryption key

**Returns:**
- Dictionary with all analysis results

---

### Initialize Result Dictionary (Lines 212-223)

```python
    result = {
        'status': 'error',
        'file_path': file_path,
        'file_hash': None,
        'file_size': None,
        'metadata': {},
        'hidden_message': None,
        'has_hidden_data': False,
        'timestamp': datetime.now().isoformat(),
        'error': None
    }
```

**What is this?**
- A Python **dictionary** (key-value pairs)
- Like a form with labeled fields
- Will be filled in as analysis proceeds

**Default values:**
- `status: 'error'` - assume error until proven successful
- `file_path` - store the input path
- `file_hash: None` - will calculate later
- `file_size: None` - will calculate later
- `metadata: {}` - empty dictionary for image info
- `hidden_message: None` - will extract if found
- `has_hidden_data: False` - assume clean until proven otherwise
- `timestamp` - current time in ISO format
- `error: None` - will set if error occurs

**Why start with 'error' status?**
- If function crashes or returns early, status is already set
- Only change to 'success' if everything works
- Fail-safe approach

---

### Validate File Existence (Lines 225-228)

```python
    # Validate file existence
    if not os.path.exists(file_path):
        result['error'] = f"File not found: {file_path}"
        return result
```

**First check:** Does the file exist?

**Line 226:** `os.path.exists(file_path)`
- Returns True if file exists
- Returns False if not found

**Lines 227-228:** Handle missing file
- Set error message
- Return result immediately (early return)
- Status remains 'error'

---

### Try Block (Lines 230-308)

The rest of the function is wrapped in a `try-except` block to catch errors.

```python
    try:
        # ... all the analysis code ...
    except FileNotFoundError:
        result['error'] = f"File not found: {file_path}"
        return result
    except OSError as e:
        result['error'] = f"Cannot read image file: {str(e)}"
        return result
    except Exception as e:
        result['error'] = f"Analysis failed: {str(e)}"
        return result
```

**Purpose:** Catch any errors during analysis and return gracefully

---

### Calculate File Hash (Lines 231-235)

```python
        # Generate SHA-256 hash
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
            result['file_hash'] = hashlib.sha256(file_bytes).hexdigest()
            result['file_size'] = len(file_bytes)
```

**Line 232:** Open file in binary mode
```python
with open(file_path, 'rb') as f:
```
- `'rb'` = read binary mode
- `with` ensures file is closed when done
- `f` is the file handle

**Line 233:** Read entire file
```python
file_bytes = f.read()
```
- Reads all bytes into memory

**Line 234:** Calculate SHA-256 hash
```python
result['file_hash'] = hashlib.sha256(file_bytes).hexdigest()
```
- `hashlib.sha256(file_bytes)` - calculates hash
- `.hexdigest()` - converts to hexadecimal string
- Example: "a3b2c1d4e5f6..."

**Why hash?**
- Unique file fingerprint
- Verify file integrity
- Track exact file analyzed
- Important for forensics

**Line 235:** Store file size
```python
result['file_size'] = len(file_bytes)
```
- Size in bytes

---

### Load Image (Line 237-238)

```python
        # Load image
        image = Image.open(file_path)
```
- Opens image using Pillow
- Creates Image object

---

### Extract Metadata (Lines 240-253)

```python
        # Extract basic metadata
        result['metadata'] = {
            'format': image.format,
            'mode': image.mode,
            'width': image.size[0],
            'height': image.size[1],
            'dimensions': f"{image.size[0]}x{image.size[1]}",
            'total_pixels': image.size[0] * image.size[1],
            'max_capacity_bits': image.size[0] * image.size[1] * 3,
            'max_capacity_bytes': (image.size[0] * image.size[1] * 3) // 8
        }
```

**Creates metadata dictionary:**

**`format`:** File format
- Example: "PNG", "JPEG", "BMP"

**`mode`:** Color mode
- Example: "RGB", "RGBA", "L" (grayscale)

**`width` and `height`:** Dimensions in pixels

**`dimensions`:** Formatted string
- Example: "800x600"

**`total_pixels`:** Total number of pixels
- width × height

**`max_capacity_bits`:** Maximum bits that can be hidden
- pixels × 3 (RGB channels)
- Example: 800×600 image = 1,440,000 bits

**`max_capacity_bytes`:** Maximum bytes
- max_capacity_bits ÷ 8
- Example: 1,440,000 bits = 180,000 bytes = 180 KB

---

### Check for EXIF Data (Lines 255-259)

```python
        # Add EXIF data if available
        if hasattr(image, '_getexif') and image._getexif():
            result['metadata']['exif_present'] = True
        else:
            result['metadata']['exif_present'] = False
```

**What is EXIF?**
- **EX**changeable **I**mage **F**ile format
- Metadata stored in photos (camera model, date, GPS, etc.)

**Line 256:** Check if EXIF exists
```python
if hasattr(image, '_getexif') and image._getexif():
```
- `hasattr()` checks if object has an attribute
- `._getexif()` returns EXIF data or None

**Why track this?**
- Some forensic analyses care about EXIF
- Indicates if image is directly from camera vs edited

---

### LSB Extraction with Validation (Lines 261-306)

This is where the **real detection** happens, combining extraction with validation!

```python
        # Attempt LSB extraction using improved detection logic
        width, height = image.size
        pixel_map = image.load()
        extracted_bits = ""
        total_bits = width * height * 3
```

**Lines 262-265:** Setup
- Get dimensions
- Load pixel map
- Initialize bit string
- Calculate total available bits

---

**Lines 267-306:** The detection loop
```python
        for y in range(height):
            for x in range(width):
                pixel = pixel_map[x, y]
                
                for color_val in pixel[:3]:
                    extracted_bits += str(color_val & 1)
                    
                    # Check if we found the EOF marker
                    if extracted_bits.endswith(EOF_MARKER):
                        bits_position = len(extracted_bits)
                        message_binary = extracted_bits[:-len(EOF_MARKER)]
                        message = ""
                        
                        # Convert bits to characters
                        for i in range(0, len(message_binary), 8):
                            byte = message_binary[i:i+8]
                            if len(byte) == 8:
                                try:
                                    message += chr(int(byte, 2))
                                except ValueError:
                                    pass  # Skip invalid bytes silently
                        
                        # Validate if this is real steganography or false positive
                        if is_valid_steganography(message, bits_position, total_bits):
                            # Valid steganography detected!
                            # Apply XOR decryption if key provided
                            if decode_key is not None:
                                try:
                                    message = xor_decrypt(message, decode_key)
                                except Exception:
                                    result['error'] = "Decryption failed - possible wrong key"
                            
                            result['hidden_message'] = message
                            result['has_hidden_data'] = True
                            result['status'] = 'success'
                            return result
                        else:
                            # False positive detected - stop scanning
                            # This is likely random data, not real steganography
                            result['hidden_message'] = "No hidden message detected"
                            result['has_hidden_data'] = False
                            result['status'] = 'success'
                            return result
```

**Lines 267-269:** Loop through all pixels
- Same nested loop pattern as encoding

**Line 272:** Loop through RGB channels

**Line 273:** Extract LSB
```python
extracted_bits += str(color_val & 1)
```
- Get the least significant bit
- Add to accumulating bit string

**Line 276:** Check for EOF marker
```python
if extracted_bits.endswith(EOF_MARKER):
```
- After each bit, check if EOF marker appears at end

**Line 277:** Record position
```python
bits_position = len(extracted_bits)
```
- Needed for validation (Check 6)

**Line 278:** Remove EOF marker
```python
message_binary = extracted_bits[:-len(EOF_MARKER)]
```

**Lines 281-288:** Convert binary to text
- Same conversion logic as decode_message()
- 8 bits at a time → characters

**Line 290:** **VALIDATION!**
```python
if is_valid_steganography(message, bits_position, total_bits):
```
- Call our 7-layer validation function
- This is the **critical decision point**

**If validation passes (real steganography):**

**Lines 292-296:** Optional decryption
```python
if decode_key is not None:
    try:
        message = xor_decrypt(message, decode_key)
    except Exception:
        result['error'] = "Decryption failed - possible wrong key"
```

**Lines 298-301:** Set success results
```python
result['hidden_message'] = message
result['has_hidden_data'] = True
result['status'] = 'success'
return result
```
- Store the message
- Mark as having hidden data
- Status = success
- Return immediately

**If validation fails (false positive):**

**Lines 303-307:** Handle false positive
```python
else:
    result['hidden_message'] = "No hidden message detected"
    result['has_hidden_data'] = False
    result['status'] = 'success'
    return result
```
- Don't show the false message
- Mark as clean (no hidden data)
- Still success (analysis completed)
- Return immediately

**Key insight:** Finding EOF ≠ finding steganography!
- We might find the bit pattern by chance
- Validation determines if it's real or coincidence

---

### No EOF Found (Lines 309-313)

```python
        # Scanned entire image, no EOF marker found at all
        result['hidden_message'] = "No hidden message detected"
        result['has_hidden_data'] = False
        
        result['status'] = 'success'
        return result
```

**If we exit the loop without finding EOF:**
- No hidden message
- Status still success (analysis completed without error)

---

### Exception Handlers (Lines 315-324)

```python
    except FileNotFoundError:
        result['error'] = f"File not found: {file_path}"
        return result
    except OSError as e:
        result['error'] = f"Cannot read image file: {str(e)}"
        return result
    except Exception as e:
        result['error'] = f"Analysis failed: {str(e)}"
        return result
```

**Three levels of error handling:**

1. **FileNotFoundError:** File doesn't exist
2. **OSError:** Can't read file (permissions, corruption, etc.)
3. **Exception:** Any other error

Each sets the error message and returns result with 'error' status.

---

## Section 9: Interactive CLI Functions (Lines 327-429)

These functions provide a command-line interface for manual testing.

### Handle Encode (Lines 329-364)

```python
def handle_encode():
    """
    Guides the user through the encoding process.
    """
    print("\n--- ENCODING MODE ---")
    print("Please provide the following:")

    try:
        # 1. Get original image path
        original_path = input("> What is your original image? (e.g., test_image.png): ")
        original_img = load_image(original_path)
        if original_img is None:
            return  # Error message already printed by load_image

        # 2. Get secret message
        secret_message = input("> What message do you want to hide?: ")
        if not secret_message:
            print("  Error: Message cannot be empty.")
            return

        # 3. Get encryption key (optional)
        use_key = input("> Do you want to use an encryption key? (y/n): ").strip().lower()
        key = None
        if use_key == 'y':
            key = input("> What is your secret key?: ")
            if not key:
                print("  Error: Key cannot be empty.")
                return

        # 4. Get output file path
        save_path = input("> What do you want to name the new (output) file?: ")
        if not save_path:
            print("  Error: Output file name cannot be empty.")
            return

        # 5. Process
        print("\n  Processing...")
        encoded_img = encode_message(original_img, secret_message, key)
        save_image(encoded_img, save_path)
        
        print(f"\n✅ Success! Your secret message is now hidden in '{save_path}'.")

    except ValueError as e:
        print(f"\n  Error during encoding: {e}")
    except Exception as e:
        print(f"\n  An unexpected error occurred: {e}")
```

**Purpose:** Interactive wizard for hiding messages

**Flow:**
1. Print header
2. Ask for original image path
3. Load image (return if failed)
4. Ask for secret message
5. Validate not empty
6. Ask if they want encryption
7. If yes, ask for key
8. Ask for output filename
9. Encode message
10. Save new image
11. Print success

**User interaction example:**
```
--- ENCODING MODE ---
Please provide the following:
> What is your original image? (e.g., test_image.png): cat.png
  Image 'cat.png' loaded successfully.
> What message do you want to hide?: Secret message!
> Do you want to use an encryption key? (y/n): y
> What is your secret key?: mypassword
> What do you want to name the new (output) file?: cat_secret.png
  Processing...
  Hiding a message of 152 bits (including EOF marker).
  Message embedded successfully.
  Image saved successfully to 'cat_secret.png'.

✅ Success! Your secret message is now hidden in 'cat_secret.png'.
```

---

### Handle Decode (Lines 366-395)

```python
def handle_decode():
    """
    Guides the user through the decoding process.
    """
    print("\n--- DECODING MODE ---")
    print("Please provide the following:")

    try:
        # 1. Get stego image path
        stego_path = input("> What image do you want to decode? (e.g., secret.png): ")
        stego_img = load_image(stego_path)
        if stego_img is None:
            return

        # 2. Get encryption key (optional)
        use_key = input("> Do you know the encryption key? (y/n): ").strip().lower()
        key = None
        if use_key == 'y':
            key = input("> What is your secret key?: ")
            if not key:
                print("  Error: Key cannot be empty.")
                return

        # 3. Process
        print("\n  Processing...")
        hidden_message = decode_message(stego_img, key)
        
        print(f"\n✅ Success! The hidden message is:")
        print(f"{hidden_message}")

    except Exception as e:
        print(f"\n  An unexpected error occurred: {e}")
```

**Purpose:** Interactive wizard for extracting messages

**Flow:**
1. Print header
2. Ask for stego image path
3. Load image
4. Ask if they know the key
5. If yes, ask for key
6. Decode message
7. Print result

**User interaction example:**
```
--- DECODING MODE ---
Please provide the following:
> What image do you want to decode? (e.g., secret.png): cat_secret.png
  Image 'cat_secret.png' loaded successfully.
> Do you know the encryption key? (y/n): y
> What is your secret key?: mypassword
  Processing...
  EOF marker found. Decoding complete.

✅ Success! The hidden message is:
Secret message!
```

---

### Main CLI Menu (Lines 397-418)

```python
def main():
    """
    Main function to run the interactive menu.
    """
    print("\n--- LSB Steganography Tool ---")
    while True:
        print("\nWhat would you like to do?")
        print("  1. Hide (encode) a message in an image")
        print("  2. Find (decode) a message from an image")
        print("  3. Exit")
        
        choice = input("Enter your choice (1, 2, or 3): ").strip()

        if choice == '1':
            handle_encode()
        elif choice == '2':
            handle_decode()
        elif choice == '3':
            print("\nGoodbye!")
            sys.exit()
        else:
            print("\n  Invalid choice. Please enter 1, 2, or 3.")
```

**Purpose:** Main menu loop for CLI

**Line 403:** Infinite loop
```python
while True:
```
- Keeps showing menu until user exits

**Lines 404-407:** Display menu
- Shows 3 options
- Clear instructions

**Line 409:** Get user input
```python
choice = input("Enter your choice (1, 2, or 3): ").strip()
```
- `.strip()` removes extra whitespace

**Lines 411-418:** Handle choice
- 1 → encode
- 2 → decode
- 3 → exit
- Other → error message, loop continues

**User experience:**
```
--- LSB Steganography Tool ---

What would you like to do?
  1. Hide (encode) a message in an image
  2. Find (decode) a message from an image
  3. Exit
Enter your choice (1, 2, or 3): 1
[... encoding flow ...]

What would you like to do?
  1. Hide (encode) a message in an image
  2. Find (decode) a message from an image
  3. Exit
Enter your choice (1, 2, or 3): 3

Goodbye!
```

---

### Entry Point (Lines 420-422)

```python
# --- MAIN EXECUTION ---
if __name__ == '__main__':
    main()
```

**What this does:**
- If file is run directly: `python image_stego_engine.py`
- Then call `main()` (start CLI)

**Remember:** This pattern means:
- Run directly → Start CLI
- Import in other files → Just get the functions

---

## How Everything Works Together

### For GUI Usage:

```python
# In GUI code
from core.image_stego_engine import analyze_image

# User clicks "Analyze"
result = analyze_image("photo.png", decode_key="mykey")

# Check result
if result['status'] == 'success':
    if result['has_hidden_data']:
        print(f"Hidden message: {result['hidden_message']}")
    else:
        print("Image is clean")
else:
    print(f"Error: {result['error']}")
```

### For CLI Usage:

```bash
# Run directly
python core/image_stego_engine.py

# Interactive menu appears
# User selects encode/decode
# Follows prompts
```

### For Testing:

```python
# In test script
from core.image_stego_engine import encode_message, decode_message, load_image

# Create test image with hidden message
img = load_image("test.png")
encoded = encode_message(img, "Test message")
save_image(encoded, "test_encoded.png")

# Verify extraction
decoded_img = load_image("test_encoded.png")
message = decode_message(decoded_img)
assert message == "Test message"
```

---

## Key Takeaways

### 1. LSB Steganography
- Hides data in least significant bits of pixels
- Imperceptible visual change
- 3 bits per pixel (RGB)

### 2. Seven Validation Layers
1. Minimum length (3+ characters)
2. Character diversity (2+ unique)
3. ASCII printable ratio (70%+)
4. Must have letters
5. Limited extended ASCII (30% max)
6. EOF position not too early
7. Reasonable length limit (10KB max)

### 3. XOR Encryption
- Simple symmetric encryption
- Same function for encrypt and decrypt
- Key can be any string
- Repeats key if shorter than message

### 4. Complete Analysis
- File hashing (SHA-256)
- Metadata extraction
- LSB analysis with validation
- Structured result dictionary
- Graceful error handling

### 5. Dual Interface
- **GUI mode:** `analyze_image()` returns structured data
- **CLI mode:** Interactive menu for manual testing

---

## Testing the Engine

You can test the engine directly:

```bash
# Run CLI
python core/image_stego_engine.py

# Choose option 1 (encode)
# Hide a message in an image
# Choose option 2 (decode)
# Extract the message back
```

Or import in Python:

```python
from core.image_stego_engine import analyze_image

result = analyze_image("test_image.png")
print(result)
```

---

## Review Questions

1. **What does LSB stand for?** (Least Significant Bit)

2. **How many bits can one RGB pixel hide?** (3 bits - one per channel)

3. **What is the EOF marker used for?** (Marks the end of hidden messages)

4. **How many validation checks are applied?** (7 checks)

5. **What does XOR encryption require?** (A key/password)

6. **What does analyze_image() return?** (Dictionary with analysis results)

7. **Why is validation important?** (Reduces false positives from random EOF matches)

8. **What color channels does the tool use?** (RGB - Red, Green, Blue)

---

## What's Next?

In **Part 5**, we'll explore the GUI (Graphical User Interface):
- How the main window is built
- Button handlers and events
- Displaying results to users
- File dialogs
- Threading for responsive UI

You'll see how the detection engine integrates with a user-friendly interface!

---

**Previous:** [Part 4 - Detection Engine](Part_04_Detection_Engine.md)
**Next:** [Part 5 - The Graphical User Interface](Part_05_GUI.md)

---

*The detection engine is complex but powerful! Understanding bit manipulation and validation logic is crucial for any steganography project. Take your time with these concepts - they're the foundation of digital forensics.*
