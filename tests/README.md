# Testing Suite - Test Files Guide

## Purpose
This directory contains all testing scripts for the SOC Steganography Detection Tool.

---

## Test Files

### `quick_test.py`
**Purpose:** Quick validation and test image generation  
**Usage:** `python tests/quick_test.py`  
**What it does:**
- Generates test images with hidden messages
- Validates detection engine is working
- Quick smoke test before demos

**Run this:** After any code changes to verify nothing broke

---

### `test_detection_fix.py`
**Purpose:** False positive validation tests  
**Usage:** `python tests/test_detection_fix.py`  
**What it tests:**
- Clean images correctly identified as "NO hidden data"
- Images with steganography correctly identified as "YES"
- 7-layer validation system works properly

**Run this:** To validate detection accuracy

---

### `test_phase2.py`
**Purpose:** Phase 2 - CSV logging functionality tests  
**Usage:** `python tests/test_phase2.py`  
**What it tests:**
- CSV file creation
- All 15 fields logged correctly
- SHA-256 hash generation
- Error handling in logger

**Run this:** To verify CSV export works

---

### `test_phase3_guide.py`
**Purpose:** Phase 3 - Basic GUI testing guide  
**Usage:** Open and read instructions (manual testing guide)  
**What it contains:**
- Manual testing checklist for basic GUI
- Step-by-step verification procedures

**Use this:** For manual GUI testing (basic features)

---

### `test_phase4_gui.py`
**Purpose:** Phase 4 - Enhanced GUI test checklist  
**Usage:** Open and follow 12-point checklist (manual testing)  
**What it tests:**
- GUI launch and interface
- File selection
- Analysis with test images (stegoTS1/2/3)
- Results display and formatting
- Color-coded indicators
- CSV export functionality

**Use this:** Pre-presentation final GUI validation

---

## Running All Tests

```bash
# Run automated tests
python tests/quick_test.py
python tests/test_detection_fix.py
python tests/test_phase2.py

# Follow manual test procedures
# Open test_phase4_gui.py and complete checklist
```

---

## Test Images
Test images are located in: `../test_images/`
- stegoTS1.png - Contains "this is secret msg 1"
- stegoTS2.png - Contains "this is secret msg 2"
- stegoTS3.png - Contains "this is secret msg 3"
- clean_test_image.png - No hidden data (clean)

---

**Status:** All tests organized in this directory  
**Last Updated:** February 14, 2026
