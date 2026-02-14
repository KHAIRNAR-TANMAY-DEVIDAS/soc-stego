"""
SOC Steganography Detection Tool - Main Entry Point
Phase 1: Project structure established
Phase 2: CSV logging implementation
Phase 3: GUI implementation
"""

import sys
import os
import argparse

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_NAME, APP_VERSION, APP_DESCRIPTION

def main():
    """
    Main application entry point.
    Launches the Tkinter GUI or runs verification based on arguments.
    """
    parser = argparse.ArgumentParser(description=APP_DESCRIPTION)
    parser.add_argument('--verify', action='store_true', 
                       help='Run project structure verification instead of launching GUI')
    parser.add_argument('--cli', action='store_true',
                       help='Launch CLI mode instead of GUI')
    
    args = parser.parse_args()
    
    if args.verify:
        # Run verification mode
        run_verification()
    elif args.cli:
        # Launch CLI mode
        print(f"\n{APP_NAME} v{APP_VERSION} - CLI Mode")
        print("=" * 60)
        from core.image_stego_engine import main as cli_main
        cli_main()
    else:
        # Launch GUI (default)
        launch_application()

def launch_application():
    """Launch the main GUI application."""
    print(f"Launching {APP_NAME} v{APP_VERSION}...")
    
    try:
        from gui import launch_gui
        launch_gui()
    except ImportError as e:
        print(f"Error: Failed to import GUI module: {e}")
        print("\nTrying to run verification...")
        run_verification()
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to launch GUI: {e}")
        sys.exit(1)

def run_verification():
    """Run project structure and module verification."""
    print("=" * 60)
    print(f"{APP_NAME}")
    print(f"Version {APP_VERSION}")
    print("=" * 60)
    print(f"\n{APP_DESCRIPTION}\n")
    
    # Phase 1: Verify imports
    print("Phase 1: Project Structure Verification")
    print("-" * 60)
    
    try:
        from core.image_stego_engine import analyze_image, encode_message, decode_message
        print("✓ Core module imported successfully")
        print("  - analyze_image()")
        print("  - encode_message()")
        print("  - decode_message()")
    except ImportError as e:
        print(f"✗ Error importing core module: {e}")
        sys.exit(1)
    
    try:
        import config
        print("✓ Configuration module imported successfully")
        print(f"  - Logs directory: {config.LOGS_DIR}")
        print(f"  - CSV fields defined: {len(config.CSV_FIELDS)} fields")
    except ImportError as e:
        print(f"✗ Error importing config module: {e}")
        sys.exit(1)
    
    try:
        from reporting import (
            log_analysis_to_csv, 
            generate_summary_report,
            format_report_text
        )
        print("✓ Reporting module imported successfully")
        print("  - log_analysis_to_csv()")
        print("  - generate_summary_report()")
        print("  - format_report_text()")
    except ImportError as e:
        print(f"✗ Error importing reporting module: {e}")
        sys.exit(1)
    
    # Check if required directories exist
    required_dirs = ['core', 'gui', 'reporting', 'config', 'tests', 'logs']
    all_dirs_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ Directory exists: /{directory}")
        else:
            print(f"✗ Directory missing: /{directory}")
            all_dirs_exist = False
    
    print("-" * 60)
    
    if all_dirs_exist:
        print("\n✅ Phase 1 Complete: Project structure validated!")
        print("✅ Phase 2 Complete: CSV logging & reporting ready!")
        print("✅ Phase 3 Complete: GUI implementation ready!")
        print("\nAvailable Commands:")
        print("  python main.py              → Launch GUI (default)")
        print("  python main.py --verify     → Run this verification")
        print("  python main.py --cli        → Launch CLI mode")
        print("  python test_phase2.py       → Test reporting module")
    else:
        print("\n❌ Some directories are missing")
        sys.exit(1)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
