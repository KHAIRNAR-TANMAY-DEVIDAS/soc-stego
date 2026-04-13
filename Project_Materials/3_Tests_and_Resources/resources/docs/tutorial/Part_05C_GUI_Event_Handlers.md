# Part 5C: GUI (Event Handlers & Results Display)

## Continuing from Part 5B...

Now let's cover the methods that **respond to user actions** and **display results**!

---

## The select_image() Method (Lines 186-202)

```python
    def select_image(self):
        """Handle image file selection."""
        image_path = select_image_file()
        
        if not image_path:
            return
        
        self.current_image_path = image_path
        self.file_path_var.set(image_path)
        
        # Enable the analyze button
        self.analyze_button.config(state=tk.NORMAL)
        
        # Clear previous results
        self.display_welcome_message()
        
        # Update status
        self.update_status("Image selected. Ready to analyze.")
```

**Purpose:** Called when user clicks "Select Image" button or File → Select Image

**Line 189: Open file dialog**
```python
image_path = select_image_file()
```
- Calls the function from `file_dialog.py` we explained in Part 5
- Returns selected path or `None` if cancelled

**Lines 191-192: Check if cancelled**
```python
if not image_path:
    return
```
- If user clicked Cancel, `image_path` is `None` or empty string
- Exit method early

**Line 194: Store path**
```python
self.current_image_path = image_path
```
- Save to instance variable
- Other methods need this path for analysis

**Line 195: Update UI display**
```python
self.file_path_var.set(image_path)
```
- Remember StringVar? Updating it updates the label automatically!
- Label now shows full file path

**Line 198: Enable analyze button**
```python
self.analyze_button.config(state=tk.NORMAL)
```
- `config()` changes widget properties
- `state=tk.NORMAL` - enable button (no longer grayed out)

**Line 201: Reset results area**
```python
self.display_welcome_message()
```
- Clear any previous analysis results
- Show welcome message again

**Line 204: Update status bar**
```python
self.update_status("Image selected. Ready to analyze.")
```
- Calls method to update status bar text

**Flow:**
```
User clicks button
    → Dialog opens
    → User selects image.png
    → Path stored
    → UI updates
    → Analyze button enabled
    → Status updated
```

---

## The analyze_current_image() Method (Lines 204-257)

This is the **MAIN ANALYSIS METHOD** - where all the magic happens!

```python
    def analyze_current_image(self):
        """Perform analysis on the currently selected image."""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please select an image file first.")
            return
```

**Line 207-209: Validation**
- Check if image is actually selected
- Show warning dialog if not
- Exit early

### Start Analysis

```python
        # Get optional XOR key
        xor_key = self.xor_key_var.get().strip()
        xor_key = xor_key if xor_key else None
        
        # Update status
        self.update_status("Analyzing image...")
        self.root.update()  # Force UI update
```

**Line 212-213: Get XOR key**
```python
xor_key = self.xor_key_var.get().strip()
```
- `.get()` - get value from StringVar
- `.strip()` - remove whitespace from edges

**Line 214: Convert empty to None**
```python
xor_key = xor_key if xor_key else None
```
- If string is empty, make it `None`
- Ternary operator: `value if condition else other_value`

**Line 217-218: Update UI**
```python
self.update_status("Analyzing image...")
self.root.update()
```
- Update status bar
- `self.root.update()` - **force UI to refresh NOW**
  - Normally UI updates after method finishes
  - This makes status appear immediately

### Call Detection Engine

```python
        try:
            # Call the detection engine
            result = analyze_image(
                self.current_image_path,
                xor_key=xor_key,
                show_progress=False  # GUI mode, no console output
            )
```

**Line 220: Try block**
- Wrap in try/except to catch errors safely

**Line 222-226: Call analysis function**
```python
result = analyze_image(
    self.current_image_path,
    xor_key=xor_key,
    show_progress=False
)
```
- This is the `analyze_image()` function from `image_stego_engine.py`!
- Pass image path and XOR key
- `show_progress=False` - don't print to console (we're in GUI mode)
- Returns dictionary with results

### Store Results

```python
            if result:
                self.analysis_results = result
                self.display_analysis_results(result)
                
                # Enable export options
                self.export_button.config(state=tk.NORMAL)
                self.file_menu.entryconfig("Export to CSV...", state=tk.NORMAL)
                
                # Update status based on detection
                if result["steganography_detected"]:
                    self.update_status("Analysis complete: HIDDEN DATA DETECTED!")
                else:
                    self.update_status("Analysis complete: No hidden data detected.")
```

**Line 228: Check if results returned**
```python
if result:
```

**Line 229: Store results**
```python
self.analysis_results = result
```
- Save to instance variable
- Needed for CSV export later

**Line 230: Display results**
```python
self.display_analysis_results(result)
```
- Call method to show results in GUI
- We'll cover this method next!

**Lines 233-234: Enable export options**
```python
self.export_button.config(state=tk.NORMAL)
self.file_menu.entryconfig("Export to CSV...", state=tk.NORMAL)
```
- Enable the Export button
- Enable File → Export menu item
- `.entryconfig()` - configure menu entry by label

**Lines 237-241: Update status based on result**
```python
if result["steganography_detected"]:
    self.update_status("Analysis complete: HIDDEN DATA DETECTED!")
else:
    self.update_status("Analysis complete: No hidden data detected.")
```
- Check the detection flag in results
- Show appropriate message

### Error Handling

```python
            else:
                messagebox.showerror("Analysis Error", "Failed to analyze image.")
                self.update_status("Analysis failed.")
                
        except Exception as e:
            error_message = f"Error during analysis: {str(e)}"
            messagebox.showerror("Analysis Error", error_message)
            self.update_status("Analysis error occurred.")
            
            # Log the error
            import traceback
            print(f"GUI Analysis Error: {error_message}")
            traceback.print_exc()
```

**Lines 243-245: If result is None**
- Show error dialog
- Update status

**Lines 247-256: If exception occurs**
- Catch any Python error
- Show error message to user
- Update status bar
- Print error details to console (for debugging)
- `traceback.print_exc()` - print full error details

**Complete flow:**
```
User clicks "Analyze Image"
    → Validate image selected
    → Get XOR key (if any)
    → Update status to "Analyzing..."
    → Call detection engine
    → Wait for results
    → Store results
    → Display results in GUI
    → Enable export options
    → Update status to "Complete!"
```

---

## The display_analysis_results() Method (Lines 259-402)

This is a **BIG METHOD** that formats and displays all analysis results beautifully!

```python
    def display_analysis_results(self, result):
        """Display comprehensive analysis results."""
        # Clear existing widgets
        for widget in self.results_container.winfo_children():
            widget.destroy()
```

**Line 262-264: Clear previous results**
- Just like in welcome message
- Remove all existing widgets

### Main Results Frame

```python
        # Create main results frame
        main_frame = ttk.Frame(self.results_container)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
```

**Line 267-268: Container**
- Frame to hold all result widgets

### Detection Summary Header

```python
        # === DETECTION SUMMARY HEADER ===
        summary_frame = ttk.Frame(main_frame, relief=tk.RAISED, borderwidth=2)
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Background color based on detection
        if result["steganography_detected"]:
            bg_color = "#ffcccc"  # Light red
            header_text = "⚠ STEGANOGRAPHY DETECTED"
            color_fg = "red"
        else:
            bg_color = "#ccffcc"  # Light green
            header_text = "✓ NO HIDDEN DATA DETECTED"
            color_fg = "green"
```

**Lines 271-273: Create summary frame**
```python
summary_frame = ttk.Frame(main_frame, relief=tk.RAISED, borderwidth=2)
```
- `relief=tk.RAISED` - looks raised/3D
- `borderwidth=2` - 2-pixel border

**Lines 276-283: Color based on detection**
- If hidden data found → red background, warning symbol
- If clean → green background, checkmark
- Emoji symbols: `⚠` (warning), `✓` (checkmark)

**Visual result:**
```
┌────────────────────────────────┐
│ ⚠ STEGANOGRAPHY DETECTED       │ ← Red background
└────────────────────────────────┘

OR

┌────────────────────────────────┐
│ ✓ NO HIDDEN DATA DETECTED      │ ← Green background
└────────────────────────────────┘
```

**Lines 285-291: Display header**
```python
        # Note: ttk widgets don't support bg parameter in all themes
        # Using Label instead of ttk.Label for better color support
        header_label = tk.Label(summary_frame, text=header_text,
                               font=("Arial", 12, "bold"),
                               bg=bg_color, fg=color_fg, pady=10)
        header_label.pack(fill=tk.X)
```
- Using `tk.Label` (not `ttk.Label`) because ttk doesn't support custom colors well
- `bg=bg_color` - background color
- `fg=color_fg` - foreground (text) color

### File Information Section

```python
        # === FILE INFORMATION SECTION ===
        file_info_frame = ttk.LabelFrame(main_frame, text="File Information", padding=10)
        file_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        file_info = [
            ("Filename", result["filename"]),
            ("File Path", result["filepath"]),
            ("File Size", f"{result['filesize_bytes']:,} bytes"),
            ("Image Dimensions", f"{result['image_dimensions']}"),
            ("Image Format", result["image_format"]),
            ("SHA-256 Hash", result["file_hash"]),
        ]
        
        for label, value in file_info:
            row = ttk.Frame(file_info_frame)
            row.pack(fill=tk.X, pady=2)
            
            ttk.Label(row, text=f"{label}:", font=("Arial", 9, "bold"),
                     width=20, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row, text=value, font=("Consolas", 9),
                     foreground="navy").pack(side=tk.LEFT, padx=(10, 0))
```

**Lines 296-304: Build info list**
```python
file_info = [
    ("Filename", result["filename"]),
    ("File Path", result["filepath"]),
    ...
]
```
- List of tuples: `(label, value)`
- Gets values from result dictionary
- `f"{result['filesize_bytes']:,} bytes"` - format with commas (e.g., "123,456 bytes")

**Lines 306-313: Loop through and display**
```python
for label, value in file_info:
```
- For each info item...

**Lines 307-308: Create row frame**
```python
row = ttk.Frame(file_info_frame)
row.pack(fill=tk.X, pady=2)
```

**Lines 310-311: Label part**
```python
ttk.Label(row, text=f"{label}:", font=("Arial", 9, "bold"),
         width=20, anchor=tk.W).pack(side=tk.LEFT)
```
- Bold label
- `width=20` - 20 characters wide (aligns all labels)
- `anchor=tk.W` - left-align

**Lines 312-313: Value part**
```python
ttk.Label(row, text=value, font=("Consolas", 9),
         foreground="navy").pack(side=tk.LEFT, padx=(10, 0))
```
- Monospace font (Consolas)
- Navy blue color
- 10 pixels padding on left

**Visual:**
```
┌─ File Information ──────────────────────────┐
│ Filename:           image.png               │
│ File Path:          C:\Users\...\image.png  │
│ File Size:          123,456 bytes           │
│ Image Dimensions:   800x600                 │
│ Image Format:       PNG                     │
│ SHA-256 Hash:       a3f5c9...               │
└─────────────────────────────────────────────┘
```

### Detection Details Section

```python
        # === DETECTION DETAILS SECTION ===
        detection_frame = ttk.LabelFrame(main_frame, text="Detection Details", padding=10)
        detection_frame.pack(fill=tk.X, pady=(0, 10))
        
        detection_info = [
            ("LSB Data Length", f"{result['lsb_data_length']} bytes"),
            ("EOF Marker Found", "YES" if result["eof_marker_present"] else "NO"),
            ("Encryption Used", "YES (XOR)" if result["encryption_used"] else "NO"),
            ("Decryption Successful", "YES" if result["decryption_successful"] else "N/A"),
        ]
        
        for label, value in detection_info:
            row = ttk.Frame(detection_frame)
            row.pack(fill=tk.X, pady=2)
            
            ttk.Label(row, text=f"{label}:", font=("Arial", 9, "bold"),
                     width=25, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row, text=value, font=("Arial", 9),
                     foreground="darkgreen" if "YES" in str(value) else "darkred").pack(side=tk.LEFT, padx=(10, 0))
```

**Same pattern as file info:**
- Build list of detection details
- Loop through and display
- But: Color "YES" green, "NO" red!

**Lines 335-336: Conditional coloring**
```python
foreground="darkgreen" if "YES" in str(value) else "darkred"
```
- If value contains "YES" → dark green
- Otherwise → dark red

### Extracted Message Section (if present)

```python
        # === EXTRACTED MESSAGE SECTION ===
        if result["steganography_detected"] and result["extracted_text"]:
            message_frame = ttk.LabelFrame(main_frame, text="Extracted Hidden Message", padding=10)
            message_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Use ScrolledText for potentially long messages
            message_box = scrolledtext.ScrolledText(message_frame, height=8, wrap=tk.WORD,
                                                   font=("Consolas", 9),
                                                   bg="#ffffcc", fg="black")
            message_box.pack(fill=tk.BOTH, expand=True)
            message_box.insert("1.0", result["extracted_text"])
            message_box.config(state=tk.DISABLED)  # Read-only
```

**Line 339: Check if message exists**
```python
if result["steganography_detected"] and result["extracted_text"]:
```
- Only show if data was detected AND text extracted

**Lines 344-346: ScrolledText widget**
```python
message_box = scrolledtext.ScrolledText(message_frame, height=8, wrap=tk.WORD,
                                       font=("Consolas", 9),
                                       bg="#ffffcc", fg="black")
```
- `ScrolledText` - multi-line text box with scrollbar
- `height=8` - 8 lines tall
- `wrap=tk.WORD` - wrap at word boundaries (not middle of word)
- `bg="#ffffcc"` - pale yellow background (like sticky note)

**Line 348: Insert text**
```python
message_box.insert("1.0", result["extracted_text"])
```
- `"1.0"` - line 1, character 0 (beginning)
- Insert the extracted message

**Line 349: Make read-only**
```python
message_box.config(state=tk.DISABLED)
```
- User can't edit it
- Only for viewing

### Validation Layers Section

```python
        # === VALIDATION LAYERS SECTION ===
        validation_frame = ttk.LabelFrame(main_frame, text="7-Layer Validation Results", padding=10)
        validation_frame.pack(fill=tk.X, pady=(0, 10))
        
        validation_results = result.get("validation_results", {})
        
        for i in range(1, 8):
            layer_key = f"layer{i}_passed"
            layer_name_key = f"layer{i}_name"
            
            passed = validation_results.get(layer_key, False)
            layer_name = validation_results.get(layer_name_key, f"Layer {i}")
            
            row = ttk.Frame(validation_frame)
            row.pack(fill=tk.X, pady=1)
            
            status_symbol = "✓" if passed else "✗"
            status_color = "green" if passed else "red"
            
            ttk.Label(row, text=status_symbol, font=("Arial", 10, "bold"),
                     foreground=status_color, width=3).pack(side=tk.LEFT)
            ttk.Label(row, text=layer_name, font=("Arial", 9)).pack(side=tk.LEFT)
```

**Line 356: Get validation results**
```python
validation_results = result.get("validation_results", {})
```
- `.get()` with default value `{}`
- If key doesn't exist, returns empty dict

**Line 358: Loop through 7 layers**
```python
for i in range(1, 8):
```
- Layers 1 through 7

**Lines 359-363: Get layer data**
```python
layer_key = f"layer{i}_passed"              # "layer1_passed"
layer_name_key = f"layer{i}_name"           # "layer1_name"

passed = validation_results.get(layer_key, False)
layer_name = validation_results.get(layer_name_key, f"Layer {i}")
```
- Build key names dynamically
- Get pass/fail status and layer name

**Lines 369-370: Status symbol and color**
```python
status_symbol = "✓" if passed else "✗"
status_color = "green" if passed else "red"
```
- Passed → green checkmark
- Failed → red X

**Visual:**
```
┌─ 7-Layer Validation Results ───┐
│ ✓ EOF Marker Present          │
│ ✓ Minimum Length Check        │
│ ✓ Printable Characters        │
│ ✓ Entropy Analysis            │
│ ✓ Null Byte Check              │
│ ✓ Pattern Recognition         │
│ ✓ Consistency Check            │
└────────────────────────────────┘
```

### Scroll to Top

```python
        # Scroll to top
        self.results_canvas.yview_moveto(0)
```

**Line 379: Reset scroll position**
- `yview_moveto(0)` - scroll to top (position 0)
- Prevents being scrolled down from previous results

---

## The export_to_csv() Method (Lines 404-452)

```python
    def export_to_csv(self):
        """Export current analysis results to CSV file."""
        if not self.analysis_results:
            messagebox.showwarning("No Results", "No analysis results to export.")
            return
```

**Purpose:** Save results to a CSV file

**Line 407-409: Validation**
- Check if results exist
- Show warning if not

### Get Save Location

```python
        # Get save file path
        csv_path = save_file_dialog()
        
        if not csv_path:
            return  # User cancelled
```

**Line 412: Call save dialog**
- Uses `save_file_dialog()` from `file_dialog.py`

**Line 414-415: Check if cancelled**

### Write to CSV

```python
        try:
            result = self.analysis_results
            
            # Prepare validation summary
            validation = result.get("validation_results", {})
            layers_passed = sum(1 for k, v in validation.items() 
                              if k.startswith("layer") and k.endswith("_passed") and v)
            
            # Write to CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
                writer.writeheader()
                
                row = {
                    "timestamp": datetime.now().isoformat(),
                    "filename": result["filename"],
                    "filepath": result["filepath"],
                    "filesize_bytes": result["filesize_bytes"],
                    "file_hash": result["file_hash"],
                    "image_format": result["image_format"],
                    "image_dimensions": result["image_dimensions"],
                    "steganography_detected": result["steganography_detected"],
                    "eof_marker_present": result["eof_marker_present"],
                    "lsb_data_length": result["lsb_data_length"],
                    "encryption_used": result["encryption_used"],
                    "decryption_successful": result["decryption_successful"],
                    "extracted_text_preview": result["extracted_text"][:200] if result["extracted_text"] else "",
                    "validation_layers_passed": layers_passed,
                }
                
                writer.writerow(row)
```

**Line 420: Count passed layers**
```python
layers_passed = sum(1 for k, v in validation.items()
                  if k.startswith("layer") and k.endswith("_passed") and v)
```
- **List comprehension** with sum
- For each key-value pair in validation dict:
  - Check if key starts with "layer"
  - Check if key ends with "_passed"
  - Check if value is True
  - Sum up the count

**Line 423: Open file for writing**
```python
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
```
- `'w'` - write mode
- `newline=''` - required for CSV on Windows
- `encoding='utf-8'` - support all characters

**Line 424-425: Create CSV writer**
```python
writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
writer.writeheader()
```
- `DictWriter` - writes dictionaries as CSV rows
- `fieldnames=CSV_FIELDNAMES` - column names from config
- `writeheader()` - write column names as first row

**Lines 427-443: Build row dictionary**
- Each key matches a CSV column name
- Values from analysis results
- `[:200]` - limit text preview to 200 characters

**Line 445: Write row**
```python
writer.writerow(row)
```

### Success Message

```python
            messagebox.showinfo("Export Successful",
                              f"Results exported to:\n{csv_path}")
            self.update_status(f"Results exported to {os.path.basename(csv_path)}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
            self.update_status("Export failed.")
```

**Lines 447-449: Success**
- Show info dialog with file path
- Update status bar

**Lines 451-453: Error handling**
- Catch exceptions
- Show error dialog

---

## The clear_results() Method (Lines 454-461)

```python
    def clear_results(self):
        """Clear current results and reset the interface."""
        self.analysis_results = None
        self.display_welcome_message()
        self.export_button.config(state=tk.DISABLED)
        self.file_menu.entryconfig("Export to CSV...", state=tk.DISABLED)
        self.update_status("Results cleared.")
```

**Purpose:** Reset everything

**Line 457: Clear stored results**
```python
self.analysis_results = None
```

**Line 458: Show welcome screen**
```python
self.display_welcome_message()
```

**Lines 459-460: Disable export options**
- Disable export button
- Disable menu item

**Line 461: Update status**

---

## Utility Methods

### show_about() - Lines 463-471

```python
    def show_about(self):
        """Show About dialog."""
        about_text = f"""{APP_NAME}
Version: {APP_VERSION}

A steganography detection tool for SOC analysts.
Detects hidden data in images using LSB analysis.

© 2025"""
        messagebox.showinfo("About", about_text)
```

**Purpose:** Show About dialog from Help menu

**Multi-line string** with app info

### update_status() - Lines 473-477

```python
    def update_status(self, message):
        """Update the status bar with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"[{timestamp}] {message}")
```

**Purpose:** Update status bar with timestamped message

**Line 476: Format time**
```python
timestamp = datetime.now().strftime("%H:%M:%S")
```
- Current time as HH:MM:SS

**Line 477: Set status**
```python
self.status_var.set(f"[{timestamp}] {message}")
```
- Example: `"[14:35:22] Analysis complete."`

### exit_application() - Lines 479-481

```python
    def exit_application(self):
        """Handle application exit."""
        self.root.destroy()
```

**Purpose:** Close the application

**Line 481: Destroy window**
```python
self.root.destroy()
```
- Closes window and exits program

---

## Quick Review Questions

1. **What does StringVar do?**
   - Creates a variable that automatically updates UI widgets when changed

2. **Why use try/except in analyze_current_image()?**
   - To catch errors safely and show user-friendly error messages

3. **What makes the results area scrollable?**
   - Canvas + Scrollbar combination with special binding

4. **How does the GUI show different colors for DETECTED vs CLEAN?**
   - Checks `result["steganography_detected"]` and sets background color accordingly

5. **Why is self.root.update() called during analysis?**
   - Forces UI to refresh immediately so user sees "Analyzing..." status

6. **What does state=tk.DISABLED do?**
   - Grays out a widget so user can't interact with it

7. **How are validation results displayed?**
   - Loop through layers 1-7, show green ✓ for pass, red ✗ for fail

8. **What happens when export button is clicked?**
   - Opens save dialog → writes results to CSV → shows success message

---

## The Complete User Journey

Let's trace a complete analysis from start to finish:

```
1. User launches GUI
   → __init__() creates all widgets
   → Welcome message displayed
   → Analyze and Export buttons disabled

2. User clicks "Select Image"
   → select_image() called
   → File dialog opens
   → User chooses image.png
   → Path stored and displayed
   → Analyze button enabled

3. User (optionally) enters XOR key
   → Types into Entry widget
   → Stored in xor_key_var

4. User clicks "Analyze Image"
   → analyze_current_image() called
   → Status updated to "Analyzing..."
   → Detection engine called
   → Results returned
   → display_analysis_results() called
   → Beautiful formatted results shown
   → Export options enabled
   → Status shows "Complete!"

5. User reviews results
   → Scrolls through results
   → Sees file info, detection details, message, validation

6. User clicks "Export to CSV"
   → export_to_csv() called
   → Save dialog opens
   → User chooses location
   → CSV file written
   → Success message shown

7. User clicks "Clear"
   → clear_results() called
   → Back to welcome screen
   → Ready for next analysis
```

---

**Previous:** [Part 5B - GUI (Main Window Construction)](Part_05B_GUI_Continued.md)
**Next:** [Part 6 - Reporting System](Part_06_Reporting_System.md)

---

*You've now seen the complete GUI implementation! Event handlers connect user actions to backend functions, and result display formats complex data into a beautiful interface. This is how desktop applications work! 🎉*
