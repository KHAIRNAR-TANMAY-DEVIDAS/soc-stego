import os
import struct
import base64
from typing import Optional

from PIL import Image

try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.fernet import Fernet
except Exception:  # pragma: no cover - cryptography may be optional
    PBKDF2HMAC = None  # type: ignore
    hashes = None  # type: ignore
    Fernet = None  # type: ignore


_SALT_LEN = 16
_HEADER_FMT = "!BI"  # 1 byte flag, 4 byte unsigned int length


def _derive_key(password: str, salt: bytes) -> bytes:
    if PBKDF2HMAC is None:
        raise RuntimeError("cryptography library is required for password operations")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def _encrypt(data: bytes, password: str) -> bytes:
    salt = os.urandom(_SALT_LEN)
    key = _derive_key(password, salt)
    token = Fernet(key).encrypt(data)
    return salt + token


def _decrypt(payload: bytes, password: str) -> bytes:
    if len(payload) < _SALT_LEN:
        raise ValueError("payload too short to contain salt")
    salt = payload[:_SALT_LEN]
    token = payload[_SALT_LEN:]
    key = _derive_key(password, salt)
    return Fernet(key).decrypt(token)


def _bytes_to_bits(data: bytes):
    for byte in data:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1


def _bits_to_bytes(bits):
    b = 0
    count = 0
    out = bytearray()
    for bit in bits:
        b = (b << 1) | (bit & 1)
        count += 1
        if count == 8:
            out.append(b)
            b = 0
            count = 0
    return bytes(out)


def encode_message(image_path: str, secret_message: str, output_path: str, password: Optional[str] = None) -> None:
    """Embed `secret_message` into `image_path` and save as `output_path` (lossless PNG/BMP).

    If `password` is provided the message is encrypted before embedding.
    """
    img = Image.open(image_path)
    img = img.convert("RGBA")
    width, height = img.size
    pixels = list(img.getdata())

    payload = secret_message.encode("utf-8")
    encrypted_flag = 0
    if password:
        if Fernet is None:
            raise RuntimeError("cryptography package is required for encryption")
        payload = _encrypt(payload, password)
        encrypted_flag = 1

    # Header: 1 byte flag, 4 bytes length
    header = struct.pack(_HEADER_FMT, encrypted_flag, len(payload))
    full = header + payload
    bits = list(_bytes_to_bits(full))

    capacity = width * height * 3
    if len(bits) > capacity:
        raise ValueError(f"Message too large to embed: needs {len(bits)} bits, capacity {capacity}")

    # Embed bits into pixel LSBs (skip alpha channel)
    pixels = list(img.getdata())
    required_pixels = (len(bits) + 2) // 3
    
    new_pixels = pixels[:required_pixels]
    modified = []
    bit_iter = iter(bits)
    
    for r, g, b, a in new_pixels:
        new_r = (r & ~1)
        new_g = (g & ~1)
        new_b = (b & ~1)
        try:
            new_r |= next(bit_iter)
            new_g |= next(bit_iter)
            new_b |= next(bit_iter)
        except StopIteration:
            pass
        modified.append((new_r, new_g, new_b, a))

    # Combine modified pixels and untouched pixels
    final_pixels = modified + pixels[required_pixels:]

    out = Image.new("RGBA", (width, height))
    out.putdata(final_pixels)

    # Ensure lossless output format
    out_format = os.path.splitext(output_path)[1].lower()
    if out_format not in {".png", ".bmp"}:
        # default to PNG if extension is not lossless
        output_path = os.path.splitext(output_path)[0] + ".png"

    out.save(output_path)


def decode_message(image_path: str, password: Optional[str] = None) -> str:
    """Extract hidden message from `image_path`. If `password` provided, will attempt decryption."""
    img = Image.open(image_path)
    img = img.convert("RGBA")
    
    pixel_data = img.getdata()
    
    # Lazy bit generator
    def bit_generator():
        for r, g, b, a in pixel_data:
            yield r & 1
            yield g & 1
            yield b & 1
            
    bit_iter = bit_generator()

    # First 1+4 bytes => 40 bits header
    header_bits = [next(bit_iter) for _ in range(40)]
    header_bytes = _bits_to_bytes(header_bits)
    try:
        flag, length = struct.unpack(_HEADER_FMT, header_bytes)
    except struct.error:
        raise ValueError("No valid header found in image")

    # Read exactly needed bytes
    payload_bits = []
    total_payload_bits = length * 8
    try:
        for _ in range(total_payload_bits):
            payload_bits.append(next(bit_iter))
    except StopIteration:
        raise ValueError("Image does not contain full payload")

    payload = _bits_to_bytes(payload_bits)

    if flag == 1:
        if password is None:
            raise ValueError("Payload is encrypted but no password was provided")
        payload = _decrypt(payload, password)

    return payload.decode("utf-8")
