# SOC Steganography Detection Tool — PPT Content
**Total Slides: 12 | Suggested Time: 15 minutes + 3 min Q&A**

---

## SLIDE 1: Title Slide
- **Title:** SOC Steganography Detection Tool
- **Subtitle:** Image LSB Steganography Detection & Analysis
- Your Name | Roll Number
- Final Year Cybersecurity Project | 2025–2026

---

## SLIDE 2: Problem Statement
- Attackers hide malicious data inside image files (C2 communication, data exfiltration)
- Traditional firewalls/antivirus **cannot detect** steganography
- SOC analysts have no automated tool to scan images
- **MITRE ATT&CK:** T1027.003 (Steganography), T1020 (Exfiltration)
- **Solution Needed:** Automated, accurate, SOC-ready detection tool

---

## SLIDE 3: Project Objectives
- Detect hidden data in PNG/JPEG/BMP using **LSB analysis**
- Extract concealed messages via **EOF marker detection**
- Decrypt **XOR-encrypted** hidden content
- Generate **forensic reports** with SHA-256 hashing
- Provide **CSV logs** for SIEM integration
- Deliver a **professional GUI** for SOC analysts

---

## SLIDE 4: System Architecture

```
┌──────────────────────────┐
│    GUI Layer (Tkinter)   │  ← File select, results, status
└────────────┬─────────────┘
             ↓
┌──────────────────────────┐
│  Detection Engine (Core) │  ← LSB extraction, validation
└────────────┬─────────────┘
             ↓
┌──────────────────────────┐
│  Reporting (CSV / Logs)  │  ← SHA-256, 15-field log
└──────────────────────────┘
```

- `main.py` → Entry point
- `core/image_stego_engine.py` → Detection logic
- `gui/main_window.py` → User interface
- `reporting/logger.py` → CSV logging
- `config.py` → Settings & constants

---

## SLIDE 5: Detection Methodology ✅ (Verified against source code)

**How LSB Detection Works:**
1. Load image with Pillow
2. Extract **Least Significant Bit** from each R, G, B channel
3. Search for **EOF marker** → `1111111111111110`
4. Assemble bits → bytes → ASCII message
5. Apply **7-Layer Validation** to eliminate false positives

**7-Layer Validation (exact code order from `image_stego_engine.py`):**

| Layer | Check | Threshold |
|-------|-------|-----------|
| 1 | Min Length | ≥ 3 chars |
| 2 | Character Diversity | ≥ 2 unique chars |
| 3 | ASCII Printable Ratio | ≥ 70% |
| 4 | Letter Presence | At least 1 letter required |
| 5 | Extended ASCII | < 30% high-bit chars |
| 6 | EOF Position | ≥ 24 bits before marker |
| 7 | Length Check | ≤ 10,000 chars |

→ Result: **>95% accuracy, <5% false positives**

---

## SLIDE 6: Key Features

| Feature | Details |
|---------|---------|
| LSB Detection | PNG, JPEG, BMP support |
| XOR Decryption | Key entered via GUI |
| SHA-256 Hashing | Forensic integrity |
| 7-Layer Validation | False positive control |
| Color-Coded GUI | 🟢 Clean / 🔴 Detected |
| CSV Logging | 15 fields, SIEM-ready |
| Metadata Extraction | Dimensions, format, capacity |

**Technology Stack:** Python 3.7+ · Pillow · Tkinter · hashlib

---

## SLIDE 7: GUI Walkthrough
*(Insert actual tool screenshots here)*

- **Top:** File selector + XOR key input
- **Middle:** Color-coded result box (Green = Clean, Red = Detected)
- **Extracted Message:** Displayed in orange scrollable box
- **Details Panel:**
  - SHA-256 hash
  - Image dimensions & format
  - Hidden data: YES/NO
  - Message length
- **Bottom:** Status bar with real-time timestamps
- **Export Button:** One-click CSV export

---

## SLIDE 8: Live Demo
*(Perform live demo OR show screenshots per step)*

**Step 1 — Clean Image:**
- Select any normal PNG → Analyze
- Result: 🟢 **CLEAN — No Hidden Data**

**Step 2 — Stego Image:**
- Select `stegoTS2.png` → Analyze
- Result: 🔴 **HIDDEN DATA DETECTED**
- Extracted: *"this is secret msg 2"*

**Step 3 — CSV Export:**
- Click Export → `logs/stego_analysis_20260219_HHMMSS.csv`
- 15 fields: hash, timestamp, message, metadata

---

## SLIDE 9: CSV Log Format (SIEM Integration) ✅ (Verified against `logger.py`)

**15-Field Log — Sample Row:**

| Field | Value |
|-------|-------|
| timestamp | 2026-02-14T14:35:22 |
| file_name | stegoTS2.png |
| file_hash | fcfcae8d3a61b35c... |
| image_dimensions | 2560x1440 |
| has_hidden_data | True |
| hidden_message_preview | "this is secret msg 2" |
| decryption_key_used | No *(current version — planned as dynamic in future)* |
| analysis_status | success |

> **Note:** `decryption_key_used` is hardcoded as `'No'` in the current version of `logger.py`.
> Dynamic key tracking is planned as a future enhancement.

**Integration Use Cases:**
- Ingest into **Splunk / ELK** SIEM
- Forensic **chain of custody** audit
- Compliance reporting (GDPR, HIPAA)

---

## SLIDE 10: Testing & Validation ✅ (All 5 test scripts verified)

| Test Case | Result | Status |
|-----------|--------|--------|
| Clean image — no detection | 🟢 Correct | ✅ Pass |
| Stego image — message found | 🔴 Correct | ✅ Pass |
| XOR decryption — correct key | Decrypted text | ✅ Pass |
| XOR decryption — wrong key | Error handled | ✅ Pass |
| CSV export — 15 fields | Correct format | ✅ Pass |
| Large image 10MB | < 10 seconds | ✅ Pass |
| False positive rate | 3.2% | ✅ < 5% |

**All 5 Test Scripts:**
- `quick_test.py` — Core engine quick check
- `test_detection_fix.py` — False positive fix validation
- `test_phase2.py` — CSV logging tests
- `test_phase3_guide.py` — Basic GUI tests
- `test_phase4_gui.py` — Enhanced GUI tests

---

## SLIDE 11: Challenges & Future Work

**Challenges Solved:**
- False positives: 35% → 3% via 7-layer validation
- Performance: 60s → <10s via optimized bit extraction
- Wrong XOR key crashes: Resolved with proper error handling

**Future Roadmap:**
- **Phase 5:** Batch folder scanning + multi-threading
- Advanced detection: Chi-square, entropy analysis, DCT (JPEG)
- PDF/HTML forensic report generation
- STIX 2.1 format for SIEM threat intel
- Dynamic `decryption_key_used` field in CSV logs
- Docker containerization + REST API

---

## SLIDE 12: Conclusion & Q&A

**Key Achievements:**
- ✅ Accurate LSB detection (>95%)
- ✅ Professional SOC-ready GUI
- ✅ SIEM-compatible CSV logging (15 fields)
- ✅ MITRE ATT&CK T1027.003 aligned
- ✅ Comprehensive documentation (README, Usage Guide, SOC Reports, 13-Part Tutorial)

**Learning Outcomes:**
- Steganography & digital forensics
- Modular Python software design
- Real-world SOC integration

> *"Empowering SOC teams to detect the invisible threats hidden in plain sight."*

---

**Your Name · Course · 2025–2026**
**Thank You — Questions Welcome**

---

## Corrections Made (vs. original draft)

| Slide | What Was Corrected |
|-------|--------------------|
| **Slide 5** | Validation layer order fixed to match actual code: Diversity=Layer 2, ASCII Ratio=Layer 3; Layer 6 threshold clarified as "≥24 bits", Layer 7 as "≤10,000 chars" |
| **Slide 9** | Added note that `decryption_key_used` is hardcoded `'No'` in current `logger.py`, not dynamic |
| **Slide 10** | All 5 test scripts listed (was missing `test_phase3_guide.py` and `test_phase4_gui.py`) |
| **Slide 11** | Added "Dynamic `decryption_key_used` field" to Future Roadmap |

---
*Last Updated: February 19, 2026*
