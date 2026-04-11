# VirusTotal Threat Intelligence Integration Plan

**Objective:** Equip the SOC Steganography Tool with active Threat Intelligence. By integrating the VirusTotal v3 REST API, we will allow analysts to instantly cross-reference underlying image files *and* the extracted hidden payloads against a global database of 90+ antivirus engines.

## Proposed Changes

### [NEW] `core/vt_client.py`
A brand new module dedicated to securely handling web requests to the VirusTotal API.
*   **Hash Checking:** Will take a SHA-256 hash, append it to `https://www.virustotal.com/api/v3/files/`, and parse the JSON response.
*   **Error Handling:** Built-in safeguards for timeouts, 404s (File not known to VT), and API rate limits.

### [MODIFY] `requirements.txt`
*   Add `requests>=2.31.0` to support remote HTTP queries.

### [MODIFY] `config.py`
*   Add a constant: `VT_API_KEY = ""` (So you can paste your free API key in).
*   Add endpoint routing constants.

### [MODIFY] `gui/main_window.py`
*   **The Button:** Adds a new action button `"Check Threat Intel (VT)"` beside the "Export to CSV" button in the Single Analysis view.
*   **Dual-Scan Logic:** 
    1. It grabs the image's SHA-256 hash and sends it to VT.
    2. **The "Wow" Factor:** If `has_hidden_data` is True, it hashes the *extracted text payload* and sends a second request to VT.
*   **The Dashboard Popup:** A stylish Tkinter `Toplevel` popup window that aggressively displays the VT scores (e.g., `0/94 Clean`, or `🔴 45/94 MALICIOUS`).

---

## User Review Required

> [!IMPORTANT]
> **API Key Sourcing**
> You will need a free VirusTotal API Key for this to work. You can get one instantly by making a free account on virustotal.com. I will hardcode a blank variable `VT_API_KEY = ""` in `config.py` for you to paste it into once we build it. Is that acceptable?

> [!TIP]
> **Visual Design**
> I plan to make the VT results pop up in a separate, dedicated "Threat Report" sub-window rather than permanently altering the main UI grid. This ensures the tool doesn't look cluttered when VT isn't used. Does a popup window sound good?

## Verification Plan
1. Add a valid API key to `config.py`.
2. Select a clean image and click "Check Threat Intel". Verify it queries VT and returns "Clean / Not Found".
3. Use an EICAR test string or malicious PowerShell snippet as the XOR decryption payload in a test image. Analyze it, hit the VT button, and verify the tool catches the malicious payload!
