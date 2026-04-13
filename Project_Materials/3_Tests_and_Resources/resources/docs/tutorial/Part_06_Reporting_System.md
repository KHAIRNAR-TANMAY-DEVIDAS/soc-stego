# Part 6: Reporting System (CSV Logging & Report Generation)

## Introduction

In **Parts 4 and 5**, we learned how to **detect hidden data** and **display results in a GUI**. But what if you analyze 100 images? How do you track all your findings? How do you prove what you found for a report to your boss?

This is where the **Reporting System** comes in!

**Purpose:**
- **CSV Logging** - Save every analysis result to a spreadsheet file
- **Audit Trail** - Track what you analyzed, when, and what you found
- **Summary Reports** - Generate statistics and summaries from logs
- **Evidence** - Proof of your analysis for documentation

**Real-world use case:**
```
SOC Analyst workflow:
1. Analyze 50 suspicious images from email attachments
2. All results automatically logged to CSV file
3. Generate summary report at end of shift
4. Report shows: "Analyzed 50 images, found 3 with hidden data"
5. Share report with team lead
```

**What we'll cover:**
- `reporting/__init__.py` - Module organization
- `reporting/logger.py` - CSV logging functions
- `reporting/report_generator.py` - Report generation

Let's dive in!

---

## Part 1: Module Organization (reporting/__init__.py)

```python
"""Reporting and logging module for analysis results."""

from .logger import log_analysis_to_csv, log_batch_results, get_csv_files
from .report_generator import (
    generate_summary_report,
    format_report_text,
    export_report_to_file,
    compare_csv_logs
)

__all__ = [
    'log_analysis_to_csv',
    'log_batch_results',
    'get_csv_files',
    'generate_summary_report',
    'format_report_text',
    'export_report_to_file',
    'compare_csv_logs'
]
```

**Purpose:** Package initialization - makes functions easily importable

**Lines 3-4: Import from logger.py**
```python
from .logger import log_analysis_to_csv, log_batch_results, get_csv_files
```
- `.logger` - dot means "from this package"
- Import three functions from logger module

**Lines 5-10: Import from report_generator.py**
```python
from .report_generator import (
    generate_summary_report,
    format_report_text,
    export_report_to_file,
    compare_csv_logs
)
```
- Import four functions from report generator

**Lines 12-20: __all__ list**
- Defines what gets exported when someone does `from reporting import *`
- Lists all public functions

**Usage example:**
```python
# Instead of:
from reporting.logger import log_analysis_to_csv

# Can do:
from reporting import log_analysis_to_csv
```

---

## Part 2: CSV Logger (reporting/logger.py)

This file handles **saving analysis results to CSV files**.

**What is CSV?**
- **C**omma-**S**eparated **V**alues
- Simple spreadsheet format
- Opens in Excel, Google Sheets, etc.
- Each line is a row, commas separate columns

**Example CSV:**
```
timestamp,file_name,has_hidden_data,message_preview
2025-01-15T10:30:00,image1.png,True,"Secret message"
2025-01-15T10:31:00,image2.png,False,None
```

### Imports (Lines 6-9)

```python
import csv
import os
from datetime import datetime
from config import CSV_FIELDS, MESSAGE_PREVIEW_LENGTH, get_default_csv_path
```

**Line 6: csv module**
- Built-in Python module for reading/writing CSV files

**Line 7: os module**
- For file path operations

**Line 8: datetime**
- For timestamps

**Line 9: From config**
- `CSV_FIELDS` - list of column names
- `MESSAGE_PREVIEW_LENGTH` - how many characters to show
- `get_default_csv_path()` - where to save CSV

---

### Function 1: log_analysis_to_csv() (Lines 12-77)

**Purpose:** Save ONE analysis result to CSV file

```python
def log_analysis_to_csv(analysis_result, csv_path=None):
    """
    Logs analysis results to a CSV file for audit trail purposes.
    
    Args:
        analysis_result (dict): Output from analyze_image() function containing:
            - status: 'success' or 'error'
            - file_path: Path to analyzed file
            - file_hash: SHA-256 hash
            - file_size: Size in bytes
            - metadata: Image metadata dict
            - hidden_message: Extracted message or None
            - has_hidden_data: Boolean
            - timestamp: Analysis timestamp
            - error: Error message if status is 'error'
        
        csv_path (str, optional): Path to CSV file. If None, uses default path.
    
    Returns:
        dict: Result dictionary with keys:
            - success: Boolean indicating if logging succeeded
            - csv_path: Path where data was logged
            - error: Error message if success is False
    """
```

**Parameters:**
- `analysis_result` - the dictionary returned by `analyze_image()`
- `csv_path` - where to save (optional, uses default if None)

**Returns:**
- Dictionary telling you if it worked

---

**Lines 37-41: Initialize result dictionary**

```python
    result = {
        'success': False,
        'csv_path': csv_path,
        'error': None
    }
```

**Why start with success=False?**
- **Fail-safe approach** - assume failure until proven successful
- If something crashes, result is already set to failed

---

**Lines 43-46: Use default path if needed**

```python
    # Use default CSV path if none provided
    if csv_path is None:
        csv_path = get_default_csv_path()
        result['csv_path'] = csv_path
```

**Example:**
- No path provided → uses `logs/stego_analysis_20250115_103000.csv`

---

**Lines 48-55: Ensure directory exists**

```python
    # Ensure directory exists
    csv_dir = os.path.dirname(csv_path)
    if csv_dir and not os.path.exists(csv_dir):
        try:
            os.makedirs(csv_dir, exist_ok=True)
        except Exception as e:
            result['error'] = f"Failed to create directory: {str(e)}"
            return result
```

**Line 49: Get directory part**
```python
csv_dir = os.path.dirname(csv_path)
```
- Example: `logs/file.csv` → `logs`

**Line 50: Check if directory exists**
```python
if csv_dir and not os.path.exists(csv_dir):
```
- `csv_dir` - not empty string
- `not os.path.exists()` - directory doesn't exist

**Line 52: Create directory**
```python
os.makedirs(csv_dir, exist_ok=True)
```
- Creates directory (and parent directories if needed)
- `exist_ok=True` - don't error if already exists

**Lines 53-55: Handle errors**
- If we can't create directory, return error

---

**Lines 57-59: Check if CSV file exists**

```python
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.exists(csv_path)
```

**Why check this?**
- **First time** - write column headers
- **Already exists** - just append data

**Example:**
```
First run (empty file):
timestamp,file_name,has_hidden_data
2025-01-15T10:30:00,image1.png,True

Second run (already has header):
timestamp,file_name,has_hidden_data
2025-01-15T10:30:00,image1.png,True
2025-01-15T10:31:00,image2.png,False  ← Just add new row
```

---

**Lines 61-77: Write to CSV**

```python
    try:
        # Prepare row data from analysis result
        row_data = prepare_csv_row(analysis_result)
        
        # Open CSV file in append mode
        with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write the analysis data
            writer.writerow(row_data)
        
        result['success'] = True
        return result
        
    except PermissionError:
        result['error'] = f"Permission denied: Cannot write to {csv_path}"
        return result
    except Exception as e:
        result['error'] = f"Failed to log to CSV: {str(e)}"
        return result
```

**Line 63: Prepare data**
```python
row_data = prepare_csv_row(analysis_result)
```
- Calls helper function (we'll cover next)
- Converts analysis result to CSV format

**Line 66: Open file**
```python
with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
```
- `'a'` - **append mode** (add to end, don't overwrite)
- `newline=''` - required for CSV on Windows (prevents extra blank lines)
- `encoding='utf-8'` - support all characters

**Line 67: Create CSV writer**
```python
writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
```
- `DictWriter` - writes dictionaries as CSV rows
- `fieldnames=CSV_FIELDS` - column names from config

**Lines 70-71: Write header if new**
```python
if not file_exists:
    writer.writeheader()
```
- First time? Write column names

**Line 74: Write data**
```python
writer.writerow(row_data)
```
- Adds one row to CSV

**Line 76: Mark success**
```python
result['success'] = True
```

**Lines 79-84: Error handling**
- `PermissionError` - file is locked/read-only
- Generic `Exception` - anything else

---

### Function 2: prepare_csv_row() (Lines 80-135)

**Purpose:** Convert analysis result dictionary to CSV row format

```python
def prepare_csv_row(analysis_result):
    """
    Converts analysis result dictionary to CSV row format.
    
    Args:
        analysis_result (dict): Output from analyze_image()
    
    Returns:
        dict: Dictionary matching CSV_FIELDS structure
    """
```

**Why a separate function?**
- Keeps code organized
- Reusable (used by both single and batch logging)
- Easier to test

---

**Lines 92-94: Get metadata and message**

```python
    metadata = analysis_result.get('metadata', {})
    hidden_message = analysis_result.get('hidden_message', '')
```

**Using .get() with defaults:**
- If key doesn't exist, return default value (`{}` or `''`)
- Prevents crashes if key is missing

---

**Lines 96-106: Prepare message preview**

```python
    # Prepare message preview (truncate if too long)
    if hidden_message and hidden_message != "No hidden message detected":
        if len(hidden_message) > MESSAGE_PREVIEW_LENGTH:
            message_preview = hidden_message[:MESSAGE_PREVIEW_LENGTH] + "..."
        else:
            message_preview = hidden_message
        message_length = len(hidden_message)
    else:
        message_preview = hidden_message if hidden_message else "None"
        message_length = 0
```

**Line 98: Check if message exists**
```python
if hidden_message and hidden_message != "No hidden message detected":
```
- Has message AND not the "none found" message

**Line 99-100: Truncate if too long**
```python
if len(hidden_message) > MESSAGE_PREVIEW_LENGTH:
    message_preview = hidden_message[:MESSAGE_PREVIEW_LENGTH] + "..."
```
- Example: `MESSAGE_PREVIEW_LENGTH = 200`
- If message is 500 characters, only save first 200 + "..."

**Why truncate?**
- CSV files can get huge with long messages
- Preview is enough for summary
- Full message is in the image anyway

---

**Lines 108-110: Extract filename**

```python
    # Extract file name from path
    file_path = analysis_result.get('file_path', '')
    file_name = os.path.basename(file_path) if file_path else 'Unknown'
```

**os.path.basename():**
- Extracts filename from full path
- `C:\Users\SOC\images\photo.png` → `photo.png`

---

**Lines 112-131: Build CSV row dictionary**

```python
    # Build CSV row
    row = {
        'timestamp': analysis_result.get('timestamp', datetime.now().isoformat()),
        'file_path': file_path,
        'file_name': file_name,
        'file_hash': analysis_result.get('file_hash', 'N/A'),
        'file_size_bytes': analysis_result.get('file_size', 0),
        'image_format': metadata.get('format', 'N/A'),
        'image_dimensions': metadata.get('dimensions', 'N/A'),
        'image_mode': metadata.get('mode', 'N/A'),
        'max_capacity_bytes': metadata.get('max_capacity_bytes', 0),
        'has_hidden_data': analysis_result.get('has_hidden_data', False),
        'hidden_message_length': message_length,
        'hidden_message_preview': message_preview,
        'decryption_key_used': 'No',  # Will be enhanced in future phases
        'analysis_status': analysis_result.get('status', 'unknown'),
        'error_message': analysis_result.get('error', '')
    }
    
    return row
```

**Each key matches a CSV column!**

**Example row:**
```python
{
    'timestamp': '2025-01-15T10:30:00',
    'file_name': 'suspicious.png',
    'file_hash': 'a3f5c9d2...',
    'has_hidden_data': True,
    'hidden_message_preview': 'Secret meeting at...',
    'message_length': 150,
    ...
}
```

**Line 127: Note about future enhancement**
```python
'decryption_key_used': 'No',  # Will be enhanced in future phases
```
- Currently always 'No'
- In future, could track which key was used

---

### Function 3: log_batch_results() (Lines 138-213)

**Purpose:** Log MULTIPLE results at once (more efficient!)

```python
def log_batch_results(analysis_results, csv_path=None):
    """
    Logs multiple analysis results to CSV in a single operation.
    More efficient than calling log_analysis_to_csv() multiple times.
    
    Args:
        analysis_results (list): List of analysis result dictionaries
        csv_path (str, optional): Path to CSV file. If None, uses default.
    
    Returns:
        dict: Result dictionary with keys:
            - success: Boolean
            - csv_path: Path where data was logged
            - logged_count: Number of results logged
            - error: Error message if any
    """
```

**Why batch logging?**

**Slow way (multiple file opens):**
```python
for result in results:
    log_analysis_to_csv(result)  # Opens file 100 times!
```

**Fast way (one file open):**
```python
log_batch_results(results)  # Opens file ONCE!
```

**Performance:**
- 100 images analyzed → 100x faster with batch!

---

**Lines 154-160: Initialize result**

```python
    result = {
        'success': False,
        'csv_path': csv_path,
        'logged_count': 0,  # New: tracks how many logged
        'error': None
    }
    
    if not analysis_results:
        result['error'] = "No results to log"
        return result
```

**Line 161: Added logged_count**
- Tracks number of results successfully written

**Lines 164-166: Validate input**
- If list is empty, return error

---

**Lines 168-196: Write all results**

```python
    try:
        # Open CSV file in append mode
        with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write all results
            for analysis_result in analysis_results:
                row_data = prepare_csv_row(analysis_result)
                writer.writerow(row_data)
                result['logged_count'] += 1
        
        result['success'] = True
        return result
```

**Key difference: Loop INSIDE the file open!**

**Line 205-207: Loop through results**
```python
for analysis_result in analysis_results:
    row_data = prepare_csv_row(analysis_result)
    writer.writerow(row_data)
    result['logged_count'] += 1
```
- For each result, prepare and write
- Increment counter

**File is open the entire time → much faster!**

---

### Function 4: get_csv_files() (Lines 216-238)

**Purpose:** List all CSV files in logs directory

```python
def get_csv_files(logs_dir=None):
    """
    Lists all CSV log files in the logs directory.
    
    Args:
        logs_dir (str, optional): Directory to search. Uses config default if None.
    
    Returns:
        list: List of CSV file paths
    """
    if logs_dir is None:
        from config import LOGS_DIR
        logs_dir = LOGS_DIR
    
    if not os.path.exists(logs_dir):
        return []
    
    csv_files = []
    for filename in os.listdir(logs_dir):
        if filename.endswith('.csv'):
            csv_files.append(os.path.join(logs_dir, filename))
    
    return sorted(csv_files, reverse=True)  # Most recent first
```

**Line 227-229: Import and use default**
```python
if logs_dir is None:
    from config import LOGS_DIR
    logs_dir = LOGS_DIR
```

**Line 231-232: Check if directory exists**
```python
if not os.path.exists(logs_dir):
    return []
```
- If logs directory doesn't exist, return empty list

**Lines 234-237: Loop through files**
```python
csv_files = []
for filename in os.listdir(logs_dir):
    if filename.endswith('.csv'):
        csv_files.append(os.path.join(logs_dir, filename))
```
- `os.listdir()` - get all files in directory
- `.endswith('.csv')` - only CSV files
- `os.path.join()` - build full path

**Line 239: Sort by name (newest first)**
```python
return sorted(csv_files, reverse=True)
```
- Files are timestamped in name
- `reverse=True` - descending order (newest first)

**Example output:**
```python
[
    'logs/stego_analysis_20250115_143000.csv',  # Newest
    'logs/stego_analysis_20250115_100000.csv',
    'logs/stego_analysis_20250114_150000.csv'   # Oldest
]
```

---

## Part 3: Report Generator (reporting/report_generator.py)

This file generates **summary reports** from CSV log files.

**Use case:**
- You've analyzed 100 images over the week
- Boss asks: "How many had hidden data?"
- Instead of manually counting, generate a report!

### Imports (Lines 6-9)

```python
import csv
import os
from datetime import datetime
from collections import Counter
```

**Line 9: Counter**
- Special dictionary for counting things
- Example: `Counter(['PNG', 'PNG', 'JPG'])` → `{'PNG': 2, 'JPG': 1}`

---

### Function 1: generate_summary_report() (Lines 12-118)

**Purpose:** Generate statistics from a CSV log file

This is a BIG function! Let's break it down.

```python
def generate_summary_report(csv_path):
    """
    Generates a comprehensive summary report from a CSV log file.
    
    Args:
        csv_path (str): Path to the CSV log file
    
    Returns:
        dict: Summary statistics containing:
            - success: Boolean indicating if report generation succeeded
            - total_scans: Total number of images analyzed
            - suspicious_count: Images with hidden data detected
            - clean_count: Images with no hidden data
            - error_count: Failed analyses
            - format_breakdown: Count by image format
            - total_size_mb: Total size of analyzed files in MB
            - detection_rate: Percentage of images with hidden data
            - hidden_messages: List of detected messages (preview)
            - csv_path: Path to source CSV
            - report_timestamp: When report was generated
            - error: Error message if success is False
    """
```

**Returns a dictionary with lots of statistics!**

---

**Lines 35-48: Initialize report dictionary**

```python
    report = {
        'success': False,
        'total_scans': 0,
        'suspicious_count': 0,
        'clean_count': 0,
        'error_count': 0,
        'format_breakdown': {},
        'total_size_mb': 0.0,
        'detection_rate': 0.0,
        'hidden_messages': [],
        'csv_path': csv_path,
        'report_timestamp': datetime.now().isoformat(),
        'error': None
    }
```

**All statistics start at zero, will be calculated from CSV**

---

**Lines 50-53: Validate file exists**

```python
    # Validate file exists
    if not os.path.exists(csv_path):
        report['error'] = f"CSV file not found: {csv_path}"
        return report
```

---

**Lines 55-117: Process CSV file**

```python
    try:
        format_counter = Counter()
        total_size_bytes = 0
        
        # Read and process CSV file
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                report['total_scans'] += 1
```

**Line 56: Counter for image formats**
```python
format_counter = Counter()
```
- Will count PNG, JPG, etc.

**Line 60: Open CSV for reading**
```python
with open(csv_path, 'r', encoding='utf-8') as csvfile:
```
- `'r'` - read mode

**Line 61: Create CSV reader**
```python
reader = csv.DictReader(csvfile)
```
- `DictReader` - reads CSV as dictionaries
- Each row becomes a dictionary with column names as keys

**Line 63-64: Loop through rows**
```python
for row in reader:
    report['total_scans'] += 1
```
- For each row (image analyzed), increment counter

---

**Lines 66-82: Count detections**

```python
                # Count by detection status
                has_hidden_data = row.get('has_hidden_data', 'False')
                if has_hidden_data in ['True', 'true', '1', 'yes']:
                    report['suspicious_count'] += 1
                    
                    # Store message preview if available
                    message_preview = row.get('hidden_message_preview', '')
                    if message_preview and message_preview not in ['None', 'No hidden message detected', '']:
                        report['hidden_messages'].append({
                            'file_name': row.get('file_name', 'Unknown'),
                            'timestamp': row.get('timestamp', 'N/A'),
                            'message_preview': message_preview,
                            'message_length': int(row.get('hidden_message_length', 0))
                        })
                else:
                    report['clean_count'] += 1
```

**Line 68: Get detection status**
```python
has_hidden_data = row.get('has_hidden_data', 'False')
```
- CSV stores as string: `"True"` or `"False"`

**Line 69: Check if hidden data found**
```python
if has_hidden_data in ['True', 'true', '1', 'yes']:
```
- Multiple formats accepted (case variations)

**Lines 72-81: Store message details**
- If message was found, save details to list
- Skips generic "None" messages

**Line 83: Clean images**
```python
else:
    report['clean_count'] += 1
```

---

**Lines 84-88: Count errors**

```python
                # Count errors
                analysis_status = row.get('analysis_status', 'success')
                if analysis_status == 'error':
                    report['error_count'] += 1
```

---

**Lines 90-92: Count image formats**

```python
                # Format breakdown
                img_format = row.get('image_format', 'Unknown')
                format_counter[img_format] += 1
```

**Counter magic:**
```python
format_counter['PNG'] += 1  # First time: 0 → 1
format_counter['PNG'] += 1  # Second time: 1 → 2
format_counter['JPG'] += 1  # First time: 0 → 1
# Result: Counter({'PNG': 2, 'JPG': 1})
```

---

**Lines 94-99: Sum file sizes**

```python
                # Total size calculation
                try:
                    file_size = int(row.get('file_size_bytes', 0))
                    total_size_bytes += file_size
                except (ValueError, TypeError):
                    pass
```

**Why try/except here?**
- CSV stores numbers as strings: `"123456"`
- `int()` converts to number
- If conversion fails (corrupted data), skip it

---

**Lines 101-106: Calculate final statistics**

```python
        # Calculate derived statistics
        report['format_breakdown'] = dict(format_counter)
        report['total_size_mb'] = round(total_size_bytes / (1024 * 1024), 2)
        
        if report['total_scans'] > 0:
            report['detection_rate'] = round(
                (report['suspicious_count'] / report['total_scans']) * 100, 2
            )
```

**Line 102: Convert Counter to regular dict**
```python
report['format_breakdown'] = dict(format_counter)
```

**Line 103: Convert bytes to megabytes**
```python
report['total_size_mb'] = round(total_size_bytes / (1024 * 1024), 2)
```
- 1 MB = 1024 KB = 1024 * 1024 bytes
- `round(..., 2)` - round to 2 decimal places

**Lines 105-108: Calculate detection rate**
```python
if report['total_scans'] > 0:
    report['detection_rate'] = round(
        (report['suspicious_count'] / report['total_scans']) * 100, 2
    )
```

**Example:**
- 50 total scans
- 5 suspicious
- Detection rate = (5 / 50) * 100 = 10%

**Why check if total_scans > 0?**
- Avoid division by zero error!

---

### Function 2: format_report_text() (Lines 121-177)

**Purpose:** Convert report dictionary to human-readable text

```python
def format_report_text(report):
    """
    Formats a summary report dictionary into human-readable text.
    
    Args:
        report (dict): Output from generate_summary_report()
    
    Returns:
        str: Formatted report text
    """
```

---

**Lines 132-134: Check if report generation succeeded**

```python
    if not report.get('success'):
        return f"Report Generation Failed: {report.get('error', 'Unknown error')}"
```

---

**Lines 136-143: Build header**

```python
    lines = []
    lines.append("=" * 70)
    lines.append("SOC STEGANOGRAPHY DETECTION - ANALYSIS SUMMARY REPORT")
    lines.append("=" * 70)
    lines.append(f"Report Generated: {report['report_timestamp']}")
    lines.append(f"Source CSV: {report['csv_path']}")
    lines.append("")
```

**Line 136: Empty list to collect lines**
```python
lines = []
```

**Line 137: 70 equals signs**
```python
lines.append("=" * 70)
```
- `"=" * 70` → `"======...====== "` (70 characters)

**Visual result:**
```
======================================================================
SOC STEGANOGRAPHY DETECTION - ANALYSIS SUMMARY REPORT
======================================================================
Report Generated: 2025-01-15T14:30:00
Source CSV: logs/stego_analysis_20250115_100000.csv

```

---

**Lines 145-153: Scan statistics**

```python
    lines.append("SCAN STATISTICS")
    lines.append("-" * 70)
    lines.append(f"Total Images Scanned:      {report['total_scans']}")
    lines.append(f"Suspicious (Hidden Data):  {report['suspicious_count']} ({report['detection_rate']}%)")
    lines.append(f"Clean (No Hidden Data):    {report['clean_count']}")
    lines.append(f"Analysis Errors:           {report['error_count']}")
    lines.append(f"Total Data Analyzed:       {report['total_size_mb']} MB")
    lines.append("")
```

**Visual:**
```
SCAN STATISTICS
----------------------------------------------------------------------
Total Images Scanned:      50
Suspicious (Hidden Data):  3 (6.0%)
Clean (No Hidden Data):    47
Analysis Errors:           0
Total Data Analyzed:       15.43 MB

```

---

**Lines 155-162: Format breakdown**

```python
    # Format breakdown
    if report['format_breakdown']:
        lines.append("IMAGE FORMAT BREAKDOWN")
        lines.append("-" * 70)
        for img_format, count in sorted(report['format_breakdown'].items()):
            lines.append(f"  {img_format}: {count} images")
        lines.append("")
```

**Line 159: Loop through formats**
```python
for img_format, count in sorted(report['format_breakdown'].items()):
```
- `.items()` - get key-value pairs
- `sorted()` - alphabetical order

**Visual:**
```
IMAGE FORMAT BREAKDOWN
----------------------------------------------------------------------
  JPG: 15 images
  PNG: 35 images

```

---

**Lines 164-177: Hidden messages section**

```python
    # Hidden messages found
    if report['hidden_messages']:
        lines.append("HIDDEN MESSAGES DETECTED")
        lines.append("-" * 70)
        for idx, msg in enumerate(report['hidden_messages'], 1):
            lines.append(f"\n[{idx}] File: {msg['file_name']}")
            lines.append(f"    Timestamp: {msg['timestamp']}")
            lines.append(f"    Message Length: {msg['message_length']} characters")
            lines.append(f"    Preview: {msg['message_preview']}")
    else:
        lines.append("HIDDEN MESSAGES DETECTED")
        lines.append("-" * 70)
        lines.append("No hidden messages found in scanned images.")
```

**Line 169: enumerate with start=1**
```python
for idx, msg in enumerate(report['hidden_messages'], 1):
```
- Gives us index starting from 1 (not 0)
- `idx` = 1, 2, 3...

**Visual (with messages):**
```
HIDDEN MESSAGES DETECTED
----------------------------------------------------------------------

[1] File: suspicious1.png
    Timestamp: 2025-01-15T10:30:00
    Message Length: 150 characters
    Preview: Meet at the usual place at midnight...

[2] File: suspicious2.png
    Timestamp: 2025-01-15T11:45:00
    Message Length: 85 characters
    Preview: Transfer complete. Await further instructions...
```

**Visual (no messages):**
```
HIDDEN MESSAGES DETECTED
----------------------------------------------------------------------
No hidden messages found in scanned images.
```

---

**Lines 179-184: Footer**

```python
    lines.append("")
    lines.append("=" * 70)
    lines.append("END OF REPORT")
    lines.append("=" * 70)
    
    return "\n".join(lines)
```

**Line 184: Join all lines**
```python
return "\n".join(lines)
```
- Takes list of strings
- Joins with newlines between each
- Returns one big string

---

### Function 3: export_report_to_file() (Lines 187-219)

**Purpose:** Save formatted report to a text file

```python
def export_report_to_file(report, output_path):
    """
    Exports a formatted report to a text file.
    
    Args:
        report (dict): Output from generate_summary_report()
        output_path (str): Path where report should be saved
    
    Returns:
        dict: Result with success status and error message if any
    """
```

**Simple function - formats text and writes to file!**

---

**Lines 206-225: Export logic**

```python
    try:
        report_text = format_report_text(report)
        
        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        result['success'] = True
        return result
        
    except Exception as e:
        result['error'] = f"Failed to export report: {str(e)}"
        return result
```

**Line 207: Format report**
```python
report_text = format_report_text(report)
```

**Lines 209-212: Ensure directory exists**
- Same pattern as CSV logger

**Line 214: Write to file**
```python
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(report_text)
```
- `'w'` - write mode (creates new file or overwrites existing)

---

### Function 4: compare_csv_logs() (Lines 222-273)

**Purpose:** Compare statistics across MULTIPLE CSV files

**Use case:**
- Monday: analyzed 20 images, 2 suspicious
- Tuesday: analyzed 30 images, 5 suspicious
- Wednesday: analyzed 25 images, 1 suspicious
- Want to see: "Total this week: 75 scanned, 8 suspicious, 10.67% detection rate"

```python
def compare_csv_logs(csv_paths):
    """
    Compares statistics across multiple CSV log files.
    Useful for tracking detection trends over time.
    
    Args:
        csv_paths (list): List of CSV file paths to compare
    
    Returns:
        dict: Comparison data with statistics for each file
    """
```

---

**Lines 234-246: Initialize comparison dictionary**

```python
    comparison = {
        'success': False,
        'files_compared': len(csv_paths),
        'reports': [],
        'aggregate': {
            'total_scans': 0,
            'total_suspicious': 0,
            'total_clean': 0,
            'overall_detection_rate': 0.0
        },
        'error': None
    }
```

**New field: aggregate**
- Totals across all CSV files

---

**Lines 248-263: Process each CSV**

```python
    try:
        for csv_path in csv_paths:
            report = generate_summary_report(csv_path)
            if report['success']:
                comparison['reports'].append({
                    'file': os.path.basename(csv_path),
                    'total_scans': report['total_scans'],
                    'suspicious_count': report['suspicious_count'],
                    'detection_rate': report['detection_rate']
                })
                
                # Aggregate statistics
                comparison['aggregate']['total_scans'] += report['total_scans']
                comparison['aggregate']['total_suspicious'] += report['suspicious_count']
                comparison['aggregate']['total_clean'] += report['clean_count']
```

**Line 250: Generate report for each file**
```python
report = generate_summary_report(csv_path)
```

**Lines 259-263: Add to aggregate totals**
- Running sum across all files

---

**Lines 265-270: Calculate overall detection rate**

```python
        # Calculate overall detection rate
        if comparison['aggregate']['total_scans'] > 0:
            comparison['aggregate']['overall_detection_rate'] = round(
                (comparison['aggregate']['total_suspicious'] / comparison['aggregate']['total_scans']) * 100,
                2
            )
```

**Example result:**
```python
{
    'success': True,
    'files_compared': 3,
    'reports': [
        {'file': 'monday.csv', 'total_scans': 20, 'suspicious_count': 2, 'detection_rate': 10.0},
        {'file': 'tuesday.csv', 'total_scans': 30, 'suspicious_count': 5, 'detection_rate': 16.67},
        {'file': 'wednesday.csv', 'total_scans': 25, 'suspicious_count': 1, 'detection_rate': 4.0}
    ],
    'aggregate': {
        'total_scans': 75,
        'total_suspicious': 8,
        'total_clean': 67,
        'overall_detection_rate': 10.67
    }
}
```

---

## How It All Works Together

**Complete workflow:**

```
1. ANALYZE IMAGE
   ↓
   analyze_image() returns result dict
   ↓
2. LOG TO CSV
   ↓
   log_analysis_to_csv(result)
   ↓
   prepare_csv_row() formats data
   ↓
   Written to logs/stego_analysis_TIMESTAMP.csv
   ↓
3. ANALYZE MORE IMAGES (repeat steps 1-2)
   ↓
4. GENERATE REPORT
   ↓
   generate_summary_report('logs/stego_analysis_TIMESTAMP.csv')
   ↓
   Reads CSV, calculates statistics
   ↓
   format_report_text() creates readable text
   ↓
5. EXPORT REPORT
   ↓
   export_report_to_file(report, 'reports/summary.txt')
   ↓
   Beautiful report saved for your boss!
```

---

## Real-World Example

**Scenario:** SOC analyst investigates phishing campaign

```python
# Step 1: Analyze all suspicious images
results = []
for image_path in suspicious_images:
    result = analyze_image(image_path)
    results.append(result)

# Step 2: Batch log all results
log_batch_results(results, csv_path='logs/phishing_investigation_2025-01-15.csv')

# Step 3: Generate summary report
report = generate_summary_report('logs/phishing_investigation_2025-01-15.csv')

# Step 4: Export for documentation
export_report_to_file(report, 'reports/phishing_summary_2025-01-15.txt')

# Step 5: Share with team
print(f"Found {report['suspicious_count']} images with hidden data!")
print(f"Detection rate: {report['detection_rate']}%")
```

**Report output:**
```
======================================================================
SOC STEGANOGRAPHY DETECTION - ANALYSIS SUMMARY REPORT
======================================================================
Report Generated: 2025-01-15T14:30:00
Source CSV: logs/phishing_investigation_2025-01-15.csv

SCAN STATISTICS
----------------------------------------------------------------------
Total Images Scanned:      50
Suspicious (Hidden Data):  3 (6.0%)
Clean (No Hidden Data):    47
Analysis Errors:           0
Total Data Analyzed:       15.43 MB

IMAGE FORMAT BREAKDOWN
----------------------------------------------------------------------
  JPG: 35 images
  PNG: 15 images

HIDDEN MESSAGES DETECTED
----------------------------------------------------------------------

[1] File: attachment_1.png
    Timestamp: 2025-01-15T10:30:00
    Message Length: 150 characters
    Preview: C2 server address: 192.168.1.100:8080

[2] File: attachment_5.png
    Timestamp: 2025-01-15T11:45:00
    Message Length: 85 characters
    Preview: Credentials: admin / P@ssw0rd123

[3] File: attachment_12.png
    Timestamp: 2025-01-15T13:15:00
    Message Length: 200 characters
    Preview: Exfiltration complete. Mission success. Await further...

======================================================================
END OF REPORT
======================================================================
```

---

## Quick Review Questions

1. **Why use CSV for logging?**
   - Universal format, opens in Excel, permanent audit trail

2. **What's the advantage of log_batch_results() over log_analysis_to_csv()?**
   - Opens file once instead of multiple times = much faster

3. **What does Counter() do?**
   - Counts occurrences automatically (like a tally)

4. **Why truncate message preview in CSV?**
   - Keeps CSV file size manageable, full message is in image anyway

5. **What's the detection rate formula?**
   - (suspicious_count / total_scans) * 100

6. **Why check if total_scans > 0 before calculating detection rate?**
   - Avoid division by zero error

7. **What does compare_csv_logs() do?**
   - Combines statistics from multiple CSV files into aggregate totals

8. **Why use 'a' mode when logging to CSV?**
   - Append mode - adds to end without overwriting existing data

---

**Previous:** [Part 5C - GUI (Event Handlers & Results)](Part_05C_GUI_Event_Handlers.md)
**Next:** [Part 7 - Complete Integration & Workflow](Part_07_Complete_Integration.md)

---

*The reporting system is your audit trail! Every analysis is logged, statistics are calculated, and professional reports are generated. This is how SOC analysts track and document their findings! 🎯*
