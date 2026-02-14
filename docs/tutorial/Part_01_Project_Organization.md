# Part 1: Project Organization

## Understanding the Codebase Structure

Now that you know **what** our tool does, let's explore **how** the code is organized. Think of this like learning the layout of a house before we tour each room.

---

## Why Organization Matters

Imagine if your house had:
- Kitchen appliances in the bedroom
- Bathroom fixtures in the garage
- Random items scattered everywhere

You'd waste time finding things and couldn't maintain it properly!

**Good code organization:**
- Makes finding things easy
- Prevents confusion
- Helps multiple people work together
- Makes maintenance and updates simpler

---

## Bird's Eye View: The Main Folder

Our project lives in a folder called `TEST PROJECT`. Inside, we have:

```
TEST PROJECT/
├── main.py                    ← The starting point (runs the program)
├── config.py                  ← Settings and configuration
├── requirements.txt           ← List of needed libraries
├── core/                      ← The brain (detection algorithms)
├── gui/                       ← The face (visual interface)
├── reporting/                 ← The documentarian (creates reports)
├── tests/                     ← Quality control (test scripts)
├── docs/                      ← Documentation and samples
├── logs/                      ← Activity records
└── test_images/               ← Sample images for testing
```

**Analogy:** Think of the project like a restaurant:
- `main.py` = Front door (entry point)
- `core/` = Kitchen (where the work happens)
- `gui/` = Dining room (what customers see)
- `reporting/` = Bookkeeping office (records and documentation)
- `tests/` = Health inspector (quality checks)
- `docs/` = Menu and promotional materials
- `logs/` = Receipt records
- `test_images/` = Sample dishes for taste testing

---

## File-by-File Breakdown

### Root Level Files

#### 1. `main.py` - The Program Entry Point

**What it is:** The file that starts everything.

**What it does:**
- Imports all necessary components
- Sets up the initial configuration
- Launches the graphical interface
- Acts as the "glue" connecting all parts

**Analogy:** Like the ignition in a car - turn the key (run this file) and the whole system starts up.

**When you run it:**
```
python main.py
```
The GUI window appears and the tool is ready to use.

---

#### 2. `config.py` - Configuration Settings

**What it is:** A central place for all settings and constants.

**What it does:**
- Stores detection thresholds (how sensitive the tool is)
- Defines supported file formats
- Sets default values
- Contains steganography tool signatures

**Why separate config?**
- Easy to adjust settings without hunting through code
- One place to change behavior
- No hardcoded "magic numbers" scattered everywhere

**Analogy:** Like the settings panel on your phone - all adjustable options in one place.

---

#### 3. `requirements.txt` - Dependency List

**What it is:** A shopping list of external libraries the project needs.

**Contents example:**
```
Pillow==10.0.0
```

**What it does:**
- Tells Python which extra packages to install
- Specifies versions to ensure compatibility

**How it's used:**
```
pip install -r requirements.txt
```
This command installs everything the project needs.

**Analogy:** Like a recipe's ingredient list - before cooking, you need to get these items from the store.

---

### The `core/` Folder - The Detection Engine

**Purpose:** Contains the core logic for analyzing images and detecting steganography.

**Contents:**
```
core/
├── __init__.py                ← Makes this a Python package
└── image_stego_engine.py      ← The main detection engine
```

#### `image_stego_engine.py` - The Brain

**What it is:** The most important file - contains all detection algorithms.

**Key responsibilities:**
1. **Load and read images** - Opens image files and accesses pixel data
2. **LSB extraction** - Extracts hidden data from least significant bits
3. **EOF detection** - Checks for data appended after the image
4. **Validation layers** - Applies 7 checks to reduce false positives
5. **Result compilation** - Packages findings into structured results

**Major components inside:**
- `ImageStegoEngine` class - The main detection object
- `analyze_image()` method - Orchestrates the entire analysis
- `extract_lsb()` method - Performs LSB extraction
- `check_eof_data()` method - Looks for EOF anomalies
- `validate_findings()` method - Runs all 7 validation checks

**Analogy:** Like a medical diagnostic machine - you put in a sample (image), it runs tests (algorithms), and outputs a diagnosis (clean or suspicious).

**File size:** ~500+ lines of code

---

### The `gui/` Folder - The User Interface

**Purpose:** Creates the visual windows, buttons, and interactive elements users see.

**Contents:**
```
gui/
├── __init__.py                ← Makes this a Python package
├── main_window.py             ← The main application window
└── file_dialog.py             ← File selection dialogs
```

#### `main_window.py` - The Main Interface

**What it is:** Defines the main application window and all its components.

**Key responsibilities:**
1. **Create the window** - Sets up the main application frame
2. **Build UI elements** - Adds buttons, text areas, progress bars
3. **Handle user actions** - Responds when users click buttons
4. **Display results** - Shows analysis findings in readable format
5. **Manage workflow** - Coordinates between user input and backend processing

**Major components inside:**
- `MainWindow` class - Represents the entire application window
- Button handlers (e.g., `analyze_button_clicked()`)
- Result display formatting
- Progress indicators

**Analogy:** Like the cockpit of an airplane - all the controls and displays the pilot (user) interacts with.

---

#### `file_dialog.py` - File Selection Helper

**What it is:** Handles opening file/folder selection dialogs.

**What it does:**
- Shows "Open File" dialog when user wants to select an image
- Shows "Open Folder" dialog for batch processing
- Filters to show only supported image formats
- Returns selected file paths to the main window

**Analogy:** Like the librarian who helps you find books - assists in locating files on your computer.

---

### The `reporting/` Folder - Documentation Generator

**Purpose:** Creates logs and reports of analysis activities.

**Contents:**
```
reporting/
├── __init__.py                ← Makes this a Python package
├── logger.py                  ← CSV logging functionality
└── report_generator.py        ← Report text generation
```

#### `logger.py` - Activity Recorder

**What it is:** Records every analysis action to a CSV file.

**What it does:**
- Creates CSV log files with timestamps
- Records 15 fields per analysis:
  - Timestamp
  - File name and path
  - File size and hash
  - Detection results
  - Validation layer outcomes
  - Confidence scores
- Appends new entries without overwriting old ones

**Why CSV?**
- Easy to open in Excel or import into other tools
- Can be fed into SIEM systems (Security Information and Event Management)
- Searchable and sortable

**Analogy:** Like a security camera's recording system - keeps detailed records of everything that happens.

---

#### `report_generator.py` - Summary Report Creator

**What it is:** Generates human-readable summary reports from CSV logs.

**What it does:**
- Reads accumulated CSV log data
- Calculates statistics:
  - Total images scanned
  - How many flagged as suspicious
  - How many were clean
  - Detection rate percentages
- Formats findings into readable text
- Creates summary reports analysts can read

**Analogy:** Like an accountant who takes transaction records and creates summary statements.

---

### The `tests/` Folder - Quality Assurance

**Purpose:** Contains test scripts to verify the tool works correctly.

**Contents:**
```
tests/
├── __init__.py                     ← Makes this a Python package
├── README.md                       ← Explains each test
├── quick_test.py                   ← Fast basic functionality test
├── test_detection_fix.py           ← Tests detection accuracy
├── test_phase2.py                  ← Phase 2 testing
├── test_phase3_guide.py            ← Phase 3 testing
└── test_phase4_gui.py              ← GUI testing
```

**Why test?**
- Ensure code works as expected
- Catch bugs before users find them
- Verify changes don't break existing features
- Build confidence in the tool's reliability

**Types of tests:**
1. **Unit tests** - Test individual functions
2. **Integration tests** - Test how components work together
3. **GUI tests** - Verify the interface works
4. **Detection tests** - Validate detection accuracy

**Analogy:** Like a car manufacturer's quality control - testing everything before shipping to customers.

---

### The `docs/` Folder - Documentation

**Purpose:** Contains project documentation and sample reports.

**Contents:**
```
docs/
└── SAMPLE_ANALYSIS_REPORT_V1.md    ← Example output report
```

**What it contains:**
- **Sample analysis report** - Shows what a real tool output looks like
- Demonstrates the tool's professional reporting capabilities
- Used for presentations and demonstrations

**Analogy:** Like a brochure showing what the product can do.

---

### The `logs/` Folder - Historical Records

**Purpose:** Stores CSV log files generated during actual usage.

**Contents (examples):**
```
logs/
├── real_test_log.csv
├── stego_analysis_20260214_091449.csv
└── test_phase2_log.csv
```

**What it contains:**
- CSV files with analysis history
- Timestamped records of every image scanned
- Detailed detection results

**File naming pattern:**
- `stego_analysis_YYYYMMDD_HHMMSS.csv`
- Each session gets a unique timestamp

**Why keep logs?**
- Audit trail for security investigations
- Historical analysis
- Performance metrics
- Compliance requirements

**Analogy:** Like medical records - keeps history of all past diagnostic results.

---

### The `test_images/` Folder - Sample Data

**Purpose:** Contains sample images for testing and demonstration.

**What it holds:**
- Clean images (no hidden data)
- Images with steganography (for detection testing)
- Various formats (PNG, JPG, BMP, etc.)
- Different sizes and complexities

**Why separate test images?**
- Don't need to hunt for test files
- Consistent testing environment
- Ready-made examples for demonstrations

**Analogy:** Like a training dummy for medical students - safe practice material.

---

## Special Files: `__init__.py`

You'll see `__init__.py` files in many folders. 

**What is it?**
- A special Python file (often empty or nearly empty)
- Tells Python "this folder is a package"
- Allows importing modules from that folder

**Example:**
Without `__init__.py` in `core/`:
```python
# This would fail:
from core import image_stego_engine
```

With `__init__.py` in `core/`:
```python
# This works:
from core import image_stego_engine
```

**Analogy:** Like a sign on a store door saying "We're open for business" - signals that the folder contains importable code.

---

## Special Files: `__pycache__/`

You might notice `__pycache__/` folders appear.

**What is it?**
- Automatically created by Python
- Stores compiled bytecode (optimized versions of your code)
- Makes the program load faster on subsequent runs

**Should you edit it?**
- **NO!** Never edit these manually
- Python manages them automatically

**Should you commit it to version control?**
- Usually no (added to `.gitignore`)

**Analogy:** Like the temporary files your web browser creates to load sites faster - helpful but not something you interact with.

---

## How Components Work Together

### The Flow of Execution

Let's trace what happens when you run the tool:

**1. User runs `main.py`:**
```python
python main.py
```

**2. `main.py` does:**
- Imports configuration from `config.py`
- Imports GUI components from `gui/main_window.py`
- Imports detection engine from `core/image_stego_engine.py`
- Launches the main window

**3. Main window appears:**
- User sees buttons and input areas
- GUI is ready for interaction

**4. User clicks "Analyze Image":**
- `gui/main_window.py` handles the click
- Opens file dialog via `gui/file_dialog.py`
- User selects an image

**5. Analysis begins:**
- GUI passes image path to `core/image_stego_engine.py`
- Engine loads the image
- Runs LSB extraction
- Runs EOF detection
- Applies 7 validation layers
- Returns results

**6. Results displayed:**
- Engine returns findings to GUI
- GUI formats and displays results
- `reporting/logger.py` records to CSV
- User sees outcome on screen

**Visual Flow:**
```
User Action
    ↓
main.py (entry point)
    ↓
gui/main_window.py (accepts input)
    ↓
core/image_stego_engine.py (analyzes)
    ↓
reporting/logger.py (records)
    ↓
gui/main_window.py (displays results)
    ↓
User sees outcome
```

---

## Separation of Concerns

**Important Design Principle:**

Each folder/module has a **single responsibility**:
- `core/` = Detection logic (doesn't care how results are displayed)
- `gui/` = User interface (doesn't care how detection works internally)
- `reporting/` = Documentation (doesn't care about GUI or detection details)

**Why this matters:**
- Can change GUI without touching detection code
- Can improve detection algorithms without breaking the interface
- Easier to test individual components
- Multiple people can work on different parts simultaneously

**Analogy:** Like a car:
- Engine (core) doesn't care what the dashboard looks like
- Dashboard (GUI) doesn't care how the engine works
- Both can be upgraded independently

---

## Import Structure

How files reference each other:

**`main.py` imports:**
```python
from gui.main_window import MainWindow
from core.image_stego_engine import ImageStegoEngine
import config
```

**`gui/main_window.py` imports:**
```python
from core.image_stego_engine import ImageStegoEngine
from reporting.logger import Logger
from gui.file_dialog import FileDialog
```

**Key point:** Files import only what they need, creating clean dependencies.

---

## Configuration Management

**Why `config.py` is important:**

Instead of scattered values throughout code:
```python
# Bad - magic numbers everywhere
if confidence > 0.75:  # What does 0.75 mean?
    flag_as_suspicious()
```

We centralize in `config.py`:
```python
# config.py
DETECTION_THRESHOLD = 0.75  # Confidence level to flag as suspicious
```

Then use it:
```python
# Good - clear and adjustable
if confidence > config.DETECTION_THRESHOLD:
    flag_as_suspicious()
```

**Benefits:**
- Change one value → affects entire program
- Behavior is explicit and documented
- Easy for analysts to tune sensitivity

---

## Project Statistics

Let me give you a sense of scale:

| Component | Files | Approximate Lines of Code |
|-----------|-------|---------------------------|
| Core (detection engine) | 1 | ~500 lines |
| GUI (interface) | 2 | ~400 lines |
| Reporting (logs/reports) | 2 | ~300 lines |
| Main/Config | 2 | ~200 lines |
| Tests | 5 | ~400 lines |
| **Total** | **~12 code files** | **~1800+ lines** |

Plus documentation files (like this guide), sample reports, and supporting files.

---

## Directory Best Practices

**Why we organize this way:**

1. **Logical grouping** - Related code lives together
2. **Discoverability** - Know where to find things
3. **Scalability** - Easy to add new features in the right place
4. **Collaboration** - Multiple developers can work simultaneously
5. **Maintenance** - Find and fix bugs faster

**Python community standards:**
- Lowercase folder names
- Underscores instead of spaces
- `__init__.py` to mark packages
- Tests in a separate `tests/` folder

---

## Finding What You Need

**Quick reference guide:**

| If you want to... | Look in... |
|-------------------|------------|
| Change detection algorithms | `core/image_stego_engine.py` |
| Modify the interface | `gui/main_window.py` |
| Adjust detection sensitivity | `config.py` |
| See how reports are made | `reporting/report_generator.py` |
| Check activity logs | `logs/` folder |
| Run tests | `tests/` folder |
| See example output | `docs/SAMPLE_ANALYSIS_REPORT_V1.md` |
| Change what gets logged | `reporting/logger.py` |

---

## Understanding File Relationships

**Dependency hierarchy:**

```
main.py
  ├─ relies on → config.py
  └─ launches → gui/main_window.py
                  ├─ uses → core/image_stego_engine.py
                  │           └─ uses → config.py
                  └─ uses → reporting/logger.py
                              └─ uses → reporting/report_generator.py
```

**Key insight:** `main.py` is at the top, but doesn't do much itself - it coordinates others.

---

## What's Next?

Now that you understand the project layout, we're ready to dive into the actual code!

In **Part 2**, we'll examine `main.py` line by line:
- How it imports components
- How it sets up the application
- How it launches the GUI
- Every variable, every function, explained in detail

You'll see exactly how the entry point works and how it kicks off the entire program.

---

## Review Questions

Before moving on, make sure you understand:

1. **What is the purpose of each main folder?** (`core/`, `gui/`, `reporting/`)
2. **What file do you run to start the application?** (`main.py`)
3. **Where are detection algorithms located?** (`core/image_stego_engine.py`)
4. **What does `config.py` do?** (Stores settings and constants)
5. **Why separate code into folders?** (Organization, maintainability, clarity)

---

**Previous:** [Part 0 - Introduction](Part_00_Introduction.md)
**Next:** [Part 2 - The Main Entry Point (main.py)](Part_02_Main_Entry_Point.md)

---

*Take a moment to navigate through the actual project folders and find the files we discussed. Getting comfortable with the structure now will make understanding the code much easier!*
