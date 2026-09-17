# Part 5: The Graphical User Interface (GUI)

## Welcome to the User's Window!

The GUI is what users see and interact with. It's the "face" of our tool - buttons, text boxes, menus, and result displays all come together here to create a user-friendly experience.

**Files covered in this part:**
- `gui/main_window.py` (~470 lines) - The main application window
- `gui/file_dialog.py` (~100 lines) - File selection dialogs
- `gui/__init__.py` - Package initialization

**Analogy:** If the detection engine is the brain, the GUI is the body - hands (buttons), eyes (displays), and mouth (status messages) through which users interact with the tool.

---

## Understanding Tkinter

Before diving into our code, let's understand the framework we're using.

### What is Tkinter?

**Tkinter** = **T**k **inter**face
- Built into Python (no installation needed)
- Cross-platform (works on Windows, Mac, Linux)
- Creates desktop GUI applications
- Mature and stable

**Competitors:**
- PyQt (more powerful but requires installation)
- wxPython (native look but requires installation)
- Kivy (modern, mobile-friendly but complex)

**We chose Tkinter because:**
- ✓ Comes with Python
- ✓ Simple for our needs
- ✓ Well-documented
- ✓ Professional appearance

### Basic Tkinter Concepts

#### Windows (Root)
```python
root = tk.Tk()  # Create main window
root.title("My App")  # Set title
root.geometry("800x600")  # Set size
root.mainloop()  # Start event loop
```

#### Widgets
**Widget** = GUI component (button, label, text box, etc.)

Common widgets:
- `Label` - Display text
- `Button` - Clickable button
- `Entry` - Single-line text input
- `Text` - Multi-line text input
- `Frame` - Container for organizing widgets
- `Menu` - Menu bar (File, Edit, Help, etc.)

#### Layout Managers
**Three ways to position widgets:**

1. **pack()** - Stack widgets (top-to-bottom or left-to-right)
2. **grid()** - Grid layout (rows and columns)
3. **place()** - Exact pixel positioning

**We use all three** depending on the situation!

#### Events
**Event** = Something that happens (button click, key press, mouse move)

**Event handler** = Function that runs when event occurs

```python
def button_clicked():
    print("Button was clicked!")

button = tk.Button(text="Click Me", command=button_clicked)
```

---

## File Structure Overview

```
gui/
├── __init__.py           ← Package setup, exports main functions
├── main_window.py        ← The main application window (470 lines)
└── file_dialog.py        ← File selection helpers (100 lines)
```

---

## Part 1: gui/__init__.py

Let's start simple!

```python
"""GUI module for the SOC Steganography Detection Tool."""

from .main_window import launch_gui, SteganographyGUI
from .file_dialog import select_image_file, select_folder, save_file_dialog

__all__ = ['launch_gui', 'SteganographyGUI', 'select_image_file', 'select_folder', 'save_file_dialog']
```

**What this does:**

**Line 3:** Import from main_window
```python
from .main_window import launch_gui, SteganographyGUI
```
- `.main_window` - the dot means "from this package"
- Import the launch function and main class

**Line 4:** Import from file_dialog
```python
from .file_dialog import select_image_file, select_folder, save_file_dialog
```
- Import three file dialog functions

**Line 6:** Define public API
```python
__all__ = [...]
```
- Lists what gets exported when someone does `from gui import *`
- Best practice to explicitly define public interface

**Why this file?**
- Makes `gui` a proper Python package
- Provides clean import interface
- Example: `from gui import launch_gui` works cleanly

---

## Part 2: gui/file_dialog.py

File dialogs let users select files/folders. Let's understand them!

### Imports (Lines 1-8)

```python
"""
File Dialog Module for SOC Steganography Detection Tool.
Handles file and folder selection dialogs.
"""

import tkinter as tk
from tkinter import filedialog
import os
```

**Line 6:** Import tkinter
**Line 7:** Import filedialog submodule
- Provides `askopenfilename()`, `askdirectory()`, etc.
**Line 8:** For path operations

---

### select_image_file() Function (Lines 11-57)

```python
def select_image_file(initial_dir=None):
    """
    Opens a file dialog to select an image file.
    
    Args:
        initial_dir (str, optional): Initial directory to open. Defaults to current directory.
    
    Returns:
        str: Selected file path, or empty string if cancelled
    """
```

**Purpose:** Show "Open File" dialog for selecting an image

**Parameter:**
- `initial_dir` - where to start (e.g., last-used folder)

**Returns:**
- File path string, or `""` if user cancels

---

**Lines 22-24: Create Hidden Root**
```python
    # Create a temporary root window (hidden)
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
```

**Why create a root?**
- Tkinter dialogs need a parent window
- Even if we don't want a visible window, we need this

**Line 23: `root.withdraw()`**
- Hides the window (don't show empty window)

**Line 24: `-topmost`**
- Keeps dialog on top of other windows
- Prevents it from hiding behind other apps

---

**Lines 26-40: Get Supported Formats**
```python
    # Import config for supported formats
    try:
        from config import SUPPORTED_IMAGE_FORMATS
        filetypes = SUPPORTED_IMAGE_FORMATS
    except ImportError:
        # Fallback if config not available
        filetypes = [
            ("All supported images", "*.png *.jpg *.jpeg *.bmp"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("BMP files", "*.bmp"),
            ("All files", "*.*")
        ]
```

**Line 28-29:** Try to import from config
- Use the formats defined in config.py

**Line 30-39:** Fallback
- If import fails (e.g., file_dialog used standalone)
- Use hardcoded fallback formats

**Defensive programming!**
- Function works even if config.py is missing

---

**Lines 42-44: Set Initial Directory**
```python
    # Set initial directory
    if initial_dir is None:
        initial_dir = os.getcwd()
```
- If no directory specified, use current working directory
- `os.getcwd()` = get current working directory

---

**Lines 46-51: Open File Dialog**
```python
    # Open file dialog
    file_path = filedialog.askopenfilename(
        title="Select Image to Analyze",
        initialdir=initial_dir,
        filetypes=filetypes
    )
```

**This is the magic line!**

**`filedialog.askopenfilename()`:**
- Opens the standard system file picker
- **Blocks** until user selects or cancels
- Returns file path or empty string

**Parameters:**
- `title` - Dialog window title
- `initialdir` - Starting directory
- `filetypes` - File filter dropdown

**What it looks like to user:**
```
┌──────────────────────────────────────┐
│ Select Image to Analyze         [×] │
├──────────────────────────────────────┤
│ Look in: [Documents ▼]              │
├──────────────────────────────────────┤
│ 📁 Folder1                           │
│ 📁 Folder2                           │
│ 🖼️ photo1.png                        │
│ 🖼️ photo2.jpg                        │
├──────────────────────────────────────┤
│ File name: [                     ]   │
│ Files of type: [All supported ▼]    │
│           [Open]  [Cancel]           │
└──────────────────────────────────────┘
```

---

**Lines 53-54: Cleanup**
```python
    # Clean up temporary root
    root.destroy()
```
- Destroy the hidden root window
- Free up resources

**Line 56: Return Result**
```python
    return file_path
```
- Return the selected path (or empty string)

---

### select_folder() Function (Lines 60-81)

```python
def select_folder(initial_dir=None):
    """
    Opens a folder dialog for batch processing.
    
    Args:
        initial_dir (str, optional): Initial directory to open.
    
    Returns:
        str: Selected folder path, or empty string if cancelled
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    if initial_dir is None:
        initial_dir = os.getcwd()
    
    folder_path = filedialog.askdirectory(
        title="Select Folder for Batch Analysis",
        initialdir=initial_dir
    )
    
    root.destroy()
    
    return folder_path
```

**Almost identical to select_image_file()!**

**Key difference:**
```python
folder_path = filedialog.askdirectory(...)
```
- Uses `askdirectory()` instead of `askopenfilename()`
- Returns a folder, not a file
- No `filetypes` parameter (selecting folders, not files)

**Use case:**
- For future batch processing feature
- Select folder containing multiple images
- Analyze all images in folder

---

### save_file_dialog() Function (Lines 84-114)

```python
def save_file_dialog(default_name="report.txt", initial_dir=None):
    """
    Opens a save file dialog.
    
    Args:
        default_name (str): Default filename
        initial_dir (str, optional): Initial directory
    
    Returns:
        str: Selected save path, or empty string if cancelled
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    if initial_dir is None:
        initial_dir = os.getcwd()
    
    file_path = filedialog.asksaveasfilename(
        title="Save Report",
        initialdir=initial_dir,
        initialfile=default_name,
        defaultextension=".txt",
        filetypes=[
            ("Text files", "*.txt"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
    )
    
    root.destroy()
    
    return file_path
```

**Similar pattern, but for saving:**

**Line 103: `asksaveasfilename()`**
- "Save As" dialog instead of "Open"
- User picks where to save

**New parameters:**

**`initialfile`** - Suggested filename
```python
initialfile=default_name
```
- Pre-fills the filename box
- User can change it

**`defaultextension`** - Auto-add extension
```python
defaultextension=".txt"
```
- If user types "report", saves as "report.txt"
- Convenience feature

**Use case:**
- Future feature: save reports to custom location
- Currently we auto-save CSV to logs folder

---

## Part 3: gui/main_window.py - The Main Show

This is the big file! Let's break it down systematically.

### Imports (Lines 1-19)

```python
"""
Main Window Module for SOC Steganography Detection Tool.
Implements the primary Tkinter GUI interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
from datetime import datetime

# Import project modules
from core.image_stego_engine import analyze_image
from reporting.logger import log_analysis_to_csv
from gui.file_dialog import select_image_file
from config import (
    APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, COLOR_PRIMARY,
    COLOR_SUCCESS, COLOR_DANGER, HASH_DISPLAY_LENGTH
)
```

**Line 6:** Import tkinter as tk
**Line 7:** Import submodules
- `ttk` - Themed widgets (modern look)
- `messagebox` - Dialog boxes (OK, Cancel, Yes/No)
- `scrolledtext` - Text box with built-in scrollbar

**Line 8-10:** Standard library imports

**Line 13:** Import our detection engine
**Line 14:** Import CSV logging function
**Line 15:** Import file dialog helper

**Lines 16-20:** Import configuration constants
- All the values we defined in config.py
- Window size, colors, etc.

---

### The SteganographyGUI Class (Line 22)

```python
class SteganographyGUI:
    """Main GUI application for SOC Steganography Detection Tool."""
```

**What is a class?**
- A blueprint for creating objects
- Bundles data (variables) and functions (methods) together
- Object-oriented programming concept

**Why use a class?**
- Organize related code
- Maintain state (current image, analysis results)
- Cleaner than global variables

**Analogy:** 
- Class = Blueprint for a car
- Object = An actual car built from that blueprint

```python
# Create a GUI object (instantiate the class)
app = SteganographyGUI(root)

# The object has its own data:
app.current_image_path = "photo.png"
app.current_analysis_result = {...}

# The object has methods (functions):
app.select_image()
app.analyze_current_image()
```

---

### __init__() Method - Constructor (Lines 24-44)

```python
    def __init__(self, root):
        """
        Initialize the main GUI window.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Application state
        self.current_image_path = None
        self.current_analysis_result = None
        
        # Initialize GUI components
        self.create_menu_bar()
        self.create_main_interface()
        self.create_status_bar()
        
        # Initial status
        self.update_status("Ready - Select an image to begin analysis")
```

**What is `__init__`?**
- Special method called **constructor**
- Runs automatically when object is created
- Initializes the object's state

**Line 24: Method signature**
```python
def __init__(self, root):
```
- `self` - reference to the object itself (required in all methods)
- `root` - the Tkinter root window (passed in)

**Line 31: Store root reference**
```python
self.root = root
```
- `self.root` - instance variable (belongs to this object)
- Stores root so other methods can access it

**Line 32: Set window title**
```python
self.root.title(f"{APP_NAME} v{APP_VERSION}")
```
- Sets title bar text
- Example: "SOC Steganography Detection Tool v1.0.0"

**Line 33: Set window size**
```python
self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
```
- `geometry()` takes string: "WIDTHxHEIGHT"
- Example: "900x700"

**Line 34: Set minimum size**
```python
self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
```
- Users can't resize smaller than this
- Prevents UI elements from being cut off

**Lines 36-38: Initialize state**
```python
self.current_image_path = None
self.current_analysis_result = None
```
- Instance variables to track application state
- `None` means "no value yet"

**Lines 40-43: Build GUI components**
```python
self.create_menu_bar()
self.create_main_interface()
self.create_status_bar()
```
- Calls three methods to build the GUI
- Each method adds a piece of the interface

**Line 46: Set initial status**
```python
self.update_status("Ready - Select an image to begin analysis")
```
- Updates status bar with welcome message

---

This is getting quite long! Let me continue in a follow-up file since Part 5 is substantial. Should I create Part 5B to continue the GUI explanation?
