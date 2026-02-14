# SOC Steganography Detection Tool - Phased Development Plan

## Current State Analysis
Your existing `image_stego_engine.py` contains:
- ✅ LSB encode/decode functionality with EOF marker detection
- ✅ XOR encryption/decryption
- ✅ SHA-256 file hashing
- ✅ Basic metadata extraction (dimensions, format, capacity)
- ✅ `analyze_image()` wrapper function (returns structured dict)
- ✅ Interactive CLI menu

**Status**: Core engine is complete and functional. Ready for GUI and logging integration.

---

## Phase 1: Project Structure & Foundation
**Goal**: Organize codebase into modular SOC-ready structure

**Tasks**:
1. Create folder structure:
   ```
   /core               → image_stego_engine.py (existing, no changes)
   /gui                → Tkinter interface modules
   /reporting          → CSV logging and report generation
   /config             → Configuration files
   /tests              → Test images and validation scripts
   /logs               → Output directory for CSV logs
   ```

2. Create `requirements.txt`:
   - Pillow
   - (tkinter is built-in)

3. Create `config.py`:
   - Default paths for logs
   - CSV field definitions
   - Application constants (window size, themes, etc.)

4. Create `main.py`:
   - Entry point that launches GUI
   - Imports from core, gui, and reporting modules

**Verification**:
- [ ] All folders created
- [ ] Can import `core.image_stego_engine` from other modules
- [ ] `python main.py` runs without import errors
- [ ] Project structure is clean and navigable

**Files Modified/Created**:
- Move: `image_stego_engine.py` → `core/image_stego_engine.py`
- Create: `requirements.txt`, `config.py`, `main.py`
- Create: Empty `__init__.py` files in each package directory

---

## Phase 2: CSV Logging & Reporting Module
**Goal**: Build SOC-grade logging for incident tracking and audit trails

**Tasks**:
1. Create `reporting/logger.py`:
   - `log_analysis_to_csv(analysis_result, csv_path)` function
   - Uses existing `analyze_image()` output dict
   - Columns: timestamp, file_path, file_hash, file_size, has_hidden_data, hidden_message_preview, format, dimensions, status
   - Append mode (don't overwrite existing logs)
   - Auto-create CSV with headers if doesn't exist

2. Create `reporting/report_generator.py`:
   - `generate_summary_report(csv_path)` → reads CSV, returns stats
   - Count total scans, suspicious images, clean images
   - List of all detected hidden messages

3. Extend `analyze_image()` wrapper (optional enhancement):
   - Add `log_to_csv=True` parameter
   - Automatically log results if enabled

**Verification**:
- [ ] Run analysis on 3 test images (1 clean, 2 with hidden data)
- [ ] CSV file created in `/logs` with correct structure
- [ ] All fields populated correctly
- [ ] Summary report shows accurate counts
- [ ] Re-running appends to CSV without duplication of headers

**Files Created**:
- `reporting/logger.py`
- `reporting/report_generator.py`
- `reporting/__init__.py`

---

## Phase 3: Basic Tkinter GUI Framework
**Goal**: Replace CLI with desktop GUI for SOC analyst usability

**Tasks**:
1. Create `gui/main_window.py`:
   - Main application window (800x600 recommended)
   - Title: "SOC Steganography Detection Tool"
   - Menu bar: File → Exit
   - Top section: "Single Image Analysis" frame
   - Button: "Select Image"
   - Button: "Analyze"
   - Text widget: Display analysis results (scrollable)

2. Create `gui/file_dialog.py`:
   - `select_image_file()` → returns file path
   - Filter: PNG, JPG, BMP only
   - Uses `tkinter.filedialog.askopenfilename()`

3. Wire up functionality:
   - "Select Image" → updates displayed path
   - "Analyze" → calls `analyze_image()`, displays results in text widget
   - Show: file hash, dimensions, hidden data status, extracted message

4. Add optional XOR key field:
   - Label + Entry widget for decryption key
   - Pass to `analyze_image(decode_key=...)`

**Verification**:
- [ ] GUI launches without errors
- [ ] Can select image via file dialog
- [ ] Analysis results display in text area
- [ ] XOR key field works for encrypted messages
- [ ] Window is resizable and usable

**Files Created**:
- `gui/main_window.py`
- `gui/file_dialog.py`
- `gui/__init__.py`

**Files Modified**:
- `main.py` → launch GUI instead of CLI

---

## Phase 4: Enhanced GUI - Analysis Dashboard
**Goal**: Professional SOC-style results panel with structured data display

**Tasks**:
1. Replace text widget with structured result panel:
   - Use `ttk.Frame` with `ttk.Label` widgets in grid layout
   - Sections:
     - **File Info**: Name, Hash (first 16 chars), Size
     - **Image Metadata**: Format, Dimensions, Mode, Max Capacity
     - **Detection Results**: Status indicator (🟢 Clean / 🔴 Hidden Data), Message preview
   - Use color coding: green for clean, red/yellow for suspicious

2. Add "Export to CSV" button:
   - Calls `log_analysis_to_csv()` with current result
   - Shows success/failure message via `messagebox`

3. Add status bar at bottom:
   - Shows last action ("Image analyzed", "Logged to CSV", etc.)
   - Timestamp display

4. Improve UX:
   - Disable "Analyze" button until image selected
   - Show loading indicator during analysis
   - Clear previous results when new image selected

**Verification**:
- [ ] Results display in structured, readable format
- [ ] Color indicators work correctly
- [ ] Export to CSV button logs data
- [ ] Status bar updates appropriately
- [ ] GUI feels responsive and professional

**Files Modified**:
- `gui/main_window.py` (major enhancement)

**Files Created**:
- `gui/results_panel.py` (optional: separate results display logic)

---

## Phase 5: Batch Processing & Automation
**Goal**: SOC-grade capability to scan multiple images in one operation

**Tasks**:
1. Add "Batch Analysis" tab/frame to GUI:
   - Button: "Select Folder"
   - Button: "Analyze All Images"
   - Listbox: Shows all images found in folder
   - Text widget: Progress log ("Analyzing image 1/10...")
   - Progress bar (`ttk.Progressbar`)

2. Create `core/batch_processor.py`:
   - `batch_analyze_folder(folder_path, decode_key=None)` function
   - Recursively finds all image files
   - Calls `analyze_image()` on each
   - Returns list of results
   - Automatically logs all to CSV

3. Wire up batch processing:
   - "Select Folder" → folder dialog, populate listbox with images
   - "Analyze All" → runs batch processor, updates progress bar
   - All results auto-logged to CSV with timestamp-based filename

4. Add batch summary pop-up:
   - Total scanned, suspicious found, time taken
   - Button to open CSV log location

**Verification**:
- [ ] Batch analysis scans all images in test folder
- [ ] Progress bar updates smoothly
- [ ] CSV contains all batch results
- [ ] Summary shows accurate statistics
- [ ] Can handle 20+ images without freezing GUI

**Files Created**:
- `core/batch_processor.py`
- `gui/batch_tab.py` (or add to `main_window.py`)

---

## Phase 6: Final Integration, Testing & Documentation
**Goal**: Ensure tool is production-ready for SOC demonstration

**Tasks**:
1. Create test suite:
   - `/tests/test_analysis.py` → pytest scripts (optional, but recommended)
   - Manual test checklist for each phase

2. Error handling audit:
   - Add try-catch blocks in GUI callbacks
   - Show user-friendly error messages via `messagebox.showerror()`
   - Handle corrupted images, permission errors

3. Documentation:
   - `README.md`:
     - Project overview, features, installation
     - Usage guide with screenshots (if possible)
     - Technical architecture diagram
   - `USAGE_GUIDE.md`:
     - Step-by-step analyst workflow
     - How to interpret results
     - CSV log format explanation

4. Code cleanup:
   - Add docstrings to all new functions
   - Remove any debug print statements
   - Ensure consistent naming conventions

5. Final testing scenarios:
   - Clean image analysis
   - Hidden message with XOR encryption
   - Wrong decryption key handling
   - Batch processing large folder
   - CSV export and re-import

**Verification**:
- [ ] All test scenarios pass
- [ ] No unhandled exceptions in GUI
- [ ] Documentation accurate and complete
- [ ] Tool ready for project demonstration
- [ ] Code is explainable and well-documented

**Files Created**:
- `README.md`
- `USAGE_GUIDE.md`
- `tests/test_analysis.py` (if using pytest)
- `tests/TEST_CHECKLIST.md`

---

## Testing Protocol Between Phases

After completing each phase:
1. **Functionality Test**: Does the new feature work as designed?
2. **Integration Test**: Does it work with existing code?
3. **Error Test**: Try to break it (wrong files, empty inputs, etc.)
4. **User Review**: Is it intuitive and SOC-appropriate?

Only proceed to next phase when current phase passes all tests.

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Don't rewrite `image_stego_engine.py` | Existing LSB logic is solid; wrapping is safer and respects working code |
| Use `analyze_image()` as bridge | Already returns structured dict perfect for GUI display and CSV logging |
| Separate reporting module | CSV logging is independent concern; easier to test and extend |
| Phase-by-phase GUI | Build simple first, then enhance; avoids complex debugging |
| Batch processing last | Requires stable single-image analysis first |

---

## Out of Scope (Not in This Prototype)

- Machine learning detection models
- Cloud API integration
- Audio/video steganography
- Network monitoring features
- User authentication system
- Database storage (CSV is sufficient for prototype)

---

**Next Steps**: Start with Phase 1 (Project Structure). Once Phase 1 is tested and verified, we'll move to Phase 2.
