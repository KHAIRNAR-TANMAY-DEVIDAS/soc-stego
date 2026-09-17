"""Automated local tests for stego encode/decode roundtrip.

Usage: python tools/test_stego_roundtrip.py
"""
import sys
import os
import tempfile

from PIL import Image

from core.stego_tool_engine import encode_message, decode_message


def make_dummy_image(path):
    img = Image.new("RGBA", (64, 64), (200, 200, 200, 255))
    img.save(path)


def run_tests():
    tmpdir = tempfile.mkdtemp(prefix="stego_test_")
    try:
        src = os.path.join(tmpdir, "test_dummy.png")
        out_enc = os.path.join(tmpdir, "test_dummy_out.png")

        make_dummy_image(src)

        secret = "This is a secret message."
        password = "correcthorsebatterystaple"

        print("[TEST] Encoding with password...")
        try:
            encode_message(src, secret, out_enc, password=password)
            print("[OK] Encode completed")
        except Exception as e:
            print(f"[FAIL] Encode failed: {e}")
            return 2

        print("[TEST] Decoding with correct password...")
        try:
            res = decode_message(out_enc, password=password)
            if res != secret:
                print(f"[FAIL] Decoded message mismatch: {res}")
                return 3
            print("[OK] Correct password decode verified")
        except Exception as e:
            print(f"[FAIL] Decode failed with correct password: {e}")
            return 4

        print("[TEST] Decoding with incorrect password (expect failure)...")
        try:
            res2 = decode_message(out_enc, password="wrongpassword")
            print(f"[FAIL] Decode unexpectedly succeeded with wrong password: {res2}")
            return 5
        except Exception:
            print("[OK] Incorrect password correctly raised an error")

        # Test without password
        out_enc2 = os.path.join(tmpdir, "test_dummy_out_plain.png")
        print("[TEST] Encoding without password...")
        try:
            encode_message(src, secret, out_enc2, password=None)
            print("[OK] Plain encode completed")
        except Exception as e:
            print(f"[FAIL] Plain encode failed: {e}")
            return 6

        print("[TEST] Decoding plain image (no password)...")
        try:
            r3 = decode_message(out_enc2, password=None)
            if r3 != secret:
                print(f"[FAIL] Plain decoded mismatch: {r3}")
                return 7
            print("[OK] Plain decode verified")
        except Exception as e:
            print(f"[FAIL] Plain decode error: {e}")
            return 8

        print("All tests passed.")
        return 0
    finally:
        # Do not remove files to aid debugging; leave temp folder
        print(f"Temporary files in: {tmpdir}")


if __name__ == "__main__":
    code = run_tests()
    sys.exit(code)
