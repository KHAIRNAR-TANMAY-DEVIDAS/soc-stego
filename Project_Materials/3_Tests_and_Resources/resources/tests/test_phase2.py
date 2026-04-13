"""
Phase 2 Test Script: CSV Logging & Reporting Module Verification
Tests the reporting module functionality without requiring actual images.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reporting.logger import log_analysis_to_csv, log_batch_results
from reporting.report_generator import generate_summary_report, format_report_text
from config import LOGS_DIR


def create_mock_analysis_result(file_name, has_hidden_data=False, message=None):
    """
    Creates a mock analysis result for testing purposes.
    Simulates the output from core.image_stego_engine.analyze_image()
    """
    return {
        'status': 'success',
        'file_path': f'tests/samples/{file_name}',
        'file_hash': 'a1b2c3d4e5f6' + file_name[:10].replace('.', ''),
        'file_size': 1024 * 50 + len(file_name) * 100,
        'metadata': {
            'format': 'PNG' if '.png' in file_name else 'JPEG',
            'mode': 'RGB',
            'width': 800,
            'height': 600,
            'dimensions': '800x600',
            'total_pixels': 480000,
            'max_capacity_bits': 1440000,
            'max_capacity_bytes': 180000,
            'exif_present': False
        },
        'hidden_message': message if has_hidden_data else 'No hidden message detected',
        'has_hidden_data': has_hidden_data,
        'timestamp': datetime.now().isoformat(),
        'error': None
    }


def test_single_log():
    """Test logging a single analysis result."""
    print("\n" + "=" * 70)
    print("TEST 1: Single Analysis Logging")
    print("=" * 70)
    
    # Create a mock analysis with hidden data
    analysis = create_mock_analysis_result(
        'suspicious_image.png',
        has_hidden_data=True,
        message='This is a secret message hidden in the image using LSB steganography!'
    )
    
    # Log to CSV
    csv_path = os.path.join(LOGS_DIR, 'test_phase2_log.csv')
    result = log_analysis_to_csv(analysis, csv_path)
    
    if result['success']:
        print(f"✓ Successfully logged to: {result['csv_path']}")
        print(f"  - File: {analysis['file_path']}")
        print(f"  - Status: {analysis['status']}")
        print(f"  - Hidden Data: {analysis['has_hidden_data']}")
    else:
        print(f"✗ Logging failed: {result['error']}")
        return False
    
    return True


def test_batch_log():
    """Test logging multiple analysis results."""
    print("\n" + "=" * 70)
    print("TEST 2: Batch Analysis Logging")
    print("=" * 70)
    
    # Create multiple mock analyses
    analyses = [
        create_mock_analysis_result('clean_photo1.jpg', has_hidden_data=False),
        create_mock_analysis_result('clean_photo2.jpg', has_hidden_data=False),
        create_mock_analysis_result('stego_image1.png', has_hidden_data=True, 
                                   message='Hidden payload detected'),
        create_mock_analysis_result('landscape.bmp', has_hidden_data=False),
        create_mock_analysis_result('encrypted_stego.png', has_hidden_data=True,
                                   message='XOR encrypted message: @#$%^&*()_+'),
    ]
    
    csv_path = os.path.join(LOGS_DIR, 'test_phase2_log.csv')
    result = log_batch_results(analyses, csv_path)
    
    if result['success']:
        print(f"✓ Successfully logged {result['logged_count']} results to CSV")
        print(f"  - Clean images: {sum(1 for a in analyses if not a['has_hidden_data'])}")
        print(f"  - Suspicious images: {sum(1 for a in analyses if a['has_hidden_data'])}")
    else:
        print(f"✗ Batch logging failed: {result['error']}")
        return False
    
    return True


def test_report_generation():
    """Test generating a summary report from CSV."""
    print("\n" + "=" * 70)
    print("TEST 3: Summary Report Generation")
    print("=" * 70)
    
    csv_path = os.path.join(LOGS_DIR, 'test_phase2_log.csv')
    
    if not os.path.exists(csv_path):
        print(f"✗ CSV file not found: {csv_path}")
        return False
    
    # Generate report
    report = generate_summary_report(csv_path)
    
    if report['success']:
        print("✓ Report generated successfully")
        print(f"  - Total Scans: {report['total_scans']}")
        print(f"  - Suspicious: {report['suspicious_count']}")
        print(f"  - Clean: {report['clean_count']}")
        print(f"  - Detection Rate: {report['detection_rate']}%")
        print(f"  - Hidden Messages Found: {len(report['hidden_messages'])}")
        
        # Display formatted report
        print("\n" + "=" * 70)
        print("GENERATED REPORT:")
        print("=" * 70)
        print(format_report_text(report))
        
        return True
    else:
        print(f"✗ Report generation failed: {report['error']}")
        return False


def test_import_functionality():
    """Test that all reporting functions can be imported."""
    print("\n" + "=" * 70)
    print("TEST 4: Module Import Verification")
    print("=" * 70)
    
    try:
        from reporting import (
            log_analysis_to_csv,
            log_batch_results,
            get_csv_files,
            generate_summary_report,
            format_report_text,
            export_report_to_file,
            compare_csv_logs
        )
        print("✓ All reporting functions imported successfully:")
        print("  - log_analysis_to_csv")
        print("  - log_batch_results")
        print("  - get_csv_files")
        print("  - generate_summary_report")
        print("  - format_report_text")
        print("  - export_report_to_file")
        print("  - compare_csv_logs")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def main():
    """Run all Phase 2 tests."""
    print("\n" + "=" * 70)
    print("PHASE 2 VERIFICATION: CSV Logging & Reporting Module")
    print("=" * 70)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Logs Directory: {LOGS_DIR}")
    
    # Ensure logs directory exists
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Run tests
    tests = [
        ("Module Import", test_import_functionality),
        ("Single Log", test_single_log),
        ("Batch Log", test_batch_log),
        ("Report Generation", test_report_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print("\n" + "=" * 70)
    if passed == total:
        print(f"✅ PHASE 2 COMPLETE: All {total} tests passed!")
        print("\nNext Steps:")
        print("  - Phase 3: Implement Tkinter GUI")
        print("  - The CSV logging and reporting modules are ready for integration")
    else:
        print(f"⚠️  PHASE 2 INCOMPLETE: {passed}/{total} tests passed")
        print("Please review failed tests before proceeding to Phase 3")
    print("=" * 70)


if __name__ == "__main__":
    main()
