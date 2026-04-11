# SOC Steganography Detection Tool - Project Structure Guide

**Last Updated:** February 14, 2026  
**Version:** 1.0.0  
**Purpose:** Complete guide to project organization and file purposes

---

## 📁 Directory Structure Overview

```
d:\TEST PROJECT\
│
├── 📄 main.py                          # Main entry point - Launch GUI or run CLI mode
├── 📄 config.py                        # Application configuration and constants
├── 📄 requirements.txt                 # Python dependencies for pip install
│
├── 📂 core/                            # Core detection engine modules
│   ├── __init__.py                     # Makes 'core' a Python package
│   └── image_stego_engine.py           # Main LSB steganography detection engine
│
├── 📂 gui/                             # Graphical User Interface modules
│   ├── __init__.py                     # Makes 'gui' a Python package
│   ├── main_window.py                  # Main GUI window with enhanced dashboard
│   └── file_dialog.py                  # File selection dialogs and utilities
│
├── 📂 reporting/                       # Report generation and logging modules
│   ├── __init__.py                     # Makes 'reporting' a Python package
│   ├── logger.py                       # CSV logging functionality
│   └── report_generator.py             # Summary report generation from CSV logs
│
├── 📂 tests/                           # All testing scripts and validation
│   ├── __init__.py                     # Makes 'tests' a Python package
│   ├── quick_test.py                   # Quick validation - generates test images
│   ├── test_detection_fix.py           # False positive validation tests
│   ├── test_phase2.py                  # Phase 2 CSV logging tests
│   ├── test_phase3_guide.py            # Phase 3 GUI testing guide
│   └── test_phase4_gui.py              # Phase 4 enhanced GUI test checklist
│
├── 📂 test_images/                     # Sample images for testing detection
│   ├── stegoTS1.png                    # Test image with hidden message 1
│   ├── stegoTS2.png                    # Test image with hidden message 2
│   ├── stegoTS3.png                    # Test image with hidden message 3
│   └── clean_test_image.png            # Clean image (no hidden data)
│
├── 📂 logs/                            # CSV logs and analysis records
│   ├── stego_analysis_*.csv            # Auto-generated analysis logs
│   ├── test_phase2_log.csv             # Phase 2 testing logs
│   └── real_test_log.csv               # Real detection testing logs
│
├── 📂 docs/                            # Documentation and reports
│   └── SAMPLE_ANALYSIS_REPORT_V1.md    # Professional SOC incident report template
│
├── 📂 config/                          # Configuration files (future use)
│   └── (Reserved for future config files)
│
├── 📄 README.md                        # Main project documentation
├── 📄 USAGE_GUIDE.md                   # SOC analyst usage guide
├── 📄 FINAL_TESTING_CHECKLIST.md       # Pre-presentation testing checklist
├── 📄 PRESENTATION_DEMO_SCRIPT.md      # Step-by-step demo script
└── 📄 PROJECT_STRUCTURE.md             # This file - project organization guide
```

---

## 📄 File Purposes - Detailed Breakdown

### 🚀 Core Application Files

#### `main.py`
- **Purpose:** Application entry point
- **Usage:** Run `python main.py` to launch GUI
- **Features:**
  - Launches Tkinter GUI interface
  - Can be modified for CLI mode
  - Handles application initialization
- **When to use:** Starting the tool

#### `config.py`
- **Purpose:** Centralized configuration settings
- **Contains:**
  - Application name and version
  - Color scheme for GUI
  - CSV field definitions
  - Default paths and constants
- **When to modify:** Changing app behavior, colors, or defaults

#### `requirements.txt`
- **Purpose:** Python package dependencies
- **Usage:** Run `pip install -r requirements.txt`
- **Contains:**
  - Pillow (image processing)
  - Other required packages
- **When to use:** Fresh installation or deployment

---

### 🔍 Core Detection Engine (`core/`)

#### `core/image_stego_engine.py`
- **Purpose:** Main steganography detection engine
- **Key Functions:**
  ```python
  analyze_image(image_path, decryption_key=None)  # Main detection function
  is_valid_steganography(extracted_data)         # 7-layer validation
  decode_message(image_path, decryption_key)     # Extract hidden message
  encode_message(image_path, message, key)       # Create test images
  ```
- **Features:**
  - LSB (Least Significant Bit) extraction
  - EOF marker detection
  - 7-layer validation system
  - XOR encryption/decryption support
- **When to modify:** Enhancing detection algorithms

#### `core/__init__.py`
- **Purpose:** Makes `core` a Python package
- **Contents:** Empty (allows `from core import image_stego_engine`)

---

### 🖼️ GUI Interface (`gui/`)

#### `gui/main_window.py`
- **Purpose:** Main application window (Phase 4 enhanced)
- **Features:**
  - Enhanced analysis results dashboard
  - Color-coded status indicators (🟢 green / 🔴 red)
  - Loading animations with progress bars
  - Scrollable results panel
  - Timestamp status bar
  - File selection and analysis controls
- **Key Methods:**
  ```python
  select_image()                  # File selection dialog
  analyze_image()                 # Trigger analysis
  display_analysis_results()      # Show results with formatting
  export_to_csv()                 # Export to CSV logs
  ```
- **When to modify:** Changing GUI layout or adding features

#### `gui/file_dialog.py`
- **Purpose:** File selection utilities
- **Features:**
  - Image file filters (PNG, JPG, BMP)
  - Directory browsing
  - File validation
- **When to modify:** Adding support for new file formats

#### `gui/__init__.py`
- **Purpose:** Makes `gui` a Python package

---

### 📊 Reporting System (`reporting/`)

#### `reporting/logger.py`
- **Purpose:** CSV logging for SIEM integration
- **Key Function:**
  ```python
  log_analysis_to_csv(analysis_result, csv_path)
  ```
- **CSV Fields (15 columns):**
  1. timestamp
  2. file_path
  3. file_name
  4. file_hash (SHA-256)
  5. file_size_bytes
  6. image_format
  7. image_dimensions
  8. image_mode
  9. max_capacity_bytes
  10. has_hidden_data
  11. hidden_message_length
  12. hidden_message_preview
  13. decryption_key_used
  14. analysis_status
  15. error_message
- **Output Location:** `logs/stego_analysis_YYYYMMDD_HHMMSS.csv`
- **When to use:** Every successful analysis (automated)

#### `reporting/report_generator.py`
- **Purpose:** Generate summary reports from CSV logs
- **Key Functions:**
  ```python
  generate_summary_report(csv_path)       # Statistics from single CSV
  format_report_text(report)              # Human-readable format
  export_report_to_file(report, path)     # Save to file
  compare_csv_logs(csv_paths)             # Compare multiple CSVs
  ```
- **When to use:** Generating analysis summaries from logs

#### `reporting/__init__.py`
- **Purpose:** Makes `reporting` a Python package

---

### 🧪 Testing Suite (`tests/`)

#### `tests/quick_test.py`
- **Purpose:** Quick validation and test image generation
- **Usage:** `python tests/quick_test.py`
- **Features:**
  - Generates test images with hidden messages
  - Validates detection engine works
  - Quick smoke test
- **When to use:** After code changes, before presentations

#### `tests/test_detection_fix.py`
- **Purpose:** False positive validation tests
- **Usage:** `python tests/test_detection_fix.py`
- **Tests:**
  - Clean images should show "NO hidden data"
  - Images with stego should show "YES"
  - 7-layer validation system checks
- **When to use:** Validating detection accuracy

#### `tests/test_phase2.py`
- **Purpose:** Phase 2 - CSV logging tests
- **Usage:** `python tests/test_phase2.py`
- **Validates:**
  - CSV file creation
  - All 15 fields logged correctly
  - SHA-256 hash generation
  - Error handling
- **When to use:** Testing logging functionality

#### `tests/test_phase3_guide.py`
- **Purpose:** Phase 3 - GUI testing guide
- **Contents:** Manual testing instructions for basic GUI
- **When to use:** GUI functionality verification

#### `tests/test_phase4_gui.py`
- **Purpose:** Phase 4 - Enhanced GUI test checklist
- **Contents:** 12-point manual test checklist
- **Tests:**
  - GUI launch
  - File selection
  - Analysis with test images
  - Results display
  - Color coding
  - CSV export
- **When to use:** Pre-presentation GUI validation

#### `tests/__init__.py`
- **Purpose:** Makes `tests` a Python package

---

### 🖼️ Test Images (`test_images/`)

#### `stegoTS1.png`
- **Contains:** Hidden message "this is secret msg 1"
- **Purpose:** Test detection with message 1
- **Usage:** Select in GUI to test positive detection

#### `stegoTS2.png`
- **Contains:** Hidden message "this is secret msg 2"
- **Purpose:** Test detection with message 2
- **Dimensions:** 2560x1440 (HD image)
- **Usage:** Primary demo image for presentations

#### `stegoTS3.png`
- **Contains:** Hidden message "this is secret msg 3"
- **Purpose:** Test detection with message 3
- **Usage:** Testing multiple detections

#### `clean_test_image.png`
- **Contains:** NO hidden data
- **Purpose:** Test that tool correctly identifies clean images
- **Usage:** Validate false positive prevention

**Note:** All test images generated using `encode_message()` function

---

### 📋 Logs Directory (`logs/`)

#### Auto-Generated Files
- **Format:** `stego_analysis_YYYYMMDD_HHMMSS.csv`
- **Purpose:** Timestamped analysis logs
- **Created:** Automatically when "Export to CSV" is clicked
- **Structure:** 15-column CSV format
- **SIEM Ready:** Can be imported into Splunk, ELK, QRadar

#### Test Log Files
- `test_phase2_log.csv` - Phase 2 testing output
- `real_test_log.csv` - Real-world detection testing

---

### 📚 Documentation (`docs/`)

#### `docs/SAMPLE_ANALYSIS_REPORT_V1.md`
- **Purpose:** Professional SOC incident report template
- **Contents:**
  - Automated report format (10,000+ words)
  - Technical analysis sections
  - MITRE ATT&CK mapping
  - IOCs and threat intelligence
  - SIEM integration formats (CEF, JSON, STIX 2.1)
  - NIST incident response tracking
  - Compliance assessments
  - Forensic chain of custody
- **Usage:** Showcase enterprise-grade reporting capability
- **When to use:** During presentations as example output

---

### 📖 Root Documentation Files

#### `README.md`
- **Purpose:** Main project documentation (500+ lines)
- **Contents:**
  - Project overview and features
  - Installation instructions
  - Usage guide (GUI and CLI)
  - Architecture diagram
  - Detection methodology
  - CSV log format reference
  - SOC integration details
  - Testing procedures
  - Future roadmap
- **Audience:** Evaluators, users, developers
- **When to use:** First file to read for project understanding

#### `USAGE_GUIDE.md`
- **Purpose:** SOC analyst operational guide (600+ lines)
- **Contents:**
  - Step-by-step analysis workflows
  - Result interpretation guide
  - CSV field reference
  - XOR encryption handling
  - Threat assessment matrix
  - Common use cases
  - Troubleshooting section
  - Best practices
- **Audience:** SOC analysts, security teams
- **When to use:** Operational reference for using the tool

#### `FINAL_TESTING_CHECKLIST.md`
- **Purpose:** Pre-presentation testing checklist (100+ tests)
- **Contents:**
  - 10 test suites (Installation, GUI, Detection, CSV, etc.)
  - Presentation readiness checklist
  - Q&A preparation
  - Demo preparation steps
  - Final sign-off checklist
- **Audience:** You (developer/presenter)
- **When to use:** Before presentations, before demo

#### `PRESENTATION_DEMO_SCRIPT.md`
- **Purpose:** Complete 5-7 minute demo script
- **Contents:**
  - Timed sections with talking points
  - Step-by-step demo workflow
  - Expected Q&A with answers
  - Contingency plans for technical issues
  - Presentation tips
  - Pre-demo checklist
- **Audience:** You (presenter)
- **When to use:** During practice and actual presentation

#### `PROJECT_STRUCTURE.md`
- **Purpose:** This file - project organization guide
- **When to use:** Understanding project layout

---

## 🎯 Quick Reference - Where to Find Things

### "I need to..."

| Task | File(s) to Use |
|------|----------------|
| **Launch the tool** | `python main.py` |
| **Test detection works** | `python tests/quick_test.py` |
| **Check false positives** | `python tests/test_detection_fix.py` |
| **Prepare for demo** | `PRESENTATION_DEMO_SCRIPT.md` |
| **Understand usage** | `USAGE_GUIDE.md` |
| **Install dependencies** | `pip install -r requirements.txt` |
| **See project overview** | `README.md` |
| **Test the GUI** | `python tests/test_phase4_gui.py` (then manual test) |
| **Generate test images** | `python tests/quick_test.py` |
| **View sample report** | `docs/SAMPLE_ANALYSIS_REPORT_V1.md` |
| **Check logs** | `logs/stego_analysis_*.csv` |
| **Modify detection algorithm** | `core/image_stego_engine.py` |
| **Change GUI appearance** | `gui/main_window.py` + `config.py` |
| **Add CSV fields** | `config.py` + `reporting/logger.py` |

---

## 🔧 Development Workflow

### For Making Changes:

1. **Modify detection logic** → Edit `core/image_stego_engine.py`
2. **Test changes** → Run `python tests/quick_test.py`
3. **Validate false positives** → Run `python tests/test_detection_fix.py`
4. **Test GUI** → Launch `python main.py` and use checklist
5. **Check CSV logging** → Run analysis and check `logs/` folder
6. **Update documentation** → Edit relevant `.md` files

### For Testing:

1. **Quick smoke test** → `python tests/quick_test.py`
2. **Full GUI test** → Follow `tests/test_phase4_gui.py` checklist
3. **Phase-specific tests** → Run `python tests/test_phaseX.py`
4. **Pre-demo final check** → Use `FINAL_TESTING_CHECKLIST.md`

### For Presentation:

1. **Practice demo** → Follow `PRESENTATION_DEMO_SCRIPT.md`
2. **Verify all tests pass** → Run all test scripts
3. **Check documentation** → Review README and USAGE_GUIDE
4. **Show sample report** → Open `docs/SAMPLE_ANALYSIS_REPORT_V1.md`

---

## 📊 Phase Completion Status

| Phase | Status | Key Files |
|-------|--------|-----------|
| **Phase 1: Structure** | ✅ Complete | All folders, config.py, main.py |
| **Phase 2: CSV Logging** | ✅ Complete | reporting/logger.py, tests/test_phase2.py |
| **Phase 3: Basic GUI** | ✅ Complete | gui/main_window.py, gui/file_dialog.py |
| **Phase 4: Enhanced GUI** | ✅ Complete | Updated main_window.py, tests/test_phase4_gui.py |
| **Phase 5: Batch Processing** | ⏭️ Skipped | (Planned for future) |
| **Phase 6: Documentation** | ✅ Complete | All .md files, sample report |

---

## 🎓 For Evaluators / Instructors

### Project Assessment Guide:

**Core Functionality:**
- Detection Engine: `core/image_stego_engine.py`
- GUI Implementation: `gui/main_window.py`
- Logging System: `reporting/logger.py`

**Testing & Validation:**
- All test files in `tests/` directory
- Test images in `test_images/`
- Test results in `logs/`

**Documentation:**
- Technical docs: `README.md`, `USAGE_GUIDE.md`
- Project organization: This file
- Professional reporting: `docs/SAMPLE_ANALYSIS_REPORT_V1.md`

**SOC Integration:**
- CSV export format (15 fields)
- MITRE ATT&CK framework implementation
- Professional incident reporting template

---

## 🚀 Quick Start Guide

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Quick test
python tests/quick_test.py

# 3. Launch GUI
python main.py

# 4. Test with sample images
# Select test_images/stegoTS2.png in GUI
# Click "Analyze Image"
# Should detect: "this is secret msg 2"

# 5. Export to CSV
# Click "Export to CSV"
# Check logs/stego_analysis_*.csv
```

---

## 📞 Support & Questions

**For questions about:**
- **File purposes** → This document
- **How to use the tool** → USAGE_GUIDE.md
- **Project overview** → README.md
- **Demo preparation** → PRESENTATION_DEMO_SCRIPT.md
- **Testing procedures** → FINAL_TESTING_CHECKLIST.md

---

**Last Updated:** February 14, 2026  
**Project Status:** ✅ Presentation Ready  
**Total Files:** 30+ files across 9 directories  
**Total Documentation:** 15,000+ words  
**Code:** ~2,000 lines of Python  
**Test Coverage:** 100+ test cases

---

**END OF PROJECT STRUCTURE GUIDE**
