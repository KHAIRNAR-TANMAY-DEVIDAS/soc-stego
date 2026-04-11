# Part 3: Configuration (config.py)

## Understanding the Configuration File

Now let's explore `config.py` - the **control center** for all settings in our tool. This file contains no complex logic, just definitions of values used throughout the application.

**Analogy:** Think of `config.py` like the settings menu in a video game - it contains all the adjustable options, colors, thresholds, and constants.

---

## Why Have a Separate Config File?

**Benefits:**
1. **Centralized** - All settings in one place
2. **Easy to find** - Don't hunt through code for magic numbers
3. **Safe to edit** - Change behavior without risking bugs
4. **Professional** - Industry best practice

**Example problem without config:**
```python
# In file1.py
if confidence > 0.75:  # What is 0.75?

# In file2.py  
if confidence > 0.73:  # Wait, why 0.73 here?

# In file3.py
if confidence > 0.8:   # Now it's 0.8?? Which is right?
```

**Solution with config:**
```python
# config.py
DETECTION_THRESHOLD = 0.75

# All other files
if confidence > config.DETECTION_THRESHOLD:  # Clear and consistent!
```

---

## Line-by-Line Explanation

### Section 1: File Header (Lines 1-3)

```python
"""
Configuration module for SOC Steganography Detection Tool.
Contains application constants, paths, and settings.
"""
```

**What is this?**
- Module-level docstring
- Explains what this file contains
- First thing someone sees when opening the file

---

### Section 2: Import Statements (Lines 5-6)

#### Line 5: Import os

```python
import os
```

**Why?**
- Used for file path operations
- Will use `os.path.join()` to build cross-platform paths
- Will use `os.makedirs()` to create directories

---

#### Line 6: Import datetime

```python
from datetime import datetime
```

**What is datetime?**
- Built-in Python module for working with dates and times
- `from datetime import datetime` - import the class, not the whole module
- Used to generate timestamps for log files

**Example usage:**
```python
datetime.now()  # Current date and time
```

---

### Section 3: Application Information (Lines 8-11)

```python
# Application Information
APP_NAME = "SOC Steganography Detection Tool"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Image Steganography Detection and Analysis Tool for SOC Operations"
```

**What are these?**
- **Constants** - values that don't change during execution
- Python convention: ALL_CAPS for constants

**Line 9: APP_NAME**
- The official name of the application
- Used in window titles, headers, about dialogs

**Line 10: APP_VERSION**
- Version number following semantic versioning
- Format: `MAJOR.MINOR.PATCH`
  - `1` = Major version (big changes)
  - `0` = Minor version (new features)
  - `0` = Patch version (bug fixes)

**Line 11: APP_DESCRIPTION**
- One-sentence description of what the tool does
- Used in help messages and documentation

**Where used:**
```python
# In main.py
print(f"Launching {APP_NAME} v{APP_VERSION}...")
# Output: Launching SOC Steganography Detection Tool v1.0.0...
```

---

### Section 4: GUI Configuration (Lines 13-17)

```python
# GUI Configuration
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
```

**What are these?**
- Window dimensions in pixels
- Control the GUI window size

**Line 14: WINDOW_WIDTH**
- Default width when window first opens
- 900 pixels wide

**Line 15: WINDOW_HEIGHT**
- Default height when window first opens
- 700 pixels tall

**Line 16-17: Minimum dimensions**
- Prevents users from making window too small
- Ensures UI elements remain readable
- 800x600 is the minimum comfortable size

**Why configurable?**
- Easy to adjust if UI elements don't fit
- Can optimize for different screen resolutions
- No need to dig through GUI code to change

**Visual:**
```
┌─────────────────────────────────────┐
│  Window: 900px wide                 │  ← WINDOW_WIDTH
│                                     │
│                                     │
│  700px tall ← WINDOW_HEIGHT         │
│                                     │
│                                     │
│                                     │
└─────────────────────────────────────┘
```

---

### Section 5: Color Scheme (Lines 19-27)

```python
# Color Scheme (Professional SOC Theme)
COLOR_PRIMARY = "#2C3E50"        # Dark blue-gray
COLOR_SECONDARY = "#34495E"      # Lighter blue-gray
COLOR_SUCCESS = "#27AE60"        # Green (clean/safe)
COLOR_WARNING = "#F39C12"        # Orange (suspicious)
COLOR_DANGER = "#E74C3C"         # Red (hidden data detected)
COLOR_INFO = "#3498DB"           # Blue (information)
COLOR_BACKGROUND = "#ECF0F1"     # Light gray background
COLOR_TEXT = "#2C3E50"           # Dark text
```

**What are hex colors?**
- Format: `#RRGGBB` (Red, Green, Blue)
- Each pair is a value from 00 to FF (0 to 255)
- Example: `#FF0000` = pure red

**Why these specific colors?**
- **Professional look** - Dark blues suggest security/technical
- **Semantic meaning** - Colors have meanings:
  - 🟢 Green = Safe, clean, success
  - 🟠 Orange = Warning, suspicious
  - 🔴 Red = Danger, alert, detection
  - 🔵 Blue = Information, neutral

**Line 20: COLOR_PRIMARY**
- `#2C3E50` - Dark blue-gray
- Main UI color (buttons, headers)

**Line 21: COLOR_SECONDARY**
- `#34495E` - Slightly lighter blue-gray
- Secondary elements (panels, borders)

**Line 22: COLOR_SUCCESS**
- `#27AE60` - Green
- Shows when image is clean (no hidden data)

**Line 23: COLOR_WARNING**
- `#F39C12` - Orange
- Shows when something is suspicious but not confirmed

**Line 24: COLOR_DANGER**
- `#E74C3C` - Red
- Shows when hidden data is detected

**Line 25: COLOR_INFO**
- `#3498DB` - Blue
- Informational messages

**Line 26: COLOR_BACKGROUND**
- `#ECF0F1` - Light gray
- Main window background

**Line 27: COLOR_TEXT**
- `#2C3E50` - Dark blue-gray (same as primary)
- Text color for readability

**Why centralize colors?**
- Easy to change theme (edit once, affects entire GUI)
- Consistent look throughout application
- Can create dark mode by changing these values

**Example usage:**
```python
# In GUI code
result_label.config(fg=config.COLOR_SUCCESS)  # Green text
```

---

### Section 6: File Paths (Lines 29-33)

```python
# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
TESTS_DIR = os.path.join(BASE_DIR, "tests")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
```

**Line 30: BASE_DIR**
```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
```

Let's break this down (inside to outside):

**Step 1: `__file__`**
- Special variable = path to current file (config.py)
- Example: `"d:\TEST PROJECT\config.py"`

**Step 2: `os.path.abspath(__file__)`**
- Make sure path is absolute (full path)
- Example: `"d:\TEST PROJECT\config.py"`

**Step 3: `os.path.dirname(...)`**
- Get directory part (remove filename)
- Example: `"d:\TEST PROJECT"`

**Result:** `BASE_DIR` = the project root directory

---

**Line 31-33: Subdirectory Paths**

```python
LOGS_DIR = os.path.join(BASE_DIR, "logs")
TESTS_DIR = os.path.join(BASE_DIR, "tests")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
```

**What is `os.path.join()`?**
- Combines path parts with the correct separator
- Windows uses `\`, Linux/Mac use `/`
- `os.path.join()` uses the right one automatically

**Examples:**
```python
# BASE_DIR = "d:\TEST PROJECT"
LOGS_DIR = os.path.join(BASE_DIR, "logs")
# Result: "d:\TEST PROJECT\logs"

TESTS_DIR = os.path.join(BASE_DIR, "tests")
# Result: "d:\TEST PROJECT\tests"
```

**Why not just use strings?**
```python
# Bad - won't work on Linux
LOGS_DIR = BASE_DIR + "\logs"

# Good - works everywhere
LOGS_DIR = os.path.join(BASE_DIR, "logs")
```

---

### Section 7: Create Logs Directory (Line 35-36)

```python
# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)
```

**Line 36: os.makedirs()**
```python
os.makedirs(LOGS_DIR, exist_ok=True)
```

**What does this do?**
- Creates the logs directory if it doesn't exist
- `exist_ok=True` means "don't error if it already exists"

**Why do this?**
- Prevents errors when trying to write log files
- First run might not have a logs folder
- Better to create it automatically than crash

**Without this:**
```python
# Try to write log file
with open("logs/analysis.csv", "w") as f:  # ERROR: Directory doesn't exist!
```

**With this:**
```python
os.makedirs(LOGS_DIR, exist_ok=True)
with open("logs/analysis.csv", "w") as f:  # Success! Directory was created
```

---

### Section 8: CSV Logging Configuration (Lines 38-40)

```python
# CSV Logging Configuration
CSV_FILENAME_PREFIX = "stego_analysis"
CSV_DATETIME_FORMAT = "%Y%m%d_%H%M%S"
```

**Line 39: CSV_FILENAME_PREFIX**
- The start of every CSV log filename
- Example: `"stego_analysis"`

**Line 40: CSV_DATETIME_FORMAT**
- Format for timestamps in filenames
- `%Y` = 4-digit year (2026)
- `%m` = 2-digit month (02)
- `%d` = 2-digit day (14)
- `%H` = 2-digit hour (09)
- `%M` = 2-digit minute (30)
- `%S` = 2-digit second (45)

**Example:**
- Date/time: February 14, 2026, 9:30:45 AM
- Format: `"%Y%m%d_%H%M%S"`
- Result: `"20260214_093045"`

**Full filename example:**
```
stego_analysis_20260214_093045.csv
     ↑             ↑        ↑
   prefix      date      time
```

**Why timestamp filenames?**
- Each analysis session gets its own file
- No overwriting previous logs
- Easy to see when analysis was run

---

### Section 9: CSV Path Generator Function (Lines 42-46)

```python
def get_default_csv_path():
    """Generate default CSV log file path with timestamp."""
    timestamp = datetime.now().strftime(CSV_DATETIME_FORMAT)
    filename = f"{CSV_FILENAME_PREFIX}_{timestamp}.csv"
    return os.path.join(LOGS_DIR, filename)
```

**This is the first function in config.py!**

**Line 42: Function definition**
```python
def get_default_csv_path():
```
- Function named `get_default_csv_path`
- No parameters needed
- Will return a file path (string)

**Line 43: Docstring**
- Explains what the function does

**Line 44: Get timestamp**
```python
timestamp = datetime.now().strftime(CSV_DATETIME_FORMAT)
```

**Breaking it down:**
- `datetime.now()` - gets current date/time
- `.strftime()` - formats it as a string
- `CSV_DATETIME_FORMAT` - the format we defined earlier
- Result stored in `timestamp` variable

**Example:**
- Current time: Feb 14, 2026, 9:30:45 AM
- `timestamp` = `"20260214_093045"`

**Line 45: Build filename**
```python
filename = f"{CSV_FILENAME_PREFIX}_{timestamp}.csv"
```
- f-string combines prefix, underscore, timestamp, and .csv extension
- Example: `"stego_analysis_20260214_093045.csv"`

**Line 46: Return full path**
```python
return os.path.join(LOGS_DIR, filename)
```
- Combines logs directory with filename
- Returns the full path
- Example: `"d:\TEST PROJECT\logs\stego_analysis_20260214_093045.csv"`

**How this function is used:**
```python
# In other code
csv_path = config.get_default_csv_path()
# csv_path = "d:\TEST PROJECT\logs\stego_analysis_20260214_093045.csv"
```

**Why a function instead of a constant?**
- Timestamp must be generated fresh each time
- Can't do that with a simple variable definition

---

### Section 10: CSV Field Definitions (Lines 48-64)

```python
# CSV Field Definitions
CSV_FIELDS = [
    'timestamp',
    'file_path',
    'file_name',
    'file_hash',
    'file_size_bytes',
    'image_format',
    'image_dimensions',
    'image_mode',
    'max_capacity_bytes',
    'has_hidden_data',
    'hidden_message_length',
    'hidden_message_preview',
    'decryption_key_used',
    'analysis_status',
    'error_message'
]
```

**What is this?**
- A list of column names for the CSV log file
- Each analysis will record these 15 fields

**Why define this?**
- Ensures all logs have the same structure
- Easy to add/remove fields
- Clear documentation of what gets logged

**Field-by-field explanation:**

| Field Name | What It Stores | Example |
|------------|----------------|---------|
| `timestamp` | When analysis ran | `"2026-02-14 09:30:45"` |
| `file_path` | Full path to image | `"d:\images\photo.png"` |
| `file_name` | Just the filename | `"photo.png"` |
| `file_hash` | SHA-256 hash | `"a3b2c1d4..."` |
| `file_size_bytes` | Size in bytes | `204800` |
| `image_format` | File format | `"PNG"` |
| `image_dimensions` | Width x Height | `"800x600"` |
| `image_mode` | Color mode | `"RGB"` |
| `max_capacity_bytes` | How much can hide | `60000` |
| `has_hidden_data` | Detection result | `True` or `False` |
| `hidden_message_length` | Length of found data | `1024` |
| `hidden_message_preview` | First 100 chars | `"Secret message..."` |
| `decryption_key_used` | XOR key if used | `"mykey123"` |
| `analysis_status` | Success or error | `"Completed"` |
| `error_message` | Error details if any | `""` or error text |

**Example CSV output:**
```csv
timestamp,file_path,file_name,file_hash,file_size_bytes,...
2026-02-14 09:30:45,d:\images\cat.png,cat.png,a3b2c1...,204800,...
2026-02-14 09:31:12,d:\images\dog.jpg,dog.jpg,f7e8d9...,156000,...
```

---

### Section 11: Supported Image Formats (Lines 66-75)

```python
# Image File Filters
SUPPORTED_IMAGE_FORMATS = [
    ("PNG files", "*.png"),
    ("JPEG files", "*.jpg *.jpeg"),
    ("BMP files", "*.bmp"),
    ("All supported images", "*.png *.jpg *.jpeg *.bmp"),
    ("All files", "*.*")
]

IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp']
```

**Line 67-73: SUPPORTED_IMAGE_FORMATS**

**What is this?**
- A list of tuples (pairs)
- Used by file dialogs to filter file types
- Each tuple: `(description, pattern)`

**Structure:**
```python
("PNG files", "*.png")
   ↑             ↑
description   pattern (what to show)
```

**Breaking down each entry:**

**Line 68:** PNG files
```python
("PNG files", "*.png")
```
- Shows only .png files
- `*` = any filename
- `.png` = extension

**Line 69:** JPEG files
```python
("JPEG files", "*.jpg *.jpeg")
```
- Shows .jpg OR .jpeg files
- Space separates multiple patterns

**Line 70:** BMP files
```python
("BMP files", "*.bmp")
```
- Shows only .bmp files

**Line 71:** All supported
```python
("All supported images", "*.png *.jpg *.jpeg *.bmp")
```
- Shows all image types we support
- Usually the default selection

**Line 72:** All files
```python
("All files", "*.*")
```
- Shows everything
- Fallback option

**How this looks in file dialog:**
```
┌─────────────────────────────────┐
│ File type:                      │
│ ┌─────────────────────────────┐ │
│ │ PNG files (*.png)           │ │
│ │ JPEG files (*.jpg, *.jpeg)  │ │
│ │ BMP files (*.bmp)           │ │
│ │ All supported images        │◄─ Selected
│ │ All files (*.*)             │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

---

**Line 75: IMAGE_EXTENSIONS**
```python
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp']
```

**What is this?**
- Simple list of supported extensions
- Used for validation in code

**Example usage:**
```python
# Check if file is supported
if file_extension in config.IMAGE_EXTENSIONS:
    # Process the image
else:
    # Show error: unsupported format
```

**Why two different formats?**
- `SUPPORTED_IMAGE_FORMATS` - for GUI file dialogs (needs descriptions)
- `IMAGE_EXTENSIONS` - for code validation (simple list)

---

### Section 12: Analysis Configuration (Lines 77-79)

```python
# Analysis Configuration
MESSAGE_PREVIEW_LENGTH = 100  # Characters to show in preview
HASH_DISPLAY_LENGTH = 16      # Characters of hash to display in GUI
```

**Line 78: MESSAGE_PREVIEW_LENGTH**
```python
MESSAGE_PREVIEW_LENGTH = 100
```

**What is this?**
- How many characters to show in found messages
- Full message might be thousands of characters
- Preview shows first 100

**Why limit?**
- GUI would get cluttered with huge messages
- CSV file would become unwieldy
- 100 chars is enough to see what it is

**Example:**
```python
# Full message: "This is a very long secret message that goes on and on..."
# Preview (first 100 chars): "This is a very long secret message that goes on and on..."
```

---

**Line 79: HASH_DISPLAY_LENGTH**
```python
HASH_DISPLAY_LENGTH = 16
```

**What is this?**
- How many characters of file hash to show in GUI
- Full SHA-256 hash is 64 characters
- Showing first 16 is usually enough for identification

**Example:**
```python
# Full hash:    "a3b2c1d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"
# Display:      "a3b2c1d4e5f6g7h8..."
```

**Why not show full hash?**
- Takes up too much screen space
- 16 chars still uniquely identifies files
- Full hash is in CSV log anyway

---

### Section 13: Detection Thresholds (Lines 81-83)

```python
# Detection Thresholds (for future enhancements)
ENTROPY_THRESHOLD = 7.5       # Statistical entropy threshold
LSB_ANOMALY_THRESHOLD = 0.05  # LSB distribution anomaly threshold
```

**What are thresholds?**
- Cutoff values for detection decisions
- Above threshold = suspicious
- Below threshold = normal

**Line 82: ENTROPY_THRESHOLD**
```python
ENTROPY_THRESHOLD = 7.5
```

**What is entropy?**
- Measure of randomness in data
- Scale: 0 (predictable) to 8 (completely random)
- Hidden data often has high entropy

**Examples:**
- Text file: entropy ≈ 4.5 (somewhat predictable)
- Compressed file: entropy ≈ 7.8 (very random)
- Encrypted data: entropy ≈ 7.99 (almost perfectly random)

**The threshold:**
- If entropy > 7.5, might be hidden data
- Could also be natural image variation

**Analogy:** Like a metal detector sensitivity - higher = more sensitive but more false alarms.

---

**Line 83: LSB_ANOMALY_THRESHOLD**
```python
LSB_ANOMALY_THRESHOLD = 0.05
```

**What is this?**
- Checks if least significant bits look unusual
- Normal images: LSBs are fairly random
- Steganography: LSBs might show patterns

**The value 0.05:**
- If deviation > 5%, flag as anomalous
- Balances detection and false positives

**Note:** "(for future enhancements)"
- These thresholds are defined but might not be fully implemented yet
- Placeholder for advanced detection features

---

### Section 14: Batch Processing Configuration (Lines 85-87)

```python
# Batch Processing Configuration
BATCH_MAX_WORKERS = 4         # For parallel processing (future enhancement)
BATCH_TIMEOUT_SECONDS = 30    # Per-image analysis timeout
```

**Line 86: BATCH_MAX_WORKERS**
```python
BATCH_MAX_WORKERS = 4
```

**What is this?**
- For processing multiple images simultaneously
- 4 = maximum number of parallel workers

**Why 4?**
- Most modern CPUs have 4+ cores
- Can analyze 4 images at once
- Balance between speed and resource usage

**How it would work:**
```
Sequential (slow):
Image1 → Image2 → Image3 → Image4
[==]    [==]     [==]     [==]     Total: 40 seconds

Parallel (fast):
Image1 → [==]
Image2 → [==]  } All at once
Image3 → [==]    Total: 10 seconds
Image4 → [==]
```

---

**Line 87: BATCH_TIMEOUT_SECONDS**
```python
BATCH_TIMEOUT_SECONDS = 30
```

**What is this?**
- Maximum time to spend analyzing one image
- If analysis takes longer than 30 seconds, stop it

**Why timeout?**
- Prevents program from hanging on corrupted files
- Very large images might take too long
- 30 seconds is generous but not infinite

**Example:**
```python
# Start analyzing huge_image.png
# After 30 seconds, still not done
# → Stop, mark as timeout, move to next image
```

---

### Section 15: Error Messages (Lines 89-93)

```python
# Error Messages
ERROR_FILE_NOT_FOUND = "Image file not found"
ERROR_INVALID_IMAGE = "Invalid or corrupted image file"
ERROR_ANALYSIS_FAILED = "Analysis failed due to unexpected error"
ERROR_DECRYPTION_FAILED = "Decryption failed - possible wrong key"
```

**Why define error messages here?**
- Consistent wording across the application
- Easy to update messages
- Could translate to other languages
- Single source of truth

**Each message explained:**

**Line 90:** File not found
- User selected a file that no longer exists
- Maybe it was moved or deleted

**Line 91:** Invalid image
- File is corrupted
- Not actually an image despite extension
- Can't be opened by image library

**Line 92:** Analysis failed
- Unexpected error during analysis
- Generic fallback message

**Line 93:** Decryption failed
- User provided a XOR key
- Key didn't work (wrong key)

**Usage example:**
```python
# In analysis code
if not os.path.exists(file_path):
    return config.ERROR_FILE_NOT_FOUND
```

**Benefits:**
- Typo in error message? Fix once in config
- Want to improve wording? Change once
- Need translations? Replace strings in config

---

### Section 16: Success Messages (Lines 95-98)

```python
# Success Messages
SUCCESS_ANALYSIS_COMPLETE = "Analysis completed successfully"
SUCCESS_LOGGED_TO_CSV = "Results logged to CSV successfully"
SUCCESS_BATCH_COMPLETE = "Batch analysis completed"
```

**Same principle as error messages**

**Line 96:** Analysis complete
- Single image analyzed successfully

**Line 97:** Logged to CSV
- Results written to log file

**Line 98:** Batch complete
- Multiple image analysis finished

---

### Section 17: GUI Labels (Lines 100-106)

```python
# GUI Labels
LABEL_SELECT_IMAGE = "Select Image"
LABEL_ANALYZE = "Analyze"
LABEL_EXPORT_CSV = "Export to CSV"
LABEL_CLEAR = "Clear"
LABEL_XOR_KEY = "XOR Decryption Key (Optional):"
LABEL_STATUS = "Ready"
```

**What are these?**
- Text shown on buttons and labels in the GUI
- Centralizing makes internationalization easier

**Each label:**

| Constant | Text on GUI | Purpose |
|----------|-------------|---------|
| `LABEL_SELECT_IMAGE` | "Select Image" | Button to open file dialog |
| `LABEL_ANALYZE` | "Analyze" | Button to start analysis |
| `LABEL_EXPORT_CSV` | "Export to CSV" | Button to export results |
| `LABEL_CLEAR` | "Clear" | Button to clear results |
| `LABEL_XOR_KEY` | "XOR Decryption Key:" | Label for key input |
| `LABEL_STATUS` | "Ready" | Default status message |

**Why define these?**
- Want to change "Analyze" to "Scan"? Edit once
- Want Spanish version? Replace all labels
- Consistent terminology throughout app

---

### Section 18: About Information (Lines 108-127)

```python
# About Information
ABOUT_TEXT = f"""
{APP_NAME}
Version {APP_VERSION}

{APP_DESCRIPTION}

Final Year Cybersecurity Project
Focus: Image LSB Steganography Detection

Features:
• LSB extraction and analysis
• XOR decryption support
• SHA-256 file hashing
• Metadata extraction
• CSV logging for audit trails
• Batch processing capability

© 2026 - For educational purposes
"""
```

**What is this?**
- Multi-line string with information about the tool
- Shown in "About" dialog when user clicks Help → About

**Line 109-110: Triple quotes**
```python
ABOUT_TEXT = f"""
...
"""
```
- Triple quotes allow multi-line strings
- `f"""` makes it an f-string (can insert variables)

**Line 111-112: Header**
```python
{APP_NAME}
Version {APP_VERSION}
```
- Inserts the app name and version we defined earlier
- Automatically updates if you change those constants

**Line 114:** Description
- Inserts the app description

**Lines 116-117:** Project context
- Identifies this as a final year project
- Explains the focus area

**Lines 119-124:** Feature list
- `•` is a bullet point character
- Lists key capabilities
- Marketing/informational

**Line 126:** Copyright/disclaimer
- Year and educational purpose notice

**Example rendered text:**
```
SOC Steganography Detection Tool
Version 1.0.0

Image Steganography Detection and Analysis Tool for SOC Operations

Final Year Cybersecurity Project
Focus: Image LSB Steganography Detection

Features:
• LSB extraction and analysis
• XOR decryption support
• SHA-256 file hashing
• Metadata extraction
• CSV logging for audit trails
• Batch processing capability

© 2026 - For educational purposes
```

---

## Configuration Categories Summary

Let's organize what we learned:

### 1. Application Identity
- Name, version, description
- About text

### 2. Visual Settings
- Window dimensions
- Color scheme
- Display lengths

### 3. File System
- Directory paths
- Log file naming
- Supported formats

### 4. Data Structure
- CSV field definitions
- Format specifications

### 5. Behavior Control
- Thresholds
- Timeouts
- Limits

### 6. User Interface Text
- Button labels
- Status messages
- Error messages

---

## How Other Files Use Config

**Example 1: GUI uses colors**
```python
# In gui/main_window.py
import config

result_label.config(
    text="Hidden data detected!",
    fg=config.COLOR_DANGER  # Red text
)
```

**Example 2: Logging uses fields**
```python
# In reporting/logger.py
import config
import csv

with open(csv_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=config.CSV_FIELDS)
    writer.writeheader()
```

**Example 3: Main uses app info**
```python
# In main.py
from config import APP_NAME, APP_VERSION

print(f"Launching {APP_NAME} v{APP_VERSION}...")
```

**Example 4: Analysis uses thresholds**
```python
# In core/image_stego_engine.py
import config

if entropy > config.ENTROPY_THRESHOLD:
    flag_as_suspicious()
```

---

## Benefits of This Approach

### 1. Maintainability
- One place to update settings
- No hunting through code for magic numbers
- Clear documentation of what each value means

### 2. Consistency
- Same colors everywhere
- Same messages everywhere
- Same behavior everywhere

### 3. Flexibility
- Easy to tune without breaking code
- Can create multiple config files for different environments
- Can override settings for testing

### 4. Clarity
- Comments explain what each constant is for
- Descriptive names make purpose obvious
- Organized into logical sections

### 5. Internationalization Ready
- All user-facing text in one place
- Could create config_spanish.py, config_french.py
- Swap configs for different languages

---

## Common Patterns in Config Files

### Constants (ALL_CAPS)
```python
MAX_SIZE = 1000
DEFAULT_TIMEOUT = 30
```

### Functions (when value needs computation)
```python
def get_default_csv_path():
    return os.path.join(LOGS_DIR, f"log_{datetime.now()}.csv")
```

### Organized Sections (comments as headers)
```python
# ============ GUI Settings ============
WINDOW_WIDTH = 800

# ============ Analysis Settings ============
THRESHOLD = 0.75
```

### Using Other Constants
```python
BASE_DIR = "/project"
LOGS_DIR = os.path.join(BASE_DIR, "logs")  # Uses BASE_DIR
```

---

## Testing Config Values

You can check what's in config:

```python
# In Python terminal
>>> import config
>>> config.APP_NAME
'SOC Steganography Detection Tool'

>>> config.COLOR_SUCCESS
'#27AE60'

>>> config.CSV_FIELDS
['timestamp', 'file_path', 'file_name', ...]

>>> config.get_default_csv_path()
'd:\\TEST PROJECT\\logs\\stego_analysis_20260214_093045.csv'
```

---

## Customizing the Tool

Want to change behavior? Edit config.py:

**Make window bigger:**
```python
WINDOW_WIDTH = 1200  # Changed from 900
WINDOW_HEIGHT = 900  # Changed from 700
```

**Change color theme:**
```python
COLOR_SUCCESS = "#00FF00"  # Brighter green
COLOR_DANGER = "#FF0000"   # Brighter red
```

**Show more of message preview:**
```python
MESSAGE_PREVIEW_LENGTH = 200  # Changed from 100
```

**More sensitive detection:**
```python
ENTROPY_THRESHOLD = 7.0  # Changed from 7.5 (lower = more sensitive)
```

**More parallel workers:**
```python
BATCH_MAX_WORKERS = 8  # Changed from 4
```

---

## Review Questions

Before moving on, make sure you understand:

1. **Why centralize configuration?** (Consistency, maintainability, clarity)

2. **What's the difference between `COLOR_SUCCESS` and `COLOR_DANGER`?** (Green for clean, red for detected)

3. **Why use `os.path.join()` instead of string concatenation?** (Cross-platform compatibility)

4. **What does `get_default_csv_path()` return?** (Full path to timestamped CSV file)

5. **How many fields are logged in the CSV?** (15 fields)

6. **What image formats are supported?** (PNG, JPG, JPEG, BMP)

7. **What happens if analysis takes longer than `BATCH_TIMEOUT_SECONDS`?** (Analysis stops)

8. **Why use constants like `ERROR_FILE_NOT_FOUND` instead of inline strings?** (Consistency, easy updates)

---

## What's Next?

In **Part 4**, we'll dive into the detection engine - `core/image_stego_engine.py`:
- How LSB extraction works
- EOF detection implementation
- The 7 validation layers
- Image processing with Pillow
- Actual steganography detection algorithms

This is where the real magic happens - the brain of the tool!

---

**Previous:** [Part 2 - The Main Entry Point](Part_02_Main_Entry_Point.md)
**Next:** [Part 4 - The Detection Engine](Part_04_Detection_Engine.md)

---

*Configuration files might seem boring, but they're crucial for professional software! Understanding config.py gives you control over the tool's behavior without touching complex logic.*
