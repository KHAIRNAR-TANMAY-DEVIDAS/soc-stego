# Chapter 6: The Record Keeper (Reporting & Audit Logs)

If you discover a deadly virus hidden inside a company logo, hitting "Analyze" on the GUI is not enough. In a real-world enterprise environment, Security Operations Centers (SOCs) are bound by strict legal and compliance rules. 

If a hacker breaches the network, the cybersecurity team must be able to prove exactly *when* the file was found, *what* the mathematical entropy score was at the time, and *what* the digital fingerprint (the SHA-256 hash) was. Without a permanent audit trail, forensic evidence is useless in a court of law.

This is why we built the **Record Keeper**: `reporting/logger.py`.

---

## 1. Clicking "Export to CSV": The Flow of Data

When an analyst clicks the **Export to CSV** button (in either the Single Analysis or Batch Analysis tabs), the tool initiates a highly structured export sequence.

1. **Grabbing the Data:** The GUI takes the same "Dictionary" package of answers that it normally paints onto the screen (Status, File Hash, Entropy Score, etc.) and hands it exclusively to `logger.py`.
2. **Formatting the Ledger:** `logger.py` acts like an accountant. It refuses to save messy data. It creates a standardized row with strict headers: `Timestamp | Image Path | Status | Entropy Score | EOF Found | File Hash`.
3. **The OS Write (Hard Drive Backup):** Using Python's built-in `csv` library, the logger securely writes this row of data into a permanent file inside the `logs/` directory. 
4. **Batch Mode Logging:** If the user ran a Batch Directory scan on 5,000 images, `logger.py` will loop through the giant list of 5,000 results and instantly compile them all into a massive, organized Excel-ready master document.

Because of this system, analysts can investigate 5,000 files in the morning, close the program, and still have a pristine, mathematical Excel report to hand to their boss in the afternoon.

---
---

# Chapter 7: The Executive Summary (The 60-Second Pitch)

*If an examiner asks you to explain the entire project from start to finish in exactly one minute, memorize this workflow:*

"Standard corporate firewalls and antiviruses evaluate digital images by checking their outer headers, which leaves them mathematically blind to **Steganography**—the act of deeply hiding malicious payloads inside the LSB (Least Significant Bit) color data of image pixels.

"To solve this critical SOC blindspot, our Python-based Forensic Tool performs a highly specialized, three-phase digital investigation:

1. **Extraction (The Brain):** We use a custom, bitwise math algorithm across a multi-threaded parallel engine to rip open the image pixels. We look for digital End-of-File signatures, but we also use **Shannon Entropy** advanced statistics. If the pixels are highly chaotic, mathematically guaranteeing an encrypted virus is present, we rip it out entirely.
2. **Validation (The API):** Once we extract the naked virus script, we run a Dual-Scan API pipeline directly to **VirusTotal**. We prove that while the Carrier Image sneaks past firewalls unseen, the extracted payload triggers Critical Malware alerts globally.
3. **Documentation (The Audit Trail):** Finally, we automatically synthesize all mathematical findings, SHA-256 evidence hashes, and threat states into compliance-ready CSV forensic logs.

"Simply put: While antiviruses blindly scan the outside of the suitcase, our software rips the suitcase open, captures the smuggler, and automatically files the police report."
