# VirusTotal Threat Intelligence Integration Plan (The Showstopper)

**Objective:** Equip the SOC Steganography Tool with active Threat Intelligence. By integrating the VirusTotal v3 REST API, we will allow analysts to instantly cross-reference underlying carrier images *and* the extracted hidden payloads against a global database of 94+ antivirus engines.

## Proposed Changes

### 1. Requirements & Config (`requirements.txt`, `config.py`)
*   **Dependencies:** Add `requests>=2.31.0` to support remote HTTP queries.
*   **Config Keys:** Add `VT_API_KEY = ""` inside `config.py` for API key input.
*   **Endpoints:** Add constant routing variables in config for `https://www.virustotal.com/api/v3/files/`.

### 2. New Core Module (`core/vt_client.py`)
*   Build a dedicated REST API integration client module.
*   **Dual-Scan Logic:** Handles concurrent/sequential requests. If the image `has_hidden_data`, the module will generate a SHA-256 hash of the *extracted text payload* alongside the image hash.
*   **Error Handling:** Include robust `try/except` safeguards tracking JSON parsing, 404s (File not known to VT), and 429 API rate limits.

### 3. GUI Threat Intelligence (`gui/main_window.py`)
*   **The Button:** Adds a new action button `"Check Threat Intel (VT)"` directly beside the "Export to CSV" button in the Single Analysis view.
*   **Threading Engine:** Network requests will trigger an insulated background thread so the core Tkinter application does not dynamically freeze while waiting for web responses.
*   **The Dashboard Popup:** Rather than permanently altering the main UI grid, VT results will spawn in a stylish `Tkinter Toplevel` popup window. This overlay will aggressively display the scores (e.g., `0/94 Clean` or `🔴 45/94 MALICIOUS`), maintaining the core app's clean appearance.

## User Review Required

> [!CAUTION]
> **API Key Sourcing**
> I am going to populate `config.py` with the empty constant `VT_API_KEY = ""`. After I build the code, you MUST generate a free API key on virustotal.com and paste it in for the buttons to actually connect to the global web!

> [!TIP]
> **Testing Strategy (Weaponized Scripting)**
> To demonstrate the power of your dual-scan logic, use the industry-standard **EICAR Test String**. Hide it in an image using a basic stego scripter. Your VirusTotal popup will successfully expose the malicious payload while completely bypassing traditional antivirus!

## Approval
Give me the command **"approved"** to begin editing `requirements.txt`, `config.py`, generating `vt_client.py`, and connecting the GUI popups!
