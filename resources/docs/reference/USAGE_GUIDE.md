# SOC Steganography Detection Tool - Usage Guide

**For Security Operations Center (SOC) Analysts**

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Single Image Analysis Workflow](#single-image-analysis-workflow)
3. [Understanding Results](#understanding-results)
4. [CSV Export and Logging](#csv-export-and-logging)
5. [Working with Encrypted Messages](#working-with-encrypted-messages)
6. [Interpreting Detection Results](#interpreting-detection-results)
7. [Common Use Cases](#common-use-cases)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## 🚀 Getting Started

### System Requirements

- **Operating System:** Windows 10/11, Linux, macOS
- **Python:** Version 3.7 or higher
- **RAM:** Minimum 2GB (4GB recommended for large images)
- **Display:** 1024x768 or higher resolution

### Initial Setup

**Step 1: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 2: Verify Installation**
```bash
python main.py --verify
```

You should see:
```
✓ Core module loaded successfully
✓ GUI module loaded successfully
✓ Reporting module loaded successfully
✓ Configuration loaded successfully
✓ All folders exist
✓ Project structure verified
```

**Step 3: Launch Application**
```bash
python main.py
```

The GUI window should open with the welcome screen.

---

## 🔍 Single Image Analysis Workflow

### Standard Analysis Procedure

#### Step 1: Launch the Application

```bash
python main.py
```

**What you'll see:**
- 900x700 pixel window
- Welcome message with features and instructions
- "Select Image" button (enabled)
- "Analyze Image" button (disabled until image selected)
- "Export to CSV" button (disabled until analysis completes)

#### Step 2: Select Target Image

1. **Click** the "Select Image" button
2. **Navigate** to the image location in the file dialog
3. **Filter** by supported formats:
   - PNG files (*.png)
   - JPEG files (*.jpg, *.jpeg)
   - BMP files (*.bmp)
4. **Select** the image file
5. **Click** "Open"

**Result:**
- File path appears in the "Selected Image" field
- "Analyze Image" button becomes enabled
- Status bar shows: `[HH:MM:SS] Image selected: filename.png`

#### Step 3: Enter Decryption Key (Optional)

**If the hidden message is encrypted:**
1. **Locate** the "XOR Decryption Key (Optional)" field
2. **Enter** the decryption key (case-sensitive)
3. **Leave blank** if message is not encrypted or key unknown

**Note:** Wrong key will result in garbled output.

#### Step 4: Run Analysis

1. **Click** "Analyze Image" button
2. **Wait** for analysis to complete

**During Analysis:**
- Loading indicator appears: "⏳ Analyzing Image..."
- Progress bar animates (indeterminate mode)
- Status bar shows: `[HH:MM:SS] ⏳ Analyzing image... Please wait`
- "Analyze Image" button temporarily disabled

**Analysis Duration:**
- Small images (< 1MB): 1-3 seconds
- Medium images (1-5MB): 5-10 seconds
- Large images (> 5MB): 10-30 seconds

#### Step 5: Review Results

**Results are displayed in structured format:**

**A. Status Indicator (Top)**
- 🟢 **Green box:** "CLEAN - No Hidden Data"
- 🔴 **Red box:** "HIDDEN DATA DETECTED"
- ❌ **Error:** Analysis failed

**B. File Information Section (📁)**
- File Name
- Full File Path
- SHA-256 Hash (first 16 characters + "...")
- File Size (in bytes)
- Analysis Timestamp

**C. Image Metadata Section (🖼️)**
- Format (PNG/JPEG/BMP)
- Dimensions (width x height)
- Color Mode (RGB/RGBA/Grayscale)
- Total Pixels
- Max LSB Capacity (maximum hidden data storage)

**D. Detection Results Section (🔍)**
- Hidden Data: YES/NO
- Extracted Message (if found) in scrollable text box
- Clean confirmation (if no data found)

#### Step 6: Export Results (Optional)

1. **Click** "Export to CSV" button
2. **Confirmation dialog** appears with CSV file path
3. **Click** "OK" to acknowledge

**CSV Location:**
```
logs/stego_analysis_YYYYMMDD_HHMMSS.csv
```

**Status bar confirms:**
```
[HH:MM:SS] Exported to: logs/stego_analysis_20260214_143522.csv
```

#### Step 7: Clear or Analyze Next Image

**Option A: Clear Current Results**
- Click "Clear" button
- Results area resets to welcome message
- All fields cleared
- Ready for new analysis

**Option B: Select Another Image**
- Click "Select Image" again
- Previous results automatically cleared
- New image loaded for analysis

---

## 📊 Understanding Results

### Result Interpretation Guide

#### 🟢 CLEAN Image (No Hidden Data)

**Indicator Display:**
```
┌────────────────────────────────────┐
│ 🟢  CLEAN - No Hidden Data        │
│    (Green background)              │
└────────────────────────────────────┘
```

**What it means:**
- No LSB steganography detected
- EOF marker not found
- No hidden message present
- Image is safe for use

**SOC Action:**
- ✅ No further investigation needed
- Log result for audit trail
- Continue with normal operations

**Example Files:**
- Regular photos
- Screenshots
- Stock images
- Clean test images

---

#### 🔴 HIDDEN DATA DETECTED

**Indicator Display:**
```
┌────────────────────────────────────┐
│ 🔴  HIDDEN DATA DETECTED           │
│       (Red background)             │
└────────────────────────────────────┘
```

**What it means:**
- LSB steganography detected
- EOF marker found at specific bit position
- Hidden message successfully extracted
- Validation checks passed (7/7 criteria)

**SOC Action:**
- ⚠️ **ALERT:** Potential data exfiltration or covert communication
- **Escalate** to Tier 2 analyst or incident response team
- **Document** extracted message content
- **Correlate** with other security events (SIEM)
- **Investigate** file source and recipient
- **Apply** MITRE ATT&CK framework (T1027.003)

**Example Files:**
- `test_images/stegoTS2.png` - Contains: "this is secret msg 2"
- `test_images/setgoTS3.png` - Contains: "This is secret msg 3"

---

#### ❌ ERROR - Analysis Failed

**Indicator Display:**
```
┌────────────────────────────────────┐
│ ❌  ERROR - Analysis Failed        │
│       (Red background)             │
└────────────────────────────────────┘
```

**Common Causes:**
1. **Corrupted image file**
2. **Unsupported format**
3. **File permission issues**
4. **Insufficient memory**
5. **File locked by another process**

**SOC Action:**
- Check file integrity (hash verification)
- Try different image format converter
- Verify file permissions
- Review error message in results panel
- Check system resources

---

### Detection Confidence Levels

The tool uses 7 validation layers to ensure accuracy:

| Validation Layer | Pass Criteria | Purpose |
|-----------------|---------------|---------|
| **1. Min Length** | ≥ 3 characters | Filter random noise |
| **2. Character Diversity** | ≥ 2 unique chars | Detect repeated patterns |
| **3. ASCII Printable Ratio** | ≥ 70% | Ensure text coherence |
| **4. Letter Presence** | Must contain letters | Validate language content |
| **5. Extended ASCII Limit** | < 30% extended ASCII | Filter binary garbage |
| **6. EOF Position** | Valid marker placement | Verify structural integrity |
| **7. Length Validation** | Reasonable message size | Prevent overflow |

**Confidence Assessment:**
- **7/7 checks passed:** HIGH confidence (>95%)
- **5-6 checks passed:** MEDIUM confidence (70-95%)
- **< 5 checks passed:** LOW confidence - likely false positive

**Current Implementation:** Tool only reports detections that pass all 7 checks.

---

## 📝 CSV Export and Logging

### CSV Log Structure

**File Naming Convention:**
```
stego_analysis_YYYYMMDD_HHMMSS.csv
```

**Example:**
```
stego_analysis_20260214_143522.csv
```

### CSV Field Reference

| Field # | Field Name | Description | Example Value |
|---------|-----------|-------------|---------------|
| 1 | `timestamp` | Analysis date/time | 2026-02-14T14:35:22.458391 |
| 2 | `file_path` | Full file path | D:\images\test.png |
| 3 | `file_name` | File name only | test.png |
| 4 | `file_hash` | SHA-256 hash | fcfcae8d3a61b35ca608ab6... |
| 5 | `file_size_bytes` | Size in bytes | 2255550 |
| 6 | `image_format` | Format type | PNG |
| 7 | `image_dimensions` | Width x Height | 2560x1440 |
| 8 | `image_mode` | Color mode | RGBA |
| 9 | `max_capacity_bytes` | LSB capacity | 1382400 |
| 10 | `has_hidden_data` | Detection bool | True |
| 11 | `hidden_message_length` | Chars in message | 125 |
| 12 | `hidden_message_preview` | First 100 chars | "This is classified..." |
| 13 | `decryption_key_used` | Key status | Yes/No |
| 14 | `analysis_status` | Result status | success |
| 15 | `error_message` | Error details | (empty if success) |

### Using CSV Logs

**View in Excel/Spreadsheet:**
```bash
# Open CSV in Excel
start excel logs\stego_analysis_20260214_143522.csv
```

**Filter Detections:**
```python
import pandas as pd

df = pd.read_csv('logs/stego_analysis_20260214_143522.csv')
detections = df[df['has_hidden_data'] == True]
print(f"Found {len(detections)} suspicious images")
```

**SIEM Integration:**
- Import CSV into Splunk, ELK, or QRadar
- Create alerts for `has_hidden_data == True`
- Correlate with file transfer logs
- Build dashboard for steganography metrics

---

## 🔐 Working with Encrypted Messages

### XOR Encryption/Decryption

#### What is XOR Encryption?

**XOR (Exclusive OR)** is a symmetric cipher:
- Same key used for encryption and decryption
- Bitwise operation: `ciphertext = plaintext XOR key`
- Simple but effective for basic obfuscation

#### Analyzing Encrypted Messages

**Scenario:** Image contains encrypted hidden message.

**Step-by-Step:**

1. **Analyze Without Key First:**
   - Select image
   - Leave XOR key field blank
   - Click "Analyze Image"
   - **Result:** Garbled/illegible text with random characters

2. **Obtain Decryption Key:**
   - From threat intelligence
   - From related artifacts
   - Through cryptanalysis (beyond tool scope)

3. **Re-Analyze with Key:**
   - Enter key in "XOR Decryption Key" field
   - Click "Analyze Image" again
   - **Result:** Decrypted plaintext message

**Example:**

**Encrypted output (no key):**
```
7fh3j@#$kl2_:>?mn...
```

**Decrypted output (correct key):**
```
This is the secret data being exfiltrated.
Contact: threat@actor.com
```

#### Key Handling Security

**⚠️ IMPORTANT:**
- Keys may themselves be sensitive intelligence
- Document key source in incident report
- Store keys securely (not in CSV logs)
- Follow organization's key management policy

---

## 🎯 Interpreting Detection Results

### Threat Assessment Matrix

| Detection Scenario | Threat Level | SOC Action |
|-------------------|--------------|------------|
| Clean corporate document | 🟢 Low | Log and continue |
| Image from untrusted source, clean | 🟡 Medium | Additional context analysis |
| Hidden message: encrypted | 🔴 High | Incident escalation |
| Hidden message: cleartext | 🔴 High | Immediate investigation |
| Hidden message with C2 indicators | 🔴🔴 Critical | P1 incident, IR team |

### Message Content Analysis

**When hidden data is detected, analyze content for:**

1. **Exfiltration Indicators:**
   - File paths: `"C:\Users\Admin\Documents\financial_data.xlsx"`
   - Credentials: `"admin:password123"`
   - Sensitive data: PII, credit cards, SSNs

2. **C2 Communication:**
   - IP addresses: `"192.168.1.100"`
   - Domains: `"c2.malicious-domain.com"`
   - Commands: `"execute ransomware.exe"`

3. **Coordination Information:**
   - Meeting times: `"2026-02-15 at 10:00 PM"`
   - Email contacts: `"user@external-domain.com"`
   - Code words: `"Operation Phoenix initiated"`

4. **Metadata Correlation:**
   - Check file creation timestamp
   - Compare with user login times
   - Cross-reference with email attachments
   - Check file transfer logs

### MITRE ATT&CK Mapping

**Primary Techniques:**
- **T1027.003** - Obfuscated Files: Steganography
- **T1020** - Automated Exfiltration
- **T1564.010** - Hide Artifacts: LSB Steganography
- **T1071.001** - Application Layer Protocol

**Tactic:** Exfiltration + Defense Evasion

---

## 💼 Common Use Cases

### Use Case 1: Email Attachment Analysis

**Scenario:** Suspicious image received via email attachment.

**Workflow:**
1. Save attachment to quarantine folder
2. Run virus/malware scan first
3. Analyze with stego detection tool
4. If hidden data found → Escalate to IR
5. Log results with email metadata correlation

**Command:**
```bash
python main.py
# Select email attachment image
# Analyze
# Document in incident ticket
```

---

### Use Case 2: Network Traffic Analysis

**Scenario:** Image file transferred via HTTP/SMTP, flagged by DLP.

**Workflow:**
1. Extract image from PCAP/email
2. Calculate file hash for evidence chain
3. Run stego analysis
4. Compare with known good versions
5. Export CSV for SIEM ingestion

---

### Use Case 3: Insider Threat Investigation

**Scenario:** Employee suspected of data exfiltration.

**Workflow:**
1. Obtain legal authorization
2. Collect user's sent images (email, cloud storage)
3. Batch analyze all images (Phase 5 feature)
4. Document chain of custody
5. Generate forensic report
6. Coordinate with HR/Legal

---

### Use Case 4: Malware Analysis

**Scenario:** Malware sample uses steganography for C2.

**Workflow:**
1. Isolate in sandbox environment
2. Extract images accessed by malware
3. Analyze for C2 communications
4. Decrypt if XOR key discovered in binary
5. IOC extraction for threat intel

---

### Use Case 5: Threat Hunting

**Scenario:** Proactive search for covert channels.

**Workflow:**
1. Define hunt hypothesis: "Steganography used for exfiltration"
2. Identify image sources (proxies, email gateways)
3. Sample analysis (random selection)
4. Statistical baseline establishment
5. Anomaly detection for suspicious patterns

---

## 🛠️ Troubleshooting

### Issue: GUI Won't Launch

**Symptoms:**
- Window doesn't appear
- Python errors in terminal

**Solutions:**
1. **Check Python version:**
   ```bash
   python --version
   # Should be 3.7+
   ```

2. **Verify Tkinter installation:**
   ```bash
   python -m tkinter
   # Should open test window
   ```

3. **Check dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run in verbose mode:**
   ```bash
   python main.py --cli
   ```

---

### Issue: "Analysis Failed" Error

**Symptoms:**
- Red error indicator
- Error message in results panel

**Common Causes & Fixes:**

**1. Corrupted Image File**
```bash
# Verify file integrity
python -c "from PIL import Image; img = Image.open('test.png'); print('OK')"
```

**2. Unsupported Format**
- Convert to PNG/JPEG/BMP
- Use image converter tool

**3. File Too Large**
- Image > 20MB may cause memory issues
- Resize image before analysis
- Close other applications

**4. Permission Denied**
- Run as administrator (Windows)
- Check file permissions (Linux/Mac)

---

### Issue: Long Analysis Time

**Symptoms:**
- Analysis takes > 60 seconds
- GUI appears frozen

**Explanations:**
- Large images (> 5MB) require more processing
- High resolution (4K+) increases bit extraction time
- First run may cache PIL libraries

**Solutions:**
- Be patient - tool is single-threaded
- Check status bar for progress
- Consider resizing images for batch analysis

---

### Issue: False Positive Detection

**Symptoms:**
- Tool reports hidden data on known clean image
- Extracted "message" is gibberish

**Explanation:**
- Random image data can accidentally match EOF pattern
- Very rare due to 7-layer validation

**Solutions:**
- Re-analyze to confirm
- Check validation criteria in code
- Report as feedback for algorithm improvement

---

### Issue: CSV Export Fails

**Symptoms:**
- "Export Failed" dialog
- No CSV file created

**Solutions:**
1. **Check logs folder exists:**
   ```bash
   mkdir logs
   ```

2. **Verify write permissions:**
   ```bash
   # Test write access
   echo "test" > logs/test.txt
   ```

3. **Check disk space:**
   ```bash
   df -h  # Linux/Mac
   # Windows: Check drive properties
   ```

---

## ✅ Best Practices

### For SOC Analysts

**1. Evidence Handling**
- ✅ Always calculate file hash BEFORE analysis
- ✅ Maintain chain of custody documentation
- ✅ Work on copies, not originals
- ✅ Use isolated/air-gapped system for highly sensitive images

**2. Documentation**
- ✅ Export every analysis to CSV
- ✅ Screenshot detection results
- ✅ Note context (source, timestamp, related events)
- ✅ Include in incident timeline

**3. Validation**
- ✅ Verify suspicious detections manually
- ✅ Cross-reference with threat intelligence
- ✅ Check file metadata (EXIF data)
- ✅ Analyze file provenance

**4. Escalation Criteria**
- 🔴 **Immediate:** Hidden message with PII, credentials, C2 info
- 🟠 **High Priority:** Encrypted message from untrusted source
- 🟡 **Medium Priority:** Suspicious patterns requiring investigation
- 🟢 **Low Priority:** Clean images from known sources

**5. Operational Security**
- ⚠️ Analyzing malicious images may be risky
- 💡 Use VM or sandbox for untrusted files
- 🔒 Keep decryption keys secure
- 📝 Follow incident response procedures

### For Forensic Investigators

**1. Chain of Custody**
- Document original file hash
- Note acquisition method and time
- Record all analysis actions
- Preserve original evidence

**2. Court Admissibility**
- Use write-blockers for original media
- Generate detailed reports
- Maintain audit logs (CSV)
- Follow forensic standards (NIST SP 800-86)

**3. Tool Validation**
- Test with known samples first
- Verify accuracy on control images
- Document tool version used
- Include methodology in reports

---

## 📞 Getting Help

### Resources

- **README:** Project overview and installation
- **Sample Report:** `docs/SAMPLE_ANALYSIS_REPORT_V1.md`
- **Test Scripts:** `test_phase*.py` for validation

### Reporting Issues

1. Document exact steps to reproduce
2. Include error messages
3. Note Python version and OS
4. Provide sample image (if non-sensitive)

---

## 📚 Additional Reading

### Steganography Concepts
- LSB Steganography Techniques
- Steganalysis Methods
- Digital Watermarking vs Steganography

### SOC Operations
- MITRE ATT&CK Framework
- NIST Incident Response Guide (SP 800-61)
- Digital Forensics Procedures

### Related Tools
- Stegdetect (Linux)
- OpenStego
- Steghide
- StegSpy

---

**Document Version:** 1.0  
**Last Updated:** February 14, 2026  
**For Tool Version:** 1.0.0

---

**End of Usage Guide**
