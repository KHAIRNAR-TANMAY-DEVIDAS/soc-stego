# SOC Steganography Detection & Analysis Studio 🛡️🔍

![Version](https://img.shields.io/badge/version-v0.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-emerald.svg)
![Security](https://img.shields.io/badge/Purpose-Educational%20%2F%20Demonstration-orange.svg)

A dual-capability cybersecurity forensic utility and covert payload studio designed to simulate both **offensive data concealment** and **defensive digital forensics (Steganalysis)** within a modern Security Operations Center (SOC) environment.

---

## 🎯 Motivation & Origin

This project was born out of a desire to bridge the gap between **theoretical cybersecurity principles and practical implementation**. While studying core security fundamentals and preparing for the **(ISC)² Certified in Cybersecurity (CC)** certification, I wanted to go beyond textbooks and build a hands-on utility from scratch.

Modern threat actors routinely leverage covert channels (steganography) to evade firewalls, conceal command-and-control (C2) payloads, and silently exfiltrate sensitive data. This tool demonstrates:
* **How data hiding and encryption work mechanically at the binary level** (Red Team simulation).
* **How SOC analysts and forensic investigators detect statistical anomalies, filter noise, and extract evidence** (Blue Team defense).
* **How global threat intelligence (VirusTotal) cross-references extracted artifacts.**

> **Note:** This project was developed for **educational, learning, and demonstration purposes**.

---

## ✨ Features at a Glance

### 1. 🔏 Steganography Studio (Red Team / Encoding & Decoding)
* **LSB Image Injection:** Embeds payloads seamlessly into the Least Significant Bits of pixel color channels with zero visual degradation.
* **Military-Grade Encryption:** Optional AES encryption via Fernet with PBKDF2HMAC (SHA-256, 390,000 iteration key derivation).
* **Live Capacity Meter:** Interactive progress gauge that measures payload size against image capacity in real-time, preventing overflow.
* **Lossless Preservation:** Automatic output validation ensuring stego images are saved in lossless formats (PNG/BMP).
* **Fast-Path Extraction:** Dedicated decoder tab to rapidly extract and decrypt payloads from known stego targets with one-click clipboard copying.

### 2. 🔬 Stego Analyzer (Blue Team / Forensics & Anomaly Hunting)
* **Fast-Path Header Extraction:** Recognizes structured V2 headers (`b'SOC'` signature) and safely extracts payloads.
* **Sliding-Window EOF Detection:** 16-bit sliding window register scanning for legacy bitstream termination patterns (`1111111111111110`).
* **7-Layer Heuristic Anti-Garbage Filter:** Evaluates extracted byte streams (printable ASCII ratios, character diversity, letter presence, length thresholds) to eliminate false positives caused by natural image noise.
* **Shannon Entropy Gauge:** Mathematical randomness scoring ($0.0 - 8.0$ scale). Automatically flags high-entropy LSB distributions ($\ge 7.99$) as anomalous/encrypted payloads.
* **Batch Directory Audit:** Multithreaded parallel engine capable of auditing hundreds of images across directories simultaneously.

### 3. 🌐 Global Threat Intelligence Integration (VirusTotal v3)
* **Cryptographic Fingerprinting:** Generates SHA-256 hashes of both carrier images and raw extracted payloads.
* **Safe Cloud Lookup:** Queries the VirusTotal v3 REST API without uploading sensitive payload text, protecting privacy.
* **Secure Local Key Management:** Supports untracked local API key files (`vt_api_key.txt`) or environment variables, preventing secret leaks to version control.

### 4. 📊 Audit Trails & Forensic Reporting
* **Automated CSV Logging:** Records timestamp, file hash, resolution, entropy score, detection status, and payload length for every scan.
* **Formatted TXT Reports:** Generates human-readable digital forensics summary reports for single scans and batch audits.

---

## 🖥️ User Interface Overview

The interface is built with **CustomTkinter** featuring a dark Cyber-SOC palette:

* **Tab 1: Steganography (Hide / Extract)**
  * *Encode Payload:* Dynamic carrier thumbnail, live capacity meter, passphrase protection, and output chooser.
  * *Decode Payload:* Stego image ingestion, passphrase authentication, and extracted message viewer.
* **Tab 2: Stego Analyzer**
  * *Single Target Scan:* Real-time thumbnail preview, threat verdict banners (Clean, Suspicious, Critical Threat), LSB entropy gauge, payload preview, and one-click VirusTotal scanning.
  * *Batch Directory Audit:* Directory selection, parallel progress dashboard, threat count metrics, and export tools.

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.8+** installed on your system.
* **Git** installed (for cloning).

### 1. Clone the Repository
```bash
git clone https://github.com/KHAIRNAR-TANMAY-DEVIDAS/soc-stego.git
cd soc-stego
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Application
```bash
# Launch the graphical dashboard (default)
python main.py

# Or verify system module integrity
python main.py --verify
```

---

## 🧪 Quickstart Testing & Demonstration

Follow these quick steps to test both offensive data hiding and defensive detection:

### Step 1: Hide a Payload (Red Team Simulation)
1. Open the **Steganography (Hide / Extract)** tab.
2. Click **Select Carrier Image** and pick any PNG or JPG image.
3. In the **Secret Payload Message** box, type any test message (e.g., `CONFIDENTIAL_SOC_INCIDENT_REPORT_2026`).
   * *(Optional)* Set a **Passphrase** to encrypt the payload with AES-Fernet.
4. Click **Encode & Save Stego Image** to save the output file (e.g., `stego_sample.png`).

### Step 2: Analyze & Hunt for Threats (Blue Team / SOC Forensics)
1. Switch to the **Stego Analyzer** tab.
2. Select your newly created `stego_sample.png`.
3. If encrypted, optionally enter the **Decryption Passphrase**.
4. Click **Scan Target**:
   * Observe the **Detection Verdict** banner update to `POSITIVL (Threat Found)`.
   * Check the **LSB Shannon Entropy score** and gauge.
   * Review the extracted payload in the viewer or copy it to the clipboard.
5. *(Optional)* Click **VirusTotal Threat Scan** to check the cryptographic hash against global threat intelligence.

---

### 🛡️ Testing with the Standard EICAR Antivirus Test String

In security operations and threat simulations, analysts often test endpoint detection and response (EDR) rules using standard, benign test signatures rather than real malware.

* To simulate malware concealment, you can copy the official standard **EICAR Anti-Malware Test String** from [eicar.org](https://www.eicar.org/download-anti-malware-testfile/) into the secret message box:
  ```
  https://www.eicar.org/download-anti-malware-testfile/
  ```
* **Why EICAR?** The EICAR test string is completely harmless, but globally recognized by antivirus scanners. Hiding it inside an image demonstrates how threat actors use steganography to evade perimeter security filters and transport signatures undetected.

---

## 🔑 Configuring Your VirusTotal API Key (Optional)

To enable the **VirusTotal Threat Scan** feature without committing your personal API credentials to Git:

1. Obtain a free API key from [VirusTotal](https://www.virustotal.com/gui/join-us).
2. Choose **one** of the following secure options:
   * **Option A (Recommended):** Create a file named `vt_api_key.txt` in the root folder and paste your key inside. *(This file is automatically ignored by `.gitignore`)*.
   * **Option B:** Set an environment variable:
     ```bash
     # Windows (Command Prompt)
     set VT_API_KEY=your_api_key_here

     # Windows (PowerShell)
     $env:VT_API_KEY="your_api_key_here"

     # Linux / macOS
     export VT_API_KEY="your_api_key_here"
     ```
   * **Option C:** Paste it directly into `config.py` under `VT_API_KEY` for local testing.

---

## 🛡️ The 7-Layer Heuristic Filter Explained

Because random noise in standard images can coincidentally match a 16-bit EOF pattern ($1 \text{ in } 65,536$ probability), the Stego Analyzer passes all candidate bitstreams through 7 strict verification layers:

| Layer | Verification Check | Purpose |
|:---|:---|:---|
| **1. Minimum Length** | $\ge 3$ characters | Rejects accidental early EOF matches. |
| **2. Character Diversity** | Unique characters $\ge 2$ | Rejects solid blocks of padding bytes (e.g. `0x00` or `0xFF`). |
| **3. ASCII Printable Ratio** | Printable characters $\ge 70\%$ | Ensures content resembles natural text, code, or structured data. |
| **4. Alphabetic Presence** | Contains at least 1 letter (`a-z`) | Discards purely numeric or random symbol noise. |
| **5. Extended ASCII Limit** | High-bit characters $\le 30\%$ | Filters out non-ASCII binary garbage. |
| **6. Position Validation** | EOF offset $\ge 24$ bits | Prevents validating sub-character truncated fragments. |
| **7. Length Sanity Cap** | Length $\le 10,000$ characters | Protects against memory exhaustion from unconstrained scans. |

---

## 📁 Project Directory Layout

```
soc-stego/
│
├── main.py                  # Application entry point & CLI verification
├── config.py                # Configuration constants, thresholds, and theme styling
├── requirements.txt         # Core dependencies (Pillow, customtkinter, cryptography, requests)
├── .gitignore               # Excludes secrets, caches, and local logs
│
├── core/                    # Backend processing engines
│   ├── image_stego_engine.py # Steganalysis, entropy analysis, & 7-layer validation
│   ├── stego_tool_engine.py  # LSB encoding, decoding, & AES-Fernet encryption
│   └── vt_client.py          # VirusTotal v3 REST API integration
│
├── gui/                     # Frontend graphical interface
│   ├── main_window.py       # CustomTkinter dashboard implementation
│   └── file_dialog.py       # File and directory selection helpers
│
├── reporting/               # Forensic report generators
│   ├── logger.py            # CSV audit logging
│   └── report_generator.py  # Structured text report generation
│
├── assets/                  # Graphical icons and theme resources
└── logs1/                   # Default local output folder for reports & logs
```

---

## ⚖️ Educational & Demonstration Disclaimer

This software is developed strictly for **educational, academic, and demonstration purposes**. It was created to demonstrate cybersecurity principles, data hiding risks, and forensic detection strategies. Users are responsible for ensuring compliance with applicable laws and organization policies when using this software.
