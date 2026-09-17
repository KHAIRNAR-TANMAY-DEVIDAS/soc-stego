# Part 2: The Main Entry Point (main.py)

## Understanding the Starting Point

Now that you understand the project organization, let's dive into the actual code! We'll start with `main.py` - the file that starts everything when you run the program.

We'll go through this file **line by line**, explaining every single piece.

---

## What Does main.py Do?

Think of `main.py` as the **receptionist at a hotel**:
- Greets you when you arrive
- Asks what you need (GUI? Verification? CLI?)
- Directs you to the right place
- Handles errors if something goes wrong

**Purpose:** This file doesn't do the heavy lifting itself. Instead, it:
1. Figures out what mode you want to run (GUI, CLI, or verification)
2. Sets up the environment
3. Launches the appropriate component
4. Handles errors gracefully

---

## The Complete File (Overview)

Before diving into details, here's the bird's eye view:

```python
# Header comment (documentation)
# Import statements (bring in tools we need)
# Path setup (tell Python where to find our modules)
# main() function (decides what to do)
# launch_application() function (starts the GUI)
# run_verification() function (checks everything works)
# Startup code (actually runs main())
```

**Total lines:** ~120 lines
**Key functions:** 3 (main, launch_application, run_verification)

---

## Line-by-Line Explanation

### Section 1: File Header (Lines 1-4)

```python
"""
SOC Steganography Detection Tool - Main Entry Point
Phase 1: Project structure established
Phase 2: CSV logging implementation
Phase 3: GUI implementation
"""
```

**What is this?**
- Called a **docstring** (documentation string)
- The triple quotes `"""` allow multi-line text
- Describes what this file is and what development phases were completed

**Why it matters:**
- Anyone reading the code immediately knows what this file does
- Documents the development history

**Analogy:** Like the title and description on the cover of a book.

---

### Section 2: Import Statements (Lines 6-8)

#### Line 6: Importing `sys`

```python
import sys
```

**What is `sys`?**
- Short for "system"
- A built-in Python module (comes with Python, no installation needed)
- Provides access to system-specific parameters and functions

**What we use it for in this file:**
- `sys.path` - tells Python where to look for modules
- `sys.exit()` - cleanly exit the program with an error code

**Analogy:** Like the control panel for your Python program's environment.

---

#### Line 7: Importing `os`

```python
import os
```

**What is `os`?**
- Short for "operating system"
- Built-in Python module for interacting with the operating system
- Works on Windows, Mac, and Linux

**What we use it for:**
- `os.path.dirname()` - get the directory path of a file
- `os.path.abspath()` - get the absolute (full) path of a file
- `os.path.exists()` - check if a file or folder exists

**Analogy:** Like a universal remote that works with any TV (operating system).

---

#### Line 8: Importing `argparse`

```python
import argparse
```

**What is `argparse`?**
- Built-in Python module for parsing command-line arguments
- Handles flags like `--verify` or `--cli`
- Automatically generates help messages

**What we use it for:**
- Let users run: `python main.py --verify` (run verification mode)
- Or: `python main.py --cli` (run CLI mode)
- Or just: `python main.py` (run GUI mode, the default)

**Analogy:** Like a menu at a restaurant - gives users options for how they want to proceed.

---

### Section 3: Path Setup (Lines 10-11)

#### Line 10: Comment

```python
# Add project root to Python path
```

**What is this?**
- A comment (ignored by Python, just for human readers)
- Explains what the next line does
- Comments start with `#`

**Why comments?**
- Help other developers (or future you) understand your code
- Document why you did something

---

#### Line 11: Path Manipulation

```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

**This looks complicated! Let's break it down from inside out:**

**Step 1: `__file__`**
- Special Python variable
- Contains the path to the current file (main.py)
- Example: `"d:\TEST PROJECT\main.py"`

**Step 2: `os.path.abspath(__file__)`**
- Makes sure the path is absolute (full path)
- Example result: `"d:\TEST PROJECT\main.py"`

**Step 3: `os.path.dirname(...)`**
- Gets the directory part, removing the filename
- Example result: `"d:\TEST PROJECT"`

**Step 4: `sys.path.insert(0, ...)`**
- `sys.path` is a list of directories Python searches for modules
- `.insert(0, ...)` adds our project directory to the **front** of that list
- Position 0 means "check here first"

**Why do this?**
- Ensures Python can find our modules (`core`, `gui`, `reporting`)
- Works regardless of where you run the script from

**Real-world scenario:**
```
Without this line:
  You run: python main.py
  Python tries: from core import ...
  Python error: ModuleNotFoundError!

With this line:
  You run: python main.py
  Python knows to look in d:\TEST PROJECT\
  Python finds: d:\TEST PROJECT\core\
  Success!
```

**Analogy:** Like telling your GPS "start from home" so it always knows where to look for directions.

---

### Section 4: Configuration Import (Line 13)

```python
from config import APP_NAME, APP_VERSION, APP_DESCRIPTION
```

**Breaking it down:**

**`from config`** 
- Look in the `config.py` file

**`import APP_NAME, APP_VERSION, APP_DESCRIPTION`**
- Bring in these three specific variables

**What are these?**
- `APP_NAME` - probably something like `"SOC Steganography Detection Tool"`
- `APP_VERSION` - probably something like `"1.0.0"`
- `APP_DESCRIPTION` - a text description of what the tool does

**Why import these?**
- Centralized configuration - change the version once in `config.py`, affects everywhere
- No hardcoded strings scattered throughout code
- Easy to keep consistent

**Example usage:**
```python
print(f"Launching {APP_NAME} v{APP_VERSION}...")
# Output: Launching SOC Steganography Detection Tool v1.0.0...
```

**Analogy:** Like keeping all your phone contacts in one address book rather than writing them on random sticky notes.

---

### Section 5: The main() Function (Lines 15-32)

#### Line 15-18: Function Definition

```python
def main():
    """
    Main application entry point.
    Launches the Tkinter GUI or runs verification based on arguments.
    """
```

**Breaking it down:**

**`def main():`**
- `def` = define a function
- `main` = the function name
- `()` = no parameters (doesn't take any inputs)
- `:` = start of the function body

**The docstring:**
- Explains what this function does
- Good practice to document every function

**What this function does:**
- Parses command-line arguments
- Decides which mode to run
- Calls the appropriate function

**Analogy:** Like a switchboard operator who routes your call to the right department.

---

#### Lines 19-23: Argument Parser Setup

```python
    parser = argparse.ArgumentParser(description=APP_DESCRIPTION)
    parser.add_argument('--verify', action='store_true', 
                       help='Run project structure verification instead of launching GUI')
    parser.add_argument('--cli', action='store_true',
                       help='Launch CLI mode instead of GUI')
```

**Line 19: Create the parser**
```python
parser = argparse.ArgumentParser(description=APP_DESCRIPTION)
```
- `argparse.ArgumentParser()` creates a new argument parser object
- `description=APP_DESCRIPTION` sets the description shown in help messages
- We store it in variable `parser`

**Lines 20-21: Add --verify flag**
```python
parser.add_argument('--verify', action='store_true', 
                   help='Run project structure verification instead of launching GUI')
```
- `'--verify'` - the flag name (users type: `python main.py --verify`)
- `action='store_true'` - if flag is present, set to True; if absent, set to False
- `help='...'` - description shown when user runs `python main.py --help`

**Lines 22-23: Add --cli flag**
```python
parser.add_argument('--cli', action='store_true',
                   help='Launch CLI mode instead of GUI')
```
- `'--cli'` - the flag name (users type: `python main.py --cli`)
- Same structure as --verify flag

**What this enables:**

| Command | What happens |
|---------|-------------|
| `python main.py` | No flags → launches GUI (default) |
| `python main.py --verify` | Runs verification mode |
| `python main.py --cli` | Runs CLI mode |
| `python main.py --help` | Shows help message |

---

#### Line 25: Parse the Arguments

```python
    args = parser.parse_args()
```

**What this does:**
- Actually reads the command-line arguments
- Stores the results in `args` object

**What `args` contains:**
- `args.verify` - True if --verify was passed, False otherwise
- `args.cli` - True if --cli was passed, False otherwise

**Example:**
```python
# User runs: python main.py --verify
# Result: args.verify = True, args.cli = False

# User runs: python main.py --cli
# Result: args.verify = False, args.cli = True

# User runs: python main.py
# Result: args.verify = False, args.cli = False
```

---

#### Lines 27-36: Decision Logic

```python
    if args.verify:
        # Run verification mode
        run_verification()
    elif args.cli:
        # Launch CLI mode
        print(f"\n{APP_NAME} v{APP_VERSION} - CLI Mode")
        print("=" * 60)
        from core.image_stego_engine import main as cli_main
        cli_main()
    else:
        # Launch GUI (default)
        launch_application()
```

**This is a decision tree (if-elif-else):**

**1. If --verify flag was passed:**
```python
if args.verify:
    run_verification()
```
- Call the `run_verification()` function
- This checks that all modules and directories exist

**2. Else if --cli flag was passed:**
```python
elif args.cli:
    print(f"\n{APP_NAME} v{APP_VERSION} - CLI Mode")
    print("=" * 60)
    from core.image_stego_engine import main as cli_main
    cli_main()
```

Let's break down each line:

**Line 31:** Print header with app name and version
- `f""` is an f-string (formatted string) - lets you insert variables with `{}`
- `\n` is a newline (blank line before text)

**Line 32:** Print separator line
- `"=" * 60` creates a string of 60 equal signs
- Output: `============================================================`

**Line 33:** Import the CLI entry point
- `from core.image_stego_engine` - look in that module
- `import main` - bring in the `main` function
- `as cli_main` - rename it to `cli_main` (to avoid confusion with our `main()`)

**Line 34:** Run the CLI
- Calls the imported function

**3. Otherwise (default):**
```python
else:
    launch_application()
```
- If neither flag was passed, launch the GUI
- This is the normal mode most users will use

**Analogy:** Like a restaurant host asking "Do you have a reservation? Do you want takeout? Otherwise, I'll seat you in the dining room."

---

### Section 6: The launch_application() Function (Lines 38-51)

```python
def launch_application():
    """Launch the main GUI application."""
    print(f"Launching {APP_NAME} v{APP_VERSION}...")
    
    try:
        from gui import launch_gui
        launch_gui()
    except ImportError as e:
        print(f"Error: Failed to import GUI module: {e}")
        print("\nTrying to run verification...")
        run_verification()
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to launch GUI: {e}")
        sys.exit(1)
```

**What this function does:**
- Attempts to launch the graphical interface
- Handles errors gracefully if something goes wrong

---

#### Line 38-39: Function Definition

```python
def launch_application():
    """Launch the main GUI application."""
```
- Defines a function named `launch_application`
- No parameters needed
- Docstring explains its purpose

---

#### Line 40: User Feedback

```python
    print(f"Launching {APP_NAME} v{APP_VERSION}...")
```
- Prints a message to the terminal
- Lets the user know the program is starting
- Good UX (user experience) - don't leave users wondering if it's working

**Example output:**
```
Launching SOC Steganography Detection Tool v1.0.0...
```

---

#### Lines 42-51: Try-Except Error Handling

**What is try-except?**
- A way to handle errors without crashing
- "Try" to do something risky
- If it fails, "except" (catch) the error and handle it gracefully

**Structure:**
```python
try:
    # Risky code that might fail
except SpecificError:
    # Handle that specific error
except AnotherError:
    # Handle different error
```

---

#### Lines 42-43: Try to Launch GUI

```python
    try:
        from gui import launch_gui
        launch_gui()
```

**Line 43:** Import the launch function
- `from gui` - look in the gui package
- `import launch_gui` - bring in the `launch_gui` function

**Why import here instead of at the top?**
- Lazy loading - only load GUI if needed
- Avoids import errors if GUI dependencies are missing and user is running --verify mode

**Line 44:** Actually launch
- Calls the imported function
- This opens the GUI window and starts the application

---

#### Lines 44-48: Handle Import Errors

```python
    except ImportError as e:
        print(f"Error: Failed to import GUI module: {e}")
        print("\nTrying to run verification...")
        run_verification()
        sys.exit(1)
```

**Line 45: Catch ImportError**
- `ImportError` happens when a module can't be imported
- `as e` stores the error details in variable `e`

**Possible causes:**
- Missing Tkinter installation
- Corrupted gui module files
- Missing dependencies

**Line 46:** Tell the user what went wrong
- `{e}` inserts the error message

**Line 47:** Try to help diagnose
- Prints a message
- Offers to run verification to check the setup

**Line 48:** Run verification
- Calls `run_verification()` function
- This will check what's missing or broken

**Line 49:** Exit with error code
- `sys.exit(1)` - terminates the program
- `1` is the exit code (0 = success, non-zero = error)
- Other programs can detect this error code

**Why exit?**
- Can't continue without GUI if that's what user wanted
- Clean termination better than crash

---

#### Lines 49-51: Handle Other Errors

```python
    except Exception as e:
        print(f"Error: Failed to launch GUI: {e}")
        sys.exit(1)
```

**Line 50: Catch all other errors**
- `Exception` is the base class for all errors
- Catches anything we didn't specifically handle above

**Possible causes:**
- GUI window creation failed
- Tkinter configuration error
- Any unexpected problem

**Line 51-52:** Inform user and exit
- Print the error
- Exit with error code 1

**Why two except blocks?**
- First one (`ImportError`) can try verification as a fallback
- Second one (generic `Exception`) just fails - can't recover

---

### Section 7: The run_verification() Function (Lines 53-114)

This is the longest function - it checks that everything is set up correctly.

```python
def run_verification():
    """Run project structure and module verification."""
```

**Purpose:** 
- Check all modules can be imported
- Verify all required directories exist
- Show which development phases are complete
- Helpful for troubleshooting

**Analogy:** Like a pre-flight checklist for an airplane - verify everything works before takeoff.

---

#### Lines 54-58: Print Header

```python
    print("=" * 60)
    print(f"{APP_NAME}")
    print(f"Version {APP_VERSION}")
    print("=" * 60)
    print(f"\n{APP_DESCRIPTION}\n")
```

**What this does:**
- Prints a nice formatted header
- Shows app name, version, description

**Example output:**
```
============================================================
SOC Steganography Detection Tool
Version 1.0.0
============================================================

Advanced steganography detection with SOC integration

```

---

#### Lines 60-62: Section 1 Header

```python
    # Phase 1: Verify imports
    print("Phase 1: Project Structure Verification")
    print("-" * 60)
```

- Line 61 is a comment (reminder of what we're doing)
- Line 62-63 print section headers
- `"-" * 60` creates a line of dashes (separator)

---

#### Lines 64-71: Verify Core Module

```python
    try:
        from core.image_stego_engine import analyze_image, encode_message, decode_message
        print("✓ Core module imported successfully")
        print("  - analyze_image()")
        print("  - encode_message()")
        print("  - decode_message()")
    except ImportError as e:
        print(f"✗ Error importing core module: {e}")
        sys.exit(1)
```

**What this does:**
- **Tries** to import key functions from the core module
- If successful: prints ✓ (checkmark) and lists imported functions
- If fails: prints ✗ (X mark) and exits with error

**Why these specific functions?**
- `analyze_image()` - the main detection function
- `encode_message()` - embeds hidden data (for testing)
- `decode_message()` - extracts hidden data

**Line 66:** Import attempt
```python
from core.image_stego_engine import analyze_image, encode_message, decode_message
```
- Imports three functions at once
- Separated by commas

**Lines 67-70:** Success message
- `✓` is a Unicode checkmark character
- Lists the successfully imported functions
- Indented `  - ` makes it look like a list

**Lines 71-73:** Error handling
- If import fails, print error with ✗
- Exit immediately (can't continue without core module)

---

#### Lines 74-82: Verify Config Module

```python
    try:
        import config
        print("✓ Configuration module imported successfully")
        print(f"  - Logs directory: {config.LOGS_DIR}")
        print(f"  - CSV fields defined: {len(config.CSV_FIELDS)} fields")
    except ImportError as e:
        print(f"✗ Error importing config module: {e}")
        sys.exit(1)
```

**Same pattern as before:**
- Try to import `config` module
- If successful: print checkmark and show some config details
- If fails: print error and exit

**Line 77:** Show logs directory location
- `config.LOGS_DIR` is a variable defined in config.py
- Probably something like `"logs"` or `"d:\TEST PROJECT\logs"`

**Line 78:** Show how many CSV fields are configured
- `config.CSV_FIELDS` is probably a list or tuple
- `len()` gets the length (number of items)
- Probably shows something like: "CSV fields defined: 15 fields"

---

#### Lines 84-96: Verify Reporting Module

```python
    try:
        from reporting import (
            log_analysis_to_csv, 
            generate_summary_report,
            format_report_text
        )
        print("✓ Reporting module imported successfully")
        print("  - log_analysis_to_csv()")
        print("  - generate_summary_report()")
        print("  - format_report_text()")
    except ImportError as e:
        print(f"✗ Error importing reporting module: {e}")
        sys.exit(1)
```

**Same verification pattern for reporting module**

**Lines 85-89:** Multi-line import
- You can break imports across multiple lines using `( )`
- Makes code more readable when importing many things

**Three functions imported:**
- `log_analysis_to_csv()` - writes analysis results to CSV
- `generate_summary_report()` - creates summary from multiple analyses
- `format_report_text()` - formats report text for display

---

#### Lines 98-106: Verify Directory Structure

```python
    # Check if required directories exist
    required_dirs = ['core', 'gui', 'reporting', 'config', 'tests', 'logs']
    all_dirs_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ Directory exists: /{directory}")
        else:
            print(f"✗ Directory missing: /{directory}")
            all_dirs_exist = False
```

**Line 99:** Define required directories
```python
required_dirs = ['core', 'gui', 'reporting', 'config', 'tests', 'logs']
```
- A list of directory names (strings)
- Square brackets `[]` create a list
- Items separated by commas

**Line 100:** Initialize tracking variable
```python
all_dirs_exist = True
```
- Start assuming everything is good
- We'll set this to False if we find a missing directory

**Line 101:** Loop through directories
```python
for directory in required_dirs:
```
- **for loop** - repeats code for each item
- `directory` is the variable holding the current item
- First loop: `directory = 'core'`
- Second loop: `directory = 'gui'`
- And so on...

**Lines 102-106:** Check each directory
```python
    if os.path.exists(directory):
        print(f"✓ Directory exists: /{directory}")
    else:
        print(f"✗ Directory missing: /{directory}")
        all_dirs_exist = False
```

- `os.path.exists(directory)` returns True if directory exists, False otherwise
- If exists: print checkmark
- If missing: print X and set flag to False

**Example output:**
```
✓ Directory exists: /core
✓ Directory exists: /gui
✓ Directory exists: /reporting
✗ Directory missing: /config
✓ Directory exists: /tests
✓ Directory exists: /logs
```

---

#### Line 108: Separator

```python
    print("-" * 60)
```
- Prints a line of dashes to separate sections
- Visual organization in the terminal

---

#### Lines 110-122: Final Status Report

```python
    if all_dirs_exist:
        print("\n✅ Phase 1 Complete: Project structure validated!")
        print("✅ Phase 2 Complete: CSV logging & reporting ready!")
        print("✅ Phase 3 Complete: GUI implementation ready!")
        print("\nAvailable Commands:")
        print("  python main.py              → Launch GUI (default)")
        print("  python main.py --verify     → Run this verification")
        print("  python main.py --cli        → Launch CLI mode")
        print("  python test_phase2.py       → Test reporting module")
    else:
        print("\n❌ Some directories are missing")
        sys.exit(1)
```

**Line 111: Check if everything passed**
```python
if all_dirs_exist:
```
- Remember we set this to False if any directory was missing

**Lines 112-120: Success messages**
- `✅` is a green checkmark emoji
- Shows which project phases are complete
- Lists available commands users can run
- `→` is an arrow showing what each command does

**Lines 121-123: Failure path**
```python
else:
    print("\n❌ Some directories are missing")
    sys.exit(1)
```
- If any directory was missing, show error
- Exit with error code

---

#### Line 124: Footer

```python
    print("\n" + "=" * 60)
```
- Final separator line
- `\n` adds blank line before it
- Closes out the verification report nicely

---

### Section 8: The Program Entry Point (Lines 126-127)

```python
if __name__ == "__main__":
    main()
```

**This is a special Python pattern. Let's break it down:**

#### Understanding `__name__`

**What is `__name__`?**
- A special built-in variable in Python
- Every Python file has one
- Its value depends on how the file is run

**Two scenarios:**

**Scenario 1: File is run directly**
```bash
python main.py
```
- Python sets: `__name__ = "__main__"`
- The if condition is True
- `main()` gets called

**Scenario 2: File is imported by another file**
```python
# In some_other_file.py
import main
```
- Python sets: `__name__ = "main"` (the module name)
- The if condition is False
- `main()` is NOT called automatically

**Why this pattern?**
- Allows code to be both:
  - **Runnable** as a script: `python main.py`
  - **Importable** as a module: `import main` (without auto-running)

**Real-world analogy:**
- Like a book that can be:
  - Read from cover to cover (run directly)
  - Used as a reference (imported without auto-playing)

**In our case:**
- When you run `python main.py`, the condition is True
- So `main()` function gets called
- Which triggers the argument parsing and application launch

**The two lines together:**
```python
if __name__ == "__main__":  # If this file is being run directly
    main()                   # Then call the main() function
```

---

## Flow Summary: What Happens When You Run main.py

Let's trace the execution:

**1. Python starts reading the file**
```
Read imports → import sys, os, argparse
Set up path → sys.path.insert(...)
Import config → get APP_NAME, APP_VERSION, APP_DESCRIPTION
Define functions → main(), launch_application(), run_verification()
```

**2. Python reaches the bottom**
```python
if __name__ == "__main__":  ← This is True (file run directly)
    main()                   ← Call main()
```

**3. Inside main()**
```
Create argument parser
Check command-line flags
  ├─ --verify? → run_verification()
  ├─ --cli? → print header, import CLI, run CLI
  └─ Neither? → launch_application()
```

**4. Most common path: launch_application()**
```
Print "Launching..."
Try to import GUI
  ├─ Success? → launch_gui() → GUI window opens
  └─ Failure? → print error, run_verification(), exit
```

**Visual flow diagram:**
```
python main.py
       ↓
   main()
       ↓
  Parse args
       ↓
    ┌───┴───┬─────────┐
    ↓       ↓         ↓
--verify  --cli    (none)
    ↓       ↓         ↓
 run_      CLI    launch_
verify()  mode   application()
    ↓       ↓         ↓
  Check   Run     Import GUI
  setup   CLI        ↓
          mode    launch_gui()
                      ↓
                  GUI opens!
```

---

## Key Concepts Explained

### Functions

**What is a function?**
- A reusable block of code with a name
- Like a mini-program inside your program

**Anatomy:**
```python
def function_name(parameter1, parameter2):
    """Docstring explaining what this does"""
    # Function body (the code)
    return result  # Optional
```

**In main.py:**
- `main()` - no parameters, orchestrates everything
- `launch_application()` - no parameters, starts GUI
- `run_verification()` - no parameters, checks setup

---

### Variables

**What is a variable?**
- A named container that holds a value
- Like a labeled box

**Examples from main.py:**
```python
parser = ...           # Holds an ArgumentParser object
args = ...             # Holds parsed arguments
required_dirs = [...]  # Holds a list of directory names
all_dirs_exist = True  # Holds a boolean (True/False)
```

---

### Importing

**What is importing?**
- Bringing in code from other files
- Lets you use functions/variables defined elsewhere

**Types we saw:**
```python
import sys                    # Import entire module
from config import APP_NAME   # Import specific item
import argparse               # Import built-in module
from gui import launch_gui    # Import from our own modules
```

---

### Error Handling (try-except)

**Why error handling?**
- Code can fail for many reasons
- Better to handle gracefully than crash

**Pattern:**
```python
try:
    # Risky operation
    potentially_failing_code()
except SpecificError:
    # Handle the specific error
    print("Something went wrong")
```

**In main.py:**
- Try to import GUI → catch ImportError
- Try to launch GUI → catch general Exception

---

### Lists

**What is a list?**
- A collection of items in order
- Can contain any type of data

**Example:**
```python
required_dirs = ['core', 'gui', 'reporting', 'config', 'tests', 'logs']
#                 ↑       ↑      ↑           ↑        ↑       ↑
#              Item 0   Item 1  Item 2     Item 3   Item 4  Item 5
```

**Operations:**
- Access: `required_dirs[0]` → `'core'`
- Loop: `for directory in required_dirs:`
- Length: `len(required_dirs)` → `6`

---

### Loops

**What is a loop?**
- Repeats code multiple times
- Avoids writing the same thing over and over

**Example from run_verification():**
```python
for directory in required_dirs:
    if os.path.exists(directory):
        print(f"✓ Directory exists: /{directory}")
```

**What happens:**
1. First iteration: directory = 'core'
2. Second iteration: directory = 'gui'
3. Continue until all items processed

---

### Conditional Statements (if-elif-else)

**What are conditionals?**
- Make decisions in code
- Execute different code based on conditions

**Structure:**
```python
if condition1:
    # Do this if condition1 is true
elif condition2:
    # Do this if condition1 is false but condition2 is true
else:
    # Do this if both are false
```

**In main():**
```python
if args.verify:
    run_verification()
elif args.cli:
    # Launch CLI
else:
    launch_application()
```

---

## Design Principles in main.py

### 1. Single Responsibility
- Each function does one clear thing
- `main()` → decide what to do
- `launch_application()` → start GUI
- `run_verification()` → check setup

### 2. Error Handling
- Don't crash silently
- Provide helpful error messages
- Try to recover when possible (e.g., run verification if GUI fails)

### 3. User Feedback
- Print messages so users know what's happening
- "Launching..."
- "Phase 1: ..."
- Clear checkmarks ✓ and errors ✗

### 4. Flexibility
- Multiple modes (GUI, CLI, verification)
- Command-line arguments for power users
- Sensible defaults for casual users

### 5. Documentation
- Docstrings for every function
- Comments explaining complex code
- Header comment describing the file

---

## Common Patterns You'll See Elsewhere

### The `if __name__ == "__main__":` Pattern
- Used in almost every Python script
- Allows dual use: run or import

### Try-Except Error Handling
- Critical for robust applications
- User-friendly error messages

### Argument Parsing
- Professional CLI tools use argparse
- Provides help, validation, and clean code

### Function Decomposition
- Break big tasks into small functions
- Easier to understand, test, and maintain

---

## Testing main.py

You can test the different modes:

**1. Default (GUI):**
```bash
python main.py
```
Expected: GUI window opens

**2. Verification mode:**
```bash
python main.py --verify
```
Expected: Checklist of modules and directories

**3. CLI mode:**
```bash
python main.py --cli
```
Expected: Command-line interface starts

**4. Help:**
```bash
python main.py --help
```
Expected: Help message with all options

---

## Review Questions

Before moving to the next part, make sure you understand:

1. **What does `sys.path.insert()` do?** (Adds our project directory so Python can find modules)

2. **What is the purpose of argparse?** (Parse command-line arguments)

3. **What's the difference between `import sys` and `from config import APP_NAME`?** (First imports entire module, second imports specific item)

4. **Why use try-except?** (Handle errors gracefully without crashing)

5. **What does `if __name__ == "__main__":` do?** (Only runs code when file is executed directly, not imported)

6. **What happens when you run `python main.py` with no flags?** (Launches GUI via launch_application())

7. **What does run_verification() check?** (Module imports and directory existence)

---

## What's Next?

In **Part 3**, we'll dive into `config.py`:
- What settings are stored there
- How thresholds control detection sensitivity
- Steganography tool signatures
- File format definitions
- All the constants that control behavior

You'll see exactly what configuration options exist and how they affect the tool.

---

**Previous:** [Part 1 - Project Organization](Part_01_Project_Organization.md)
**Next:** [Part 3 - Configuration (config.py)](Part_03_Configuration.md)

---

*Take your time with this! main.py might seem simple, but it demonstrates many important Python concepts. Try running the different modes yourself to see how the argument parsing works!*
