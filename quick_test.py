"""Quick test - just clean image"""
from core.image_stego_engine import analyze_image
import time

print("Testing clean image detection...")
start = time.time()
result = analyze_image('test_images/clean_test_image.png')
elapsed = time.time() - start

print(f"Analysis took {elapsed:.2f} seconds")
print(f"Has hidden data: {result['has_hidden_data']}")
print(f"Message: {result['hidden_message']}")

if not result['has_hidden_data']:
    print("✅ SUCCESS - No false positive!")
else:
    print("❌ FAILED - Still detecting false positive")
