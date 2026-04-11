"""
SOC Steganography Detection Tool - Core Detection Engine
Focuses on DETECTION and ANALYSIS of LSB steganography (not creation).
"""

from PIL import Image
import hashlib
import os
from datetime import datetime
import math
from collections import Counter

# EOF marker pattern used to identify end of hidden messages
EOF_MARKER = '1111111111111110'  # 16-bit binary pattern


# ===========================
# VALIDATION FUNCTIONS
# ===========================

def is_valid_steganography(message, bits_position, total_bits):
    """
    Validates if extracted data is likely real steganography or a false positive.
    Uses 7-layer validation to prevent false detections.
    
    Args:
        message (str): Extracted message
        bits_position (int): Bit position where EOF marker was found
        total_bits (int): Total available bits in image
    
    Returns:
        bool: True if likely real steganography, False if likely false positive
    """
    if not message:
        return False
    
    # Layer 1: Minimum length check (likely random EOF marker if too short)
    if len(message) < 3:
        return False
    
    # Layer 2: Character diversity check (all same character = false positive)
    unique_chars = len(set(message))
    if unique_chars < 2:
        return False
    
    # Layer 3: ASCII printable ratio check (32-126 range)
    ascii_printable = sum(1 for c in message if 32 <= ord(c) <= 126)
    ascii_ratio = ascii_printable / len(message)
    if ascii_ratio < 0.7:  # Less than 70% printable = likely garbage
        return False
    
    # Layer 4: Letter presence check (real messages usually have letters)
    has_letters = any(c.isalpha() for c in message)
    if not has_letters:
        return False
    
    # Layer 5: Extended ASCII limit check (high-bit characters = likely garbage)
    high_bit_chars = sum(1 for c in message if ord(c) > 127)
    if high_bit_chars > len(message) * 0.3:  # More than 30% = garbage
        return False
    
    # Layer 6: EOF position validation (at least 3 characters before EOF)
    min_expected_bits = 24  # 3 characters * 8 bits
    if bits_position < min_expected_bits:
        return False
    
    # Layer 7: Maximum length check (prevent scanning into random data)
    max_reasonable_length = 10000  # 10KB is reasonable for steganography
    if len(message) > max_reasonable_length:
        return False
    
    return True


# ===========================
# DECRYPTION FUNCTIONS
# ===========================

def xor_decrypt(ciphertext, key):
    """
    Decrypts a message using XOR cipher with a string key.
    XOR is symmetric, so encryption and decryption use the same operation.
    
    Args:
        ciphertext (str): Encrypted message to decrypt
        key (str): Decryption key
    
    Returns:
        str: Decrypted plaintext message
    """
    plaintext = ""
    key_len = len(key)
    
    for i in range(len(ciphertext)):
        cipher_char_code = ord(ciphertext[i])
        key_char_code = ord(key[i % key_len])
        decrypted_char_code = cipher_char_code ^ key_char_code
        plaintext += chr(decrypted_char_code)
    
    return plaintext


# ===========================
# STATISTICAL ANALYSIS
# ===========================

def calculate_shannon_entropy(data_bytes):
    """
    Calculates the Shannon Entropy of a sequence of bytes.
    Reveals the mathematical randomness of data to detect encryption/compression.
    
    Args:
        data_bytes (list): List of byte integers (0-255).
        
    Returns:
        float: Entropy score (0.0 to 8.0, where 8.0 is total absolute randomness).
    """
    if not data_bytes:
        return 0.0
        
    entropy = 0.0
    length = len(data_bytes)
    counts = Counter(data_bytes)
    
    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
        
    return entropy

def calculate_entropy_from_bits(bits_list):
    """Helper to convert bit strings to bytes and calculate entropy."""
    if not bits_list:
        return 0.0
    byte_list = []
    for i in range(0, len(bits_list) - 7, 8):
        byte_list.append(int("".join(bits_list[i:i+8]), 2))
    return calculate_shannon_entropy(byte_list)

# ===========================
# DETECTION & ANALYSIS FUNCTIONS
# ===========================

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
    result = {
        'status': 'error',
        'file_path': file_path,
        'file_hash': None,
        'file_size': None,
        'metadata': {},
        'hidden_message': None,
        'entropy_score': 0.0,
        'has_hidden_data': False,
        'decryption_key_used': False,
        'timestamp': datetime.now().isoformat(),
        'error': None
    }
    
    # Validate file existence
    if not os.path.exists(file_path):
        result['error'] = f"File not found: {file_path}"
        return result
    
    try:
        # Generate SHA-256 hash
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
            result['file_hash'] = hashlib.sha256(file_bytes).hexdigest()
            result['file_size'] = len(file_bytes)
        
        # Load image
        image = Image.open(file_path)
        
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
        
        # Add EXIF data if available
        if hasattr(image, '_getexif') and image._getexif():
            result['metadata']['exif_present'] = True
        else:
            result['metadata']['exif_present'] = False
        
        # Attempt LSB extraction using improved fast bit-shift logic
        width, height = image.size
        pixel_map = image.load()
        
        extracted_bits_list = []
        total_bits = width * height * 3
        
        eof_target = int(EOF_MARKER, 2)
        eof_shift = 0
        bits_count = 0
        
        for y in range(height):
            for x in range(width):
                pixel = pixel_map[x, y]
                
                for color_val in pixel[:3]:
                    bit = color_val & 1
                    extracted_bits_list.append(str(bit))
                    bits_count += 1
                    
                    # Efficient bitwise sliding window check for EOF
                    eof_shift = ((eof_shift << 1) | bit) & 0xFFFF
                    
                    # Check if we found the EOF marker
                    if bits_count >= 16 and eof_shift == eof_target:
                        bits_position = bits_count
                        # Convert fast buffer string ignoring the EOF bits
                        message_binary = "".join(extracted_bits_list[:-16])
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
                            result['entropy_score'] = round(calculate_entropy_from_bits(extracted_bits_list), 4)
                            
                            # Apply XOR decryption if key provided
                            if decode_key is not None:
                                result['decryption_key_used'] = True
                                try:
                                    message = xor_decrypt(message, decode_key)
                                except Exception:
                                    result['error'] = "Decryption failed - possible wrong key"
                            
                            result['hidden_message'] = message
                            result['has_hidden_data'] = True
                            result['status'] = 'success'
                            return result
                        else:
                            # False positive detected - stop scanning, but log entropy up to here
                            result['entropy_score'] = round(calculate_entropy_from_bits(extracted_bits_list), 4)
                            result['hidden_message'] = f"No hidden message detected (False positive EOF). Entropy: {result['entropy_score']:.4f}"
                            result['has_hidden_data'] = False
                            result['status'] = 'success'
                            return result
        
        # Scanned entire image, no EOF marker found at all
        # Step 2: Advanced Statistical Fallback (Entropy Analysis)
        entropy_score = round(calculate_entropy_from_bits(extracted_bits_list), 4)
        result['entropy_score'] = entropy_score
        
        from config import ENTROPY_THRESHOLD
        if entropy_score >= ENTROPY_THRESHOLD:
            # Mathematical anomaly detected
            result['has_hidden_data'] = True
            result['status'] = 'success'
            result['hidden_message'] = (
                f"WARNING: High Randomness Detected.\n"
                f"No EOF signature found, but LSB Shannon Entropy is {entropy_score:.4f} (Threshold: {ENTROPY_THRESHOLD}).\n"
                f"This mathematical anomaly indicates a highly probable encrypted or compressed steganographic payload."
            )
            return result
        else:
            result['hidden_message'] = f"Image clean. LSB Entropy: {entropy_score:.4f} (Normal range)"
            result['has_hidden_data'] = False
        
        result['status'] = 'success'
        return result
        
    except FileNotFoundError:
        result['error'] = f"File not found: {file_path}"
        return result
    except OSError as e:
        result['error'] = f"Cannot read image file: {str(e)}"
        return result
    except Exception as e:
        result['error'] = f"Analysis failed: {str(e)}"
        return result

