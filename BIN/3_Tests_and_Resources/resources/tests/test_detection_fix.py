"""Test detection logic fix"""
from core.image_stego_engine import analyze_image

print("=" * 70)
print("TESTING IMPROVED DETECTION LOGIC")
print("=" * 70)

# Test clean image
print("\n1. Testing CLEAN IMAGE (clean_test_image.png):")
result = analyze_image('test_images/clean_test_image.png')
print(f"   Has hidden data: {result['has_hidden_data']}")
print(f"   Message: {result['hidden_message']}")
print(f"   Status: {'✓ CORRECT - No false positive' if not result['has_hidden_data'] else '✗ FAILED - False positive detected'}")

# Test stego image 2
print("\n2. Testing STEGO IMAGE (stegoTS2.png):")
result2 = analyze_image('test_images/stegoTS2.png')
print(f"   Has hidden data: {result2['has_hidden_data']}")
print(f"   Message: {result2['hidden_message']}")
print(f"   Status: {'✓ CORRECT - Hidden message found' if result2['has_hidden_data'] else '✗ FAILED - Missed hidden data'}")

# Test stego image 3
print("\n3. Testing STEGO IMAGE (setgoTS3.png):")
result3 = analyze_image('test_images/setgoTS3.png')
print(f"   Has hidden data: {result3['has_hidden_data']}")
print(f"   Message: {result3['hidden_message']}")
print(f"   Status: {'✓ CORRECT - Hidden message found' if result3['has_hidden_data'] else '✗ FAILED - Missed hidden data'}")

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

tests_passed = 0
if not result['has_hidden_data']:
    print("✓ Clean image correctly identified")
    tests_passed += 1
else:
    print("✗ Clean image false positive - FAILED")

if result2['has_hidden_data'] and "secret msg 2" in result2['hidden_message']:
    print("✓ Stego image 2 correctly detected")
    tests_passed += 1
else:
    print("✗ Stego image 2 not detected - FAILED")

if result3['has_hidden_data'] and "secret msg 3" in result3['hidden_message']:
    print("✓ Stego image 3 correctly detected")
    tests_passed += 1
else:
    print("✗ Stego image 3 not detected - FAILED")

print(f"\nPassed: {tests_passed}/3 tests")
if tests_passed == 3:
    print("✅ DETECTION LOGIC FIX SUCCESSFUL!")
else:
    print("⚠ DETECTION LOGIC NEEDS MORE WORK")
print("=" * 70)
