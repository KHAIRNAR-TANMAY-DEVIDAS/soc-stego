# Part 4: The Detection Engine (core/image_stego_engine.py)

## Welcome to the Brain!

This is where the **real magic** happens. The detection engine is the core of our tool - it's where we analyze images, extract hidden data, and validate findings.

**Analogy:** If the project were a hospital:
- GUI = reception desk (where patients check in)
- Config = hospital policies and procedures
- Detection engine = diagnostic lab (where actual testing happens)

**File size:** ~450 lines of code
**Complexity:** High (but we'll explain everything!)

---

## What This File Does

The detection engine has several responsibilities:

1. **Load images** - Open image files using Pillow library
2. **Encode messages** - Hide secret messages in images (LSB technique)
3. **Decode messages** - Extract hidden messages from images
4. **Validate findings** - Apply 7 checks to reduce false positives
5. **Analyze images** - Complete analysis with metadata extraction
6. **XOR encryption/decryption** - Support for encrypted messages
7. **Interactive CLI** - Command-line interface for manual testing

---

## Understanding LSB Steganography

Before diving into code, let's understand the technique.

### What is LSB?

**LSB = Least Significant Bit**

Every pixel in a color image has three values (RGB):
- **R**ed: 0-255
- **G**reen: 0-255
- **B**lue: 0-255

Each value is stored as 8 bits (binary):
```
Example: Red = 156
Binary:  10011100
         ↑      ↑
        MSB    LSB
```

**Most Significant Bit (MSB):** Leftmost bit (has biggest impact on value)
**Least Significant Bit (LSB):** Rightmost bit (has smallest impact)

### The Trick

If you change the LSB, the color change is imperceptible:

```
Original:  10011100 = 156
Change LSB: 10011101 = 157

Difference: 156 → 157 (invisible to human eye!)
```

### Hiding Data

To hide "A" (binary: 01000001):
1. Take 8 pixels
2. For each RGB channel, replace its LSB with one bit of "A"
3. You can hide 1 bit per color channel = 3 bits per pixel

**Example:**
```
Original pixel 1: R=156, G=200, B=78
Message bit: 0
New R: Change LSB to 0 → 156 (already 0, no change)

Original pixel 1: G=200
Message bit: 1
New G: Change LSB to 1 → 201
```

The image looks exactly the same to humans, but now contains hidden data in the LSBs!

---

## Line-by-Line Explanation

### Section 1: Imports (Lines 1-5)

```python
from PIL import Image
import sys
import hashlib
import os
from datetime import datetime
```

**Line 1: PIL (Pillow)**
```python
from PIL import Image
```
- **PIL** = Python Imaging Library (Pillow is the modern version)
- `Image` class lets us open, create, and manipulate images
- Core functionality: load images, access pixels, save images

**What we use it for:**
- `Image.open()` - load image files
- `image.load()` - access pixel data
- `image.copy()` - create a copy for encoding
- `image.size` - get dimensions

---

**Line 2: sys**
```python
import sys
```
- System-specific parameters and functions
- Used for `sys.exit()` to quit the CLI program

---

**Line 3: hashlib**
```python
import hashlib
```
- Cryptographic hash functions
- Used for `hashlib.sha256()` to generate file hashes

**What is a hash?**
- A unique "fingerprint" of a file
- Same file = same hash
- Different file = different hash
- Used to verify file integrity

**Example:**
```python
hash = hashlib.sha256(b"Hello").hexdigest()
# Result: "185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969"
```

---

**Line 4: os**
```python
import os
```
- Operating system interface
- Used for `os.path.exists()` to check if files exist

---

**Line 5: datetime**
```python
from datetime import datetime
```
- Date and time functions
- Used for `datetime.now()` to timestamp analyses

---

### Section 2: EOF Marker Definition (Line 7-8)

```python
# MODIFICATION: Define the EOF marker as a binary string
EOF_MARKER = '1111111111111110'  # 16 bits unlikely to appear in normal text
```

**What is an EOF marker?**
- **EOF** = End Of File
- A special bit pattern marking the end of hidden messages
- Without it, we wouldn't know where the message stops

**Why this specific pattern?**
```
1111111111111110
```
- 15 ones followed by a zero
- **Very unlikely** to randomly occur in text data
- Distinctive enough to reliably detect

**How it works:**
```
Hidden message bits: 0100100001101001  ...  1111111111111110
                     ↑ Start of "Hi"          ↑ End marker
                                               Stop reading here!
```

**Without EOF marker:**
- We'd extract the entire image's LSBs
- Get thousands of bits of random garbage
- Can't tell where message ends

**With EOF marker:**
- Extract bits until we see the marker
- Stop immediately
- Clean message extraction

---

### Section 3: Validation Function (Lines 10-84)

This is the **most important function** for reducing false positives!

```python
def is_valid_steganography(message, bits_position, total_bits):
    """
    Validates if extracted data is likely real steganography or a false positive.
    
    Args:
        message (str): Extracted message
        bits_position (int): Bit position where EOF marker was found
        total_bits (int): Total available bits in image
    
    Returns:
        bool: True if likely real steganography, False if likely false positive
    """
```

**Function signature:**
- **Name:** `is_valid_steganography`
- **Parameters:**
  - `message` - the extracted text
  - `bits_position` - where we found the EOF marker
  - `total_bits` - total bits in image
- **Returns:** True (real) or False (false positive)

**Purpose:**
Finding an EOF marker doesn't guarantee real steganography! The marker might appear by random chance in normal images. This function applies **7 validation checks**.

---

#### Check 1: Minimum Length (Lines 19-21)

```python
    if not message:
        return False
    
    # Check 1: Message should not be too short (likely random EOF marker)
    if len(message) < 3:
        return False
```

**What it checks:**
- Message must be at least 3 characters

**Why?**
- Very short "messages" are probably random noise
- Real hidden messages are usually longer
- 1-2 characters unlikely to be intentional steganography

**Example:**
```python
message = "A"  # Too short
→ Return False (probably false positive)

message = "Hello world"  # Long enough
→ Pass this check, continue to next
```

---

#### Check 2: Character Diversity (Lines 23-26)

```python
    # Check 2: Message should not be all null bytes or single repeated character
    unique_chars = len(set(message))
    if unique_chars < 2:  # All same character = false positive
        return False
```

**What it checks:**
- Message must have at least 2 different characters

**Breaking down the code:**

**Line 24:** `unique_chars = len(set(message))`
- `set(message)` - creates a set (unique items only)
- Example: `set("AAABBB")` = `{'A', 'B'}` (only 2 unique)
- `len()` - counts unique characters

**Line 25:** Check if less than 2 unique
- If all characters are the same (or all null bytes)
- Probably random data, not real text

**Example:**
```python
message = "AAAAAAA"  # Only 'A'
unique_chars = 1
→ Return False

message = "Hi there"  # Multiple characters
unique_chars = 8  # H, i, space, t, h, e, r, e
→ Pass this check
```

---

#### Check 3: ASCII Printable Ratio (Lines 28-34)

```python
    # Check 3: Should have substantial ASCII printable characters (32-126 range)
    # Not extended ASCII or binary garbage
    ascii_printable = sum(1 for c in message if 32 <= ord(c) <= 126)
    ascii_ratio = ascii_printable / len(message)
    
    # If less than 70% standard ASCII printable, likely false positive
    if ascii_ratio < 0.7:
        return False
```

**What it checks:**
- At least 70% of characters should be standard printable ASCII

**Understanding ASCII:**
```
ASCII Values:
0-31:    Control characters (unprintable)
32-126:  Printable characters (letters, numbers, punctuation, space)
127-255: Extended ASCII (often garbage in random data)
```

**Line 31:** Count printable characters
```python
ascii_printable = sum(1 for c in message if 32 <= ord(c) <= 126)
```
- `ord(c)` - gets ASCII value of character
- `32 <= ord(c) <= 126` - checks if printable
- `sum(1 for ...)` - counts how many pass the test

**Line 32:** Calculate ratio
```python
ascii_ratio = ascii_printable / len(message)
```
- Ratio of printable to total characters

**Line 35:** Reject if too low
- If less than 70% printable → probably garbage

**Example:**
```python
message = "Hello!"  # All printable
ascii_printable = 6
ascii_ratio = 6/6 = 1.0 (100%)
→ Pass this check

message = "\x00\x01\x02ABC"  # Half unprintable
ascii_printable = 3
ascii_ratio = 3/6 = 0.5 (50%)
→ Return False (less than 70%)
```

---

#### Check 4: Must Have Letters (Lines 36-39)

```python
    # Check 4: Should contain common text characters (letters, spaces, punctuation)
    # Real text messages usually have letters
    has_letters = any(c.isalpha() for c in message)
    if not has_letters:
        return False
```

**What it checks:**
- Message must contain at least one letter (a-z, A-Z)

**Line 38:** Check for letters
```python
has_letters = any(c.isalpha() for c in message)
```
- `c.isalpha()` - returns True if character is a letter
- `any(...)` - returns True if at least one item is True

**Why this check?**
- Real text messages almost always have letters
- Numbers-only or symbols-only unlikely to be real messages
- Helps eliminate random data

**Example:**
```python
message = "12345!@#"  # No letters
has_letters = False
→ Return False

message = "Code 123"  # Has letters
has_letters = True
→ Pass this check
```

---

#### Check 5: Limit Extended ASCII (Lines 41-44)

```python
    # Check 5: Should not have too many high-bit characters (extended ASCII junk)
    high_bit_chars = sum(1 for c in message if ord(c) > 127)
    if high_bit_chars > len(message) * 0.3:  # More than 30% = likely garbage
        return False
```

**What it checks:**
- No more than 30% extended ASCII characters (128-255)

**Line 42:** Count high-bit characters
```python
high_bit_chars = sum(1 for c in message if ord(c) > 127)
```
- Characters above ASCII 127 are "extended" ASCII
- Often indicates random binary data

**Line 43:** Check percentage
- If more than 30% are high-bit → probably random garbage

**Example:**
```python
message = "Normal text"  # No extended ASCII
high_bit_chars = 0
0 > 11 * 0.3? → 0 > 3.3? → False
→ Pass this check

message = "\xFF\xFF\xFFABC"  # Half garbage
high_bit_chars = 3
3 > 6 * 0.3? → 3 > 1.8? → True
→ Return False
```

---

#### Check 6: EOF Position Not Too Early (Lines 46-50)

```python
    # Check 6: EOF marker should not appear too early in the image
    # Real steganography usually has at least a few characters before EOF
    min_expected_bits = 24  # At least 3 characters (3 * 8 bits)
    if bits_position < min_expected_bits:
        return False
```

**What it checks:**
- EOF marker should appear at least 24 bits (3 characters) into the image

**Line 48:** Define minimum
- 24 bits = 3 bytes = 3 characters
- Real messages are at least this long

**Line 49:** Check position
- If EOF marker found too early → probably random occurrence

**Example:**
```python
# EOF marker found at bit 16 (2 characters)
bits_position = 16
16 < 24? → True
→ Return False (too early, probably false positive)

# EOF marker found at bit 200 (25 characters)
bits_position = 200
200 < 24? → False
→ Pass this check
```

---

#### Check 7: Maximum Reasonable Length (Lines 52-55)

```python
    # Check 7: Message should not be excessive length (likely scanning into random data)
    max_reasonable_length = 10000  # 10KB of text is reasonable for steganography
    if len(message) > max_reasonable_length:
        return False
```

**What it checks:**
- Message shouldn't exceed 10,000 characters (10KB)

**Why?**
- Real LSB steganography typically hides small messages
- Extremely long "messages" suggest we're reading random image data
- 10KB is generous but prevents scanning entire images

**Example:**
```python
message = "Short secret"  # 12 characters
12 > 10000? → False
→ Pass this check

message = "..." (15,000 characters) 
15000 > 10000? → True
→ Return False (too long, probably not real steganography)
```

---

#### Function Return (Line 57)

```python
    return True
```

**If we reach this line:**
- Passed all 7 validation checks
- High confidence this is real steganography
- Return True

**Summary of 7 validation layers:**
1. ✓ At least 3 characters
2. ✓ At least 2 unique characters
3. ✓ At least 70% printable ASCII
4. ✓ Contains at least one letter
5. ✓ No more than 30% extended ASCII
6. ✓ EOF marker not too early
7. ✓ Message not excessively long

---

### Section 4: XOR Encryption Functions (Lines 59-72)

#### XOR Encrypt (Lines 59-71)

```python
def xor_encrypt(plaintext, key):
    """
    Encrypts a message using a simple XOR cipher with a string key.
    """
    ciphertext = ""
    key_len = len(key)
    
    for i in range(len(plaintext)):
        plain_char_code = ord(plaintext[i])
        key_char_code = ord(key[i % key_len])
        encrypted_char_code = plain_char_code ^ key_char_code
        ciphertext += chr(encrypted_char_code)
        
    return ciphertext
```

**What is XOR encryption?**
- XOR = "exclusive or" bitwise operation
- Simple but effective encryption
- Same key encrypts and decrypts

**How XOR works:**
```
0 XOR 0 = 0
0 XOR 1 = 1
1 XOR 0 = 1
1 XOR 1 = 0

Rule: Output is 1 only if inputs are different
```

**Example:**
```
Message: 'A' = 65 = 01000001
Key:     'K' = 75 = 01001011
XOR:             → 00001010 = 10 (encrypted)

To decrypt:
Encrypted: 10 = 00001010
Key:    'K'=75 = 01001011
XOR:          → 01000001 = 65 = 'A' (original!)
```

**Line-by-line:**

**Line 63:** Initialize empty result
**Line 64:** Store key length for reuse

**Line 66:** Loop through each character
```python
for i in range(len(plaintext)):
```

**Line 67:** Get ASCII value of message character
```python
plain_char_code = ord(plaintext[i])
```

**Line 68:** Get ASCII value of key character
```python
key_char_code = ord(key[i % key_len])
```
- `i % key_len` - wraps around if key is shorter than message
- Example: key="ABC", i=5 → 5 % 3 = 2 → use key[2]='C'

**Line 69:** XOR operation
```python
encrypted_char_code = plain_char_code ^ key_char_code
```
- `^` is the XOR operator in Python

**Line 70:** Convert back to character and append
```python
ciphertext += chr(encrypted_char_code)
```

**Line 72:** Return encrypted text

---

#### XOR Decrypt (Lines 74-77)

```python
def xor_decrypt(ciphertext, key):
    """
    Decrypts a message using the same XOR cipher and key.
    """
    return xor_encrypt(ciphertext, key)
```

**Beautiful simplicity!**
- XOR encryption is **symmetric**
- Encrypt twice with same key = back to original
- `encrypt(encrypt(text, key), key) = text`

**Why it works:**
```
Original XOR Key = Encrypted
Encrypted XOR Key = Original

Because: (A XOR B) XOR B = A
```

---

### Section 5: Image Loading Functions (Lines 79-96)

#### Load Image (Lines 79-92)

```python
def load_image(image_path):
    """
    Opens and loads an image from the specified path.
    Returns an Image object or None if the file is not found.
    """
    try:
        image = Image.open(image_path)
        print(f"  Image '{image_path}' loaded successfully.")
        return image
    except FileNotFoundError:
        print(f"  Error: The file '{image_path}' was not found.")
        return None
    except OSError:
        print(f"  Error: Cannot identify image file '{image_path}'.")
        return None
```

**Purpose:** Safely load an image file with error handling

**Line 84:** Try to open
```python
image = Image.open(image_path)
```
- Uses Pillow's Image.open()
- Returns an Image object

**Line 85:** Success message

**Line 86:** Return the image

**Line 87-89:** Handle file not found
- If file doesn't exist, print error
- Return None instead of crashing

**Line 90-92:** Handle invalid file
- If file exists but isn't a valid image
- Return None

**Usage:**
```python
img = load_image("photo.png")
if img is not None:
    # Process image
else:
    # Handle error
```

---

#### Save Image (Lines 94-99)

```python
def save_image(image_object, save_path):
    """
    Saves the given Image object to the specified path.
    """
    if image_object:
        image_object.save(save_path)
        print(f"  Image saved successfully to '{save_path}'.")
```

**Purpose:** Save an image to disk

**Line 97:** Check if image exists
```python
if image_object:
```

**Line 98:** Save it
```python
image_object.save(save_path)
```

**Line 99:** Confirm success

---

### Section 6: Encode Message (Lines 101-149)

This function **hides** a message in an image.

```python
def encode_message(image, secret_message, key=None):
    """
    Hides a secret message within an image using the LSB technique.
    If `key` is provided the message will be XOR-encrypted before embedding.
    Returns a new Image object with the message embedded.
    """
```

**Parameters:**
- `image` - PIL Image object to hide message in
- `secret_message` - text to hide
- `key` - optional XOR encryption key

**Returns:** New Image object with hidden message

---

**Lines 107-108:** Get dimensions
```python
width, height = image.size
```
- `image.size` returns tuple: (width, height)
- Unpacks into two variables

---

**Lines 110-113:** Optional encryption
```python
if key is not None:
    encrypted_message = xor_encrypt(secret_message, key)
else:
    encrypted_message = secret_message
```
- If key provided, encrypt message first
- Otherwise, use message as-is

---

**Lines 115-116:** Convert to binary
```python
message_binary = ''.join(format(ord(char), '08b') for char in encrypted_message)
message_binary += EOF_MARKER
```

**Line 115 breakdown:**
```python
''.join(format(ord(char), '08b') for char in encrypted_message)
```

Let's trace with "Hi":

**Step 1:** Loop through characters
- char = 'H'

**Step 2:** Get ASCII value
- `ord('H')` = 72

**Step 3:** Format as 8-bit binary
- `format(72, '08b')` = "01001000"
  - `08b` means: 8 digits, binary

**Step 4:** Join all together
- 'H' = "01001000"
- 'i' = "01101001"
- Result: "0100100001101001"

**Line 116:** Append EOF marker
- Add the special end marker to signal end of message

---

**Lines 118-120:** Check capacity
```python
max_bits = width * height * 3
if len(message_binary) > max_bits:
    raise ValueError("Error: Message is too large for this image.")
```

**Line 118:** Calculate capacity
- Each pixel has 3 color channels (RGB)
- Each channel can hold 1 bit
- Total capacity = width × height × 3 bits

**Example:**
```
Image: 100×100 pixels
Capacity: 100 × 100 × 3 = 30,000 bits = 3,750 bytes
Can hide: Up to 3,750 characters
```

**Line 119-120:** Validate size
- If message is too large, throw error

---

**Line 122:** Print status
```python
print(f"  Hiding a message of {len(message_binary)} bits (including EOF marker).")
```

---

**Lines 124-125:** Prepare for encoding
```python
encoded_image = image.copy()
pixel_map = encoded_image.load()
```

**Line 124:** Create a copy
- Don't modify original image
- Work on a copy

**Line 125:** Get pixel access object
- `image.load()` returns pixel map
- Allows reading/writing pixels efficiently

---

**Lines 127-147:** The encoding loop!

```python
data_index = 0
for y in range(height):
    for x in range(width):
        pixel = pixel_map[x, y]
        r, g, b = pixel[0], pixel[1], pixel[2]

        if data_index < len(message_binary):
            r = (r & 254) | int(message_binary[data_index])
            data_index += 1
        if data_index < len(message_binary):
            g = (g & 254) | int(message_binary[data_index])
            data_index += 1
        if data_index < len(message_binary):
            b = (b & 254) | int(message_binary[data_index])
            data_index += 1

        if len(pixel) == 4:
            a = pixel[3]
            pixel_map[x, y] = (r, g, b, a)
        else:
            pixel_map[x, y] = (r, g, b)

        if data_index >= len(message_binary):
            print("  Message embedded successfully.")
            return encoded_image
```

**Line 127:** Track position in message
```python
data_index = 0
```

**Lines 128-129:** Nested loop through all pixels
```python
for y in range(height):
    for x in range(width):
```
- Outer loop: rows (y coordinate)
- Inner loop: columns (x coordinate)
- Visits every pixel left-to-right, top-to-bottom

**Line 130:** Get current pixel
```python
pixel = pixel_map[x, y]
```
- Returns tuple: (R, G, B) or (R, G, B, A)

**Line 131:** Extract RGB values
```python
r, g, b = pixel[0], pixel[1], pixel[2]
```

**Lines 133-135:** Encode in red channel
```python
if data_index < len(message_binary):
    r = (r & 254) | int(message_binary[data_index])
    data_index += 1
```

**THIS IS THE KEY LINE!** Let's break it down:

```python
r = (r & 254) | int(message_binary[data_index])
```

**Part 1: `(r & 254)`**
- `&` is bitwise AND
- `254` in binary is `11111110`
- AND with 254 clears the LSB:
  ```
  r = 10011101 (157)
  &   11111110 (254)
  =   10011100 (156) ← LSB now 0
  ```

**Part 2: `| int(message_binary[data_index])`**
- `|` is bitwise OR
- `int(message_binary[data_index])` gets next bit (0 or 1)
- OR sets the LSB to our message bit:
  ```
  10011100 (cleared LSB)
  |      1 (our message bit)
  = 10011101 (LSB now set to our bit!)
  ```

**Complete example:**
```
Original R: 156 = 10011100
Message bit: 1
Step 1: Clear LSB → 10011100 (already 0)
Step 2: OR with 1 → 10011101 = 157
Result: R changed from 156 to 157 (imperceptible!)
```

**Lines 136-141:** Same for green and blue channels

**Lines 143-147:** Write pixel back
```python
if len(pixel) == 4:
    a = pixel[3]
    pixel_map[x, y] = (r, g, b, a)
else:
    pixel_map[x, y] = (r, g, b)
```
- If pixel has alpha channel (transparency), preserve it
- Otherwise, just write RGB

**Lines 149-151:** Done!
```python
if data_index >= len(message_binary):
    print("  Message embedded successfully.")
    return encoded_image
```
- Once all bits are embedded, return the image
- No need to continue looping

---

### Section 7: Decode Message (Lines 153-190)

This function **extracts** hidden messages.

```python
def decode_message(image, key=None):
    """
    Extracts a secret message from an image.
    If `key` is provided, the extracted message is decrypted with XOR using that key.
    """
```

**Parameters:**
- `image` - PIL Image object to extract from
- `key` - optional XOR decryption key

**Returns:** Extracted message string

---

**Lines 158-160:** Setup
```python
width, height = image.size
pixel_map = image.load()
extracted_bits = ""
```
- Get dimensions
- Get pixel access
- Initialize empty string for bits

---

**Lines 162-190:** Extraction loop
```python
for y in range(height):
    for x in range(width):
        pixel = pixel_map[x, y]

        for color_val in pixel[:3]:
            extracted_bits += str(color_val & 1)

            if extracted_bits.endswith(EOF_MARKER):
                print("  EOF marker found. Decoding complete.")
                message_binary = extracted_bits[:-len(EOF_MARKER)]
                message = ""
                
                for i in range(0, len(message_binary), 8):
                    byte = message_binary[i:i+8]
                    if len(byte) == 8:
                        try:
                            message += chr(int(byte, 2))
                        except ValueError:
                            print(f"  Warning: Invalid byte '{byte}', skipping.")
                
                if key is not None:
                    try:
                        decrypted_message = xor_decrypt(message, key)
                        return decrypted_message
                    except Exception as e:
                        print(f"  Decryption failed (maybe wrong key?): {e}")
                        return "[DECRYPTION FAILED]"
                
                return message

return "Could not find a hidden message."
```

**Lines 162-163:** Loop through all pixels

**Line 164:** Get pixel

**Line 166:** Loop through RGB channels
```python
for color_val in pixel[:3]:
```
- `pixel[:3]` gets first 3 values (RGB)
- Ignores alpha channel if present

**Line 167:** Extract LSB!
```python
extracted_bits += str(color_val & 1)
```

**This is extraction:**
```
color_val = 157 = 10011101
& 1              = 00000001
Result =           00000001 = 1

Gets the LSB (rightmost bit)!
```

**Line 169:** Check for EOF
```python
if extracted_bits.endswith(EOF_MARKER):
```
- After each bit, check if we've accumulated the EOF marker
- Example: "...010101111111111111110"
           Ends with our marker? Yes! Stop!

**Line 170:** Print status

**Line 171:** Remove EOF marker
```python
message_binary = extracted_bits[:-len(EOF_MARKER)]
```
- `[:-16]` removes last 16 characters (the marker)

**Line 172:** Initialize result

**Lines 174-180:** Convert binary to text
```python
for i in range(0, len(message_binary), 8):
    byte = message_binary[i:i+8]
    if len(byte) == 8:
        try:
            message += chr(int(byte, 2))
        except ValueError:
            print(f"  Warning: Invalid byte '{byte}', skipping.")
```

**Line 174:** Loop in steps of 8
- `range(0, len, 8)` gives: 0, 8, 16, 24, ...
- Each step processes one character (8 bits = 1 byte)

**Line 175:** Extract 8-bit slice
```python
byte = message_binary[i:i+8]
```
- Example: "01001000" (one character)

**Line 177:** Convert to character
```python
message += chr(int(byte, 2))
```
- `int(byte, 2)` converts binary string to integer
  - Example: int("01001000", 2) = 72
- `chr(72)` converts to character
  - chr(72) = 'H'

**Lines 182-188:** Optional decryption
- If key provided, decrypt the message
- If decryption fails, return error message

**Line 190:** Return message

**Line 192:** No EOF found
- If we scan entire image without finding EOF marker
- Return "Could not find a hidden message."

---

## Part 4 has grown quite long! Let me create a continuation as Part 4B for the analyze_image function and CLI functions.

---

**Previous:** [Part 3 - Configuration](Part_03_Configuration.md)
**Next:** [Part 4B - Detection Engine (Continued)](Part_04B_Detection_Engine_Continued.md)

---

*This is the heart of the steganography tool! Take your time understanding LSB manipulation and the validation layers. These concepts are fundamental to how the tool works.*
