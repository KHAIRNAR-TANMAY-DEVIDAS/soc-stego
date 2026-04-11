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
from reporting.logger import log_analysis_to_csv, log_batch_results
from gui.file_dialog import select_image_file, select_folder
from core.vt_client import query_virustotal_hash, hash_payload_string
from config import (
    APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, COLOR_PRIMARY,
    COLOR_SUCCESS, COLOR_DANGER, HASH_DISPLAY_LENGTH,
    IMAGE_EXTENSIONS, BATCH_MAX_WORKERS
)
import concurrent.futures


class SteganographyGUI:
    """Main GUI application for SOC Steganography Detection Tool."""
    
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
        
        # Batch Application state
        self.batch_folder_path = None
        self.batch_results = []
        self.is_batch_running = False
        
        # Initialize GUI components
        self.create_menu_bar()
        self.create_main_interface()
        self.create_status_bar()
        
        # Initial status
        self.update_status("Ready - Select an image to begin analysis")
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Image...", command=self.select_image)
        file_menu.add_separator()
        file_menu.add_command(label="Export to CSV...", command=self.export_to_csv, state=tk.DISABLED)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Store menu references for enabling/disabling
        self.file_menu = file_menu
    
    def create_main_interface(self):
        """Create the main interface components."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.single_tab = ttk.Frame(self.notebook)
        self.batch_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.single_tab, text="Single Image Analysis")
        self.notebook.add(self.batch_tab, text="Batch Directory Analysis")
        
        self.setup_single_analysis_tab()
        self.setup_batch_analysis_tab()

    def setup_single_analysis_tab(self):
        """Setup the Single Image Analysis tab."""
        analysis_frame = ttk.LabelFrame(self.single_tab, text="Single Image Analysis", padding="10")
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # File selection row
        file_frame = ttk.Frame(analysis_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="Selected Image:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.file_path_var = tk.StringVar(value="No image selected")
        file_path_label = ttk.Label(file_frame, textvariable=self.file_path_var, 
                                     foreground="gray", relief=tk.SUNKEN, padding=5)
        file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(file_frame, text="Select Image", command=self.select_image).pack(side=tk.LEFT)
        
        # XOR Key input row
        key_frame = ttk.Frame(analysis_frame)
        key_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(key_frame, text="XOR Decryption Key (Optional):").pack(side=tk.LEFT, padx=(0, 5))
        
        self.xor_key_var = tk.StringVar()
        xor_entry = ttk.Entry(key_frame, textvariable=self.xor_key_var, width=30)
        xor_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(key_frame, text="(Leave empty if message is not encrypted)", 
                 foreground="gray").pack(side=tk.LEFT)
        
        # Action buttons row
        button_frame = ttk.Frame(analysis_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.analyze_button = ttk.Button(button_frame, text="Analyze Image", 
                                         command=self.analyze_current_image, state=tk.DISABLED)
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.export_button = ttk.Button(button_frame, text="Export to CSV", 
                                        command=self.export_to_csv, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.vt_button = ttk.Button(button_frame, text="Check Threat Intel (VT)", 
                                    command=self.launch_vt_scan, state=tk.DISABLED)
        self.vt_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Clear", command=self.clear_results).pack(side=tk.LEFT)
        
        # Results display area
        results_frame = ttk.LabelFrame(analysis_frame, text="Analysis Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        canvas = tk.Canvas(results_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        self.results_container = ttk.Frame(canvas)
        
        self.results_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.results_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_canvas = canvas
        self.display_welcome_message()

    def setup_batch_analysis_tab(self):
        """Setup the Batch Directory Analysis tab."""
        batch_frame = ttk.LabelFrame(self.batch_tab, text="Batch Directory Analysis", padding="10")
        batch_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Folder selection row
        folder_frame = ttk.Frame(batch_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(folder_frame, text="Selected Folder:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.folder_path_var = tk.StringVar(value="No folder selected")
        folder_path_label = ttk.Label(folder_frame, textvariable=self.folder_path_var, 
                                     foreground="gray", relief=tk.SUNKEN, padding=5)
        folder_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(folder_frame, text="Select Folder", command=self.select_batch_folder).pack(side=tk.LEFT)
        
        # Options row
        options_frame = ttk.Frame(batch_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(options_frame, text="XOR Decryption Key (Optional):").pack(side=tk.LEFT, padx=(0, 5))
        self.batch_xor_key_var = tk.StringVar()
        ttk.Entry(options_frame, textvariable=self.batch_xor_key_var, width=30).pack(side=tk.LEFT, padx=(0, 5))
        
        # Action buttons row
        btn_frame = ttk.Frame(batch_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.batch_scan_btn = ttk.Button(btn_frame, text="Start Batch Scan", 
                                         command=self.start_batch_scan, state=tk.DISABLED)
        self.batch_scan_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.batch_stop_btn = ttk.Button(btn_frame, text="Stop / Cancel", 
                                         command=self.stop_batch_scan, state=tk.DISABLED)
        self.batch_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.batch_export_btn = ttk.Button(btn_frame, text="Export CSV Report", 
                                         command=self.export_batch_csv, state=tk.DISABLED)
        self.batch_export_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(btn_frame, text="Clear", command=self.clear_batch_results).pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress area
        progress_frame = ttk.Frame(batch_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 10))
        
        self.batch_progress_var = tk.DoubleVar(value=0)
        self.batch_progress = ttk.Progressbar(progress_frame, variable=self.batch_progress_var, maximum=100)
        self.batch_progress.pack(fill=tk.X, pady=(0, 5))
        
        self.batch_status_var = tk.StringVar(value="Ready.")
        ttk.Label(progress_frame, textvariable=self.batch_status_var, font=("Arial", 9, "italic")).pack(anchor=tk.W)
        
        # Batch Results Dashboard (Identical Structure to Single Image)
        results_frame = ttk.LabelFrame(batch_frame, text="Batch Analysis Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.batch_results_container = ttk.Frame(results_frame)
        self.batch_results_container.pack(fill=tk.BOTH, expand=True)
        
        self.display_batch_welcome_message()
    
    def create_status_bar(self):
        """Create the status bar at the bottom."""
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def display_welcome_message(self):
        """Display welcome message in results area."""
        # Clear existing widgets
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        # Create welcome frame
        welcome_frame = ttk.Frame(self.results_container)
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_label = ttk.Label(welcome_frame, 
                                 text=f"{APP_NAME} v{APP_VERSION}",
                                 font=("Arial", 14, "bold"))
        header_label.pack(pady=(0, 20))
        
        # Welcome text
        welcome_text = f"""Welcome to the SOC Steganography Detection Tool!

This tool analyzes images for hidden data using LSB (Least Significant Bit)
steganography detection techniques.

FEATURES:
  • LSB extraction and analysis
  • XOR decryption support  
  • SHA-256 file hashing
  • Comprehensive metadata extraction
  • CSV logging for audit trails

INSTRUCTIONS:
  1. Click "Select Image" to choose an image file (PNG, JPG, BMP)
  2. Enter XOR decryption key if the message is encrypted (optional)
  3. Click "Analyze Image" to perform detection
  4. Review the results below
  5. Export findings to CSV for reporting

Ready to begin analysis..."""
        
        text_label = ttk.Label(welcome_frame, text=welcome_text, 
                              justify=tk.LEFT, font=("Consolas", 9))
        text_label.pack(anchor=tk.W)
    
    def select_image(self):
        """Handle image file selection."""
        initial_dir = os.path.dirname(self.current_image_path) if self.current_image_path else None
        
        file_path = select_image_file(initial_dir)
        
        if file_path:
            # Clear previous results when new image is selected
            if self.current_image_path != file_path:
                self.current_analysis_result = None
                self.export_button.config(state=tk.DISABLED)
                self.file_menu.entryconfig("Export to CSV...", state=tk.DISABLED)
                self.display_welcome_message()
            
            self.current_image_path = file_path
            self.file_path_var.set(file_path)
            self.analyze_button.config(state=tk.NORMAL)
            self.update_status(f"Image selected: {os.path.basename(file_path)}")
        else:
            self.update_status("Image selection cancelled")
    
    def analyze_current_image(self):
        """Analyze the currently selected image."""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please select an image first.")
            return
        
        # Show loading indicator
        self.show_loading_indicator()
        
        # Update UI
        self.update_status("⏳ Analyzing image... Please wait")
        self.analyze_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)
        self.root.update_idletasks()
        
        # Get XOR key if provided
        xor_key = self.xor_key_var.get().strip()
        decode_key = xor_key if xor_key else None
        
        # Import threading dynamically (or usually at file top)
        import threading
        
        # Launch analysis in a separate background thread so GUI doesn't freeze
        analysis_thread = threading.Thread(
            target=self._run_analysis_thread, 
            args=(self.current_image_path, decode_key)
        )
        analysis_thread.daemon = True
        analysis_thread.start()

    def _run_analysis_thread(self, file_path, decode_key):
        """Runs the CPU-intensive analysis in a background thread."""
        try:
            # Perform analysis
            result = analyze_image(file_path, decode_key)
            
            # Safely schedule GUI updates back on the main thread
            self.root.after(0, self._handle_analysis_complete, result)
        except Exception as e:
            # Safely handle unexpected thread errors
            error_msg = str(e)
            self.root.after(0, self._handle_analysis_error, error_msg)

    def _handle_analysis_complete(self, result):
        """Callback to handle completed analysis on main thread."""
        self.current_analysis_result = result
        
        # Display results
        self.display_analysis_results(self.current_analysis_result)
        
        # Enable export button
        self.export_button.config(state=tk.NORMAL)
        self.vt_button.config(state=tk.NORMAL)
        self.file_menu.entryconfig("Export to CSV...", state=tk.NORMAL)
        
        # Success status
        has_hidden = self.current_analysis_result.get('has_hidden_data', False)
        if has_hidden:
            self.update_status("⚠️ Analysis complete - Hidden data detected!")
        else:
            self.update_status("✓ Analysis complete - Image is clean")
            
        self.analyze_button.config(state=tk.NORMAL)
        
    def _handle_analysis_error(self, error_msg):
        """Callback to handle errors on main thread."""
        messagebox.showerror("Analysis Error", f"Failed to analyze image:\n{error_msg}")
        self.update_status("❌ Analysis failed")
        self.display_welcome_message()
        self.analyze_button.config(state=tk.NORMAL)
        
    # === BATCH ANALYSIS LOGIC ===
    def display_batch_welcome_message(self):
        """Display welcome message in batch results area."""
        for widget in self.batch_results_container.winfo_children():
            widget.destroy()
            
        welcome_frame = ttk.Frame(self.batch_results_container)
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        header_label = ttk.Label(welcome_frame, text="Batch Directory Scanner", font=("Arial", 14, "bold"))
        header_label.pack(pady=(0, 20))
        
        text = "Select a folder to instantly scan all supported images for hidden steganography.\nMetrics and flags will load here automatically."
        ttk.Label(welcome_frame, text=text, font=("Consolas", 10)).pack(anchor=tk.W)

    def select_batch_folder(self):
        """Handle batch folder selection."""
        folder_path = select_folder()
        if folder_path:
            self.batch_folder_path = folder_path
            self.folder_path_var.set(folder_path)
            self.batch_scan_btn.config(state=tk.NORMAL)
            self.update_status(f"Folder selected: {os.path.basename(folder_path)}")
        else:
            self.update_status("Folder selection cancelled")

    def start_batch_scan(self):
        if not self.batch_folder_path:
            return
            
        self.is_batch_running = True
        self.batch_results = []
        self.batch_scan_btn.config(state=tk.DISABLED)
        self.batch_stop_btn.config(state=tk.NORMAL)
        
        xor_key = self.batch_xor_key_var.get().strip()
        decode_key = xor_key if xor_key else None
        
        # Gather images
        image_files = []
        for root_dir, _, files in os.walk(self.batch_folder_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in IMAGE_EXTENSIONS:
                    image_files.append(os.path.join(root_dir, file))
                    
        total_files = len(image_files)
        if total_files == 0:
            messagebox.showinfo("No Images", "No supported images found in the selected folder.")
            self.stop_batch_scan()
            return
            
        self.batch_progress.config(maximum=total_files)
        self.batch_progress_var.set(0)
        self.batch_status_var.set(f"Starting scan of {total_files} images...")
        self._update_batch_dashboard(0, total_files, 0, 0, 0)
        
        # Start manager thread
        import threading
        t = threading.Thread(target=self._run_batch_thread, args=(image_files, decode_key, total_files))
        t.daemon = True
        t.start()

    def stop_batch_scan(self):
        self.is_batch_running = False
        self.batch_status_var.set("Cancelling scan...")

    def _run_batch_thread(self, image_files, decode_key, total_files):
        processed = 0
        flagged = 0
        clean = 0
        errors = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_MAX_WORKERS) as executor:
            future_to_file = {executor.submit(analyze_image, file_path, decode_key): file_path for file_path in image_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                if not self.is_batch_running:
                    break 
                    
                processed += 1
                try:
                    result = future.result()
                    self.batch_results.append(result)
                    
                    if result.get('status') == 'error':
                        errors += 1
                    elif result.get('has_hidden_data'):
                        flagged += 1
                    else:
                        clean += 1
                except Exception as exc:
                    errors += 1
                
                self.root.after(0, self._update_batch_progress, processed, total_files, flagged, clean, errors)
                
        if self.is_batch_running:
            self.root.after(0, self._handle_batch_complete)
        else:
            self.root.after(0, self._handle_batch_cancelled)

    def _update_batch_progress(self, processed, total_files, flagged, clean, errors):
        self.batch_progress_var.set(processed)
        self.batch_status_var.set(f"Scanning... {processed}/{total_files} completed")
        self._update_batch_dashboard(processed, total_files, flagged, clean, errors)

    def _update_batch_dashboard(self, processed, total_files, flagged, clean, errors, is_complete=False, cancelled=False):
        for widget in self.batch_results_container.winfo_children():
            widget.destroy()
            
        main_frame = ttk.Frame(self.batch_results_container)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        status_frame = ttk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        if is_complete:
            if flagged > 0:
                header_text = f"🔴 BATCH COMPLETE - {flagged} INFECTIONS FOUND"
                bg_color = "#ffebee"
                fg_color = COLOR_DANGER
            else:
                header_text = "🟢 BATCH COMPLETE - ALL FOLDERS CLEAN"
                bg_color = "#e8f5e9"
                fg_color = COLOR_SUCCESS
        elif cancelled:
            header_text = "⚠️ BATCH PROCESS CANCELLED"
            bg_color = "#fff3e0"
            fg_color = "#f57c00"
        else:
            header_text = "⏳ SCANNING BATCH... PLEASE WAIT"
            bg_color = "#e3f2fd"
            fg_color = COLOR_PRIMARY
            
        status_label = tk.Label(status_frame, text=header_text, font=("Arial", 14, "bold"), fg=fg_color, bg=bg_color, pady=15)
        status_label.pack(fill=tk.X)
        status_frame.configure(style="Status.TFrame")
        
        metrics_section = ttk.LabelFrame(main_frame, text="📊 Scan Metrics", padding=10)
        metrics_section.pack(fill=tk.X, pady=(0, 10))
        
        metrics_grid = ttk.Frame(metrics_section)
        metrics_grid.pack(fill=tk.X)
        
        self._add_info_row(metrics_grid, 0, "Total Images Located:", f"{total_files:,}")
        self._add_info_row(metrics_grid, 1, "Images Processed:", f"{processed:,}")
        self._add_info_row(metrics_grid, 2, "Suspicious (Stego Found):", f"{flagged:,}", value_color=COLOR_DANGER if flagged > 0 else None, value_bold=True)
        self._add_info_row(metrics_grid, 3, "Clean Images:", f"{clean:,}", value_color=COLOR_SUCCESS)
        self._add_info_row(metrics_grid, 4, "Errors:", f"{errors:,}")

    def _handle_batch_complete(self):
        self.batch_status_var.set("Batch processing complete! Report ready for export.")
        self.batch_scan_btn.config(state=tk.NORMAL)
        self.batch_stop_btn.config(state=tk.DISABLED)
        self.batch_export_btn.config(state=tk.NORMAL)
        
        flagged = sum(1 for res in self.batch_results if res.get('has_hidden_data'))
        clean = sum(1 for res in self.batch_results if not res.get('has_hidden_data') and res.get('status') != 'error')
        errors = sum(1 for res in self.batch_results if res.get('status') == 'error')
        
        self._update_batch_dashboard(len(self.batch_results), len(self.batch_results), flagged, clean, errors, is_complete=True)

    def _handle_batch_cancelled(self):
        self.batch_status_var.set("Batch processing cancelled.")
        self.batch_scan_btn.config(state=tk.NORMAL)
        self.batch_stop_btn.config(state=tk.DISABLED)
        self.batch_export_btn.config(state=tk.NORMAL)
        
        flagged = sum(1 for res in self.batch_results if res.get('has_hidden_data'))
        clean = sum(1 for res in self.batch_results if not res.get('has_hidden_data') and res.get('status') != 'error')
        errors = sum(1 for res in self.batch_results if res.get('status') == 'error')
        total = int(self.batch_progress.cget('maximum'))
        
        self._update_batch_dashboard(len(self.batch_results), total, flagged, clean, errors, cancelled=True)

    def export_batch_csv(self):
        """Export the current batch results array manually."""
        if not self.batch_results:
            messagebox.showwarning("No Results", "Please run a batch scan first.")
            return
            
        try:
            log_res = log_batch_results(self.batch_results)
            if log_res.get('success'):
                messagebox.showinfo("Export Success", f"Batch Results successfully logged to CSV!\n\nFile: {log_res.get('csv_path')}")
                self.update_status(f"Batch exported to: {log_res.get('csv_path')}")
            else:
                messagebox.showerror("Export Error", f"Failed to save batch logs:\n{log_res.get('error')}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Unexpected error during export:\n{str(e)}")

    def clear_batch_results(self):
        """Clear the batch results dashboard entirely."""
        self.batch_folder_path = None
        self.batch_results = []
        self.folder_path_var.set("No folder selected")
        self.batch_xor_key_var.set("")
        self.batch_scan_btn.config(state=tk.DISABLED)
        self.batch_export_btn.config(state=tk.DISABLED)
        self.batch_progress_var.set(0)
        self.batch_status_var.set("Ready.")
        self.display_batch_welcome_message()
    
    def show_loading_indicator(self):
        """Display a loading indicator in the results area."""
        # Clear existing widgets
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        # Create loading frame
        loading_frame = ttk.Frame(self.results_container)
        loading_frame.pack(fill=tk.BOTH, expand=True)
        
        # Center the loading message
        center_frame = ttk.Frame(loading_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        loading_label = ttk.Label(center_frame, 
                                  text="⏳ Analyzing Image...",
                                  font=("Arial", 14, "bold"))
        loading_label.pack(pady=10)
        
        progress = ttk.Progressbar(center_frame, mode='indeterminate', length=300)
        progress.pack(pady=10)
        progress.start(10)
        
        status_label = ttk.Label(center_frame, 
                                text="Please wait while the image is being analyzed",
                                font=("Arial", 9))
        status_label.pack()
    
    def display_analysis_results(self, result):
        """
        Display analysis results in structured panel format.
        
        Args:
            result (dict): Analysis result from analyze_image()
        """
        # Clear existing widgets
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        # Main results frame
        main_frame = ttk.Frame(self.results_container)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === DETECTION STATUS INDICATOR (Prominent at top) ===
        status_frame = ttk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        has_hidden_data = result.get('has_hidden_data', False)
        status = result.get('status', 'unknown')
        
        if status == 'error':
            status_color = COLOR_DANGER
            status_icon = "❌"
            status_text = "ERROR - Analysis Failed"
            bg_color = "#ffebee"
        elif has_hidden_data:
            status_color = COLOR_DANGER
            status_icon = "🔴"
            status_text = "HIDDEN DATA DETECTED"
            bg_color = "#ffebee"
        else:
            status_color = COLOR_SUCCESS
            status_icon = "🟢"
            status_text = "CLEAN - No Hidden Data"
            bg_color = "#e8f5e9"
        
        status_label = tk.Label(status_frame, text=f"{status_icon}  {status_text}",
                               font=("Arial", 14, "bold"), fg=status_color, bg=bg_color,
                               pady=15)
        status_label.pack(fill=tk.X)
        status_frame.configure(style="Status.TFrame")
        
        # === FILE INFORMATION SECTION ===
        file_section = ttk.LabelFrame(main_frame, text="📁 File Information", padding=10)
        file_section.pack(fill=tk.X, pady=(0, 10))
        
        file_grid = ttk.Frame(file_section)
        file_grid.pack(fill=tk.X)
        
        self._add_info_row(file_grid, 0, "File Name:", os.path.basename(result.get('file_path', 'N/A')))
        self._add_info_row(file_grid, 1, "File Path:", result.get('file_path', 'N/A'), wrap=True)
        self._add_info_row(file_grid, 2, "SHA-256 Hash:", result.get('file_hash', 'N/A')[:HASH_DISPLAY_LENGTH] + "...")
        self._add_info_row(file_grid, 3, "File Size:", f"{result.get('file_size', 0):,} bytes")
        self._add_info_row(file_grid, 4, "Analysis Time:", result.get('timestamp', 'N/A'))
        
        # === IMAGE METADATA SECTION ===
        metadata = result.get('metadata', {})
        meta_section = ttk.LabelFrame(main_frame, text="🖼️ Image Metadata", padding=10)
        meta_section.pack(fill=tk.X, pady=(0, 10))
        
        meta_grid = ttk.Frame(meta_section)
        meta_grid.pack(fill=tk.X)
        
        self._add_info_row(meta_grid, 0, "Format:", metadata.get('format', 'N/A'))
        self._add_info_row(meta_grid, 1, "Dimensions:", metadata.get('dimensions', 'N/A'))
        self._add_info_row(meta_grid, 2, "Color Mode:", metadata.get('mode', 'N/A'))
        self._add_info_row(meta_grid, 3, "Total Pixels:", f"{metadata.get('total_pixels', 0):,}")
        self._add_info_row(meta_grid, 4, "Max LSB Capacity:", f"{metadata.get('max_capacity_bytes', 0):,} bytes")
        
        # === DETECTION RESULTS SECTION ===
        detect_section = ttk.LabelFrame(main_frame, text="🔍 Detection Results", padding=10)
        detect_section.pack(fill=tk.X, pady=(0, 10))
        
        entropy_score = result.get('entropy_score', 0.0)
        from config import ENTROPY_THRESHOLD
        
        if status == 'error':
            error_label = ttk.Label(detect_section, 
                                   text=f"Error: {result.get('error', 'Unknown error')}",
                                   foreground=COLOR_DANGER, font=("Arial", 10))
            error_label.pack(anchor=tk.W)
        elif has_hidden_data:
            detect_grid = ttk.Frame(detect_section)
            detect_grid.pack(fill=tk.X)
            
            self._add_info_row(detect_grid, 0, "Hidden Data:", "YES", value_color=COLOR_DANGER, value_bold=True)
            self._add_info_row(detect_grid, 1, "LSB Shannon Entropy:", f"{entropy_score:.4f}", value_color=COLOR_DANGER if entropy_score >= ENTROPY_THRESHOLD else COLOR_SUCCESS, value_bold=True)
            
            hidden_message = result.get('hidden_message', '')
            if hidden_message:
                # Message preview
                ttk.Label(detect_grid, text="Extracted Message:", 
                         font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
                
                # Message text box
                message_frame = ttk.Frame(detect_section)
                message_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
                
                message_text = tk.Text(message_frame, wrap=tk.WORD, height=8, 
                                      font=("Consolas", 9), bg="#fff3e0")
                message_text.insert(1.0, hidden_message)
                message_text.config(state=tk.DISABLED)
                
                msg_scrollbar = ttk.Scrollbar(message_frame, command=message_text.yview)
                message_text.config(yscrollcommand=msg_scrollbar.set)
                
                message_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                msg_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            detect_grid = ttk.Frame(detect_section)
            detect_grid.pack(fill=tk.X)
            
            self._add_info_row(detect_grid, 0, "Hidden Data:", "NO", value_color=COLOR_SUCCESS, value_bold=True)
            self._add_info_row(detect_grid, 1, "LSB Shannon Entropy:", f"{entropy_score:.4f}", value_color=COLOR_SUCCESS, value_bold=True)
            
            clean_label = ttk.Label(detect_section, 
                                   text="✓ No steganographic content or mathematical anomalies detected.",
                                   foreground=COLOR_SUCCESS, font=("Arial", 9))
            clean_label.pack(anchor=tk.W, pady=(5, 0))
    
    def _add_info_row(self, parent, row, label_text, value_text, wrap=False, 
                     value_color=None, value_bold=False):
        """
        Helper method to add a label-value row to a grid.
        
        Args:
            parent: Parent frame
            row: Grid row number
            label_text: Label text (left side)
            value_text: Value text (right side)
            wrap: Whether to wrap long text
            value_color: Optional color for value text
            value_bold: Whether to make value text bold
        """
        label = ttk.Label(parent, text=label_text, font=("Arial", 9, "bold"))
        label.grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=3)
        
        value_font = ("Arial", 9, "bold") if value_bold else ("Arial", 9)
        
        if wrap:
            value = ttk.Label(parent, text=value_text, font=value_font, wraplength=500)
        else:
            value = ttk.Label(parent, text=value_text, font=value_font)
        
        if value_color:
            value.configure(foreground=value_color)
        
        value.grid(row=row, column=1, sticky=tk.W, pady=3)
    
    def export_to_csv(self):
        """Export current analysis result to CSV."""
        if not self.current_analysis_result:
            messagebox.showwarning("No Results", "Please analyze an image first.")
            return
        
        try:
            result = log_analysis_to_csv(self.current_analysis_result)
            
            if result['success']:
                messagebox.showinfo("Export Success", 
                                   f"Results logged to CSV successfully!\n\nFile: {result['csv_path']}")
                self.update_status(f"Exported to: {result['csv_path']}")
            else:
                messagebox.showerror("Export Failed", 
                                    f"Failed to export to CSV:\n{result['error']}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Unexpected error during export:\n{str(e)}")
    
    def clear_results(self):
        """Clear current results and reset interface."""
        self.current_image_path = None
        self.current_analysis_result = None
        self.file_path_var.set("No image selected")
        self.xor_key_var.set("")
        self.analyze_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)
        self.vt_button.config(state=tk.DISABLED)
        self.file_menu.entryconfig("Export to CSV...", state=tk.DISABLED)
        self.display_welcome_message()
        self.update_status("Cleared - Ready for new analysis")
    
    def update_status(self, message):
        """Update the status bar message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"  [{timestamp}] {message}")
    
    def launch_vt_scan(self):
        """Spawns popup and triggers VT asynchronous thread."""
        if not self.current_analysis_result:
            return
            
        import threading
        self.vt_button.config(state=tk.DISABLED)
        
        # Display the custom Toplevel popup
        vt_window = tk.Toplevel(self.root)
        vt_window.title("VirusTotal Threat Intelligence")
        vt_window.geometry("550x400")
        vt_window.resizable(False, False)
        vt_window.transient(self.root)
        vt_window.grab_set()
        
        ttk.Label(vt_window, text="Querying Global Threat Database...", font=("Arial", 12, "bold")).pack(pady=20)
        
        progress = ttk.Progressbar(vt_window, mode='indeterminate', length=300)
        progress.pack(pady=10)
        progress.start(10)
        
        status_var = tk.StringVar(value="Waiting for API response...")
        ttk.Label(vt_window, textvariable=status_var, font=("Arial", 10)).pack(pady=10)
        
        # Build Thread targets
        img_hash = self.current_analysis_result.get('file_hash')
        payload_hash = None
        if self.current_analysis_result.get('has_hidden_data'):
            payload_str = self.current_analysis_result.get('hidden_message', '')
            payload_hash = hash_payload_string(payload_str)
            
        t = threading.Thread(target=self._run_vt_thread, args=(img_hash, payload_hash, vt_window, status_var, progress))
        t.daemon = True
        t.start()

    def _run_vt_thread(self, img_hash, payload_hash, window, status_var, progress):
        try:
            status_var.set("Scanning carrier image hash...")
            img_result = query_virustotal_hash(img_hash)
            
            payload_result = None
            if payload_hash:
                status_var.set("Scanning extracted hidden payload hash...")
                payload_result = query_virustotal_hash(payload_hash)
                
            self.root.after(0, self._render_vt_results, window, img_result, payload_result)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("VT Error", str(e), parent=window))
            self.root.after(0, window.destroy)
            self.root.after(0, lambda: self.vt_button.config(state=tk.NORMAL))

    def _render_vt_results(self, window, img_res, payload_res):
        for widget in window.winfo_children():
            widget.destroy()
            
        main_frame = ttk.Frame(window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Display Image Result
        ttk.Label(main_frame, text="Carrier Image Scan", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(0, 5))
        if img_res and img_res.get('success'):
            data = img_res['data']
            color = COLOR_DANGER if data['is_threat'] else COLOR_SUCCESS
            text = f"{data['malicious']}/{data['total']} Malicious"
            tk.Label(main_frame, text=text, font=("Arial", 14, "bold"), fg=color, bg="#f5f5f5", padx=10, pady=5).pack(anchor=tk.W)
        else:
            tk.Label(main_frame, text=img_res.get('error', 'Unknown Error') if img_res else "No data", fg="gray").pack(anchor=tk.W)
            
        # Display Payload Result
        if payload_res:
            ttk.Label(main_frame, text="\nExtracted Payload Scan", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
            if payload_res.get('success'):
                data = payload_res['data']
                color = COLOR_DANGER if data['is_threat'] else COLOR_SUCCESS
                text = f"{data['malicious']}/{data['total']} Malicious"
                tk.Label(main_frame, text=text, font=("Arial", 14, "bold"), fg=color, bg="#f5f5f5", padx=10, pady=5).pack(anchor=tk.W)
                
                if data['is_threat']:
                    ttk.Label(main_frame, text="⚠️ CRITICAL: The extracted steganography payload is confirmed malware!", foreground=COLOR_DANGER).pack(anchor=tk.W, pady=5)
            else:
                tk.Label(main_frame, text=payload_res.get('error', 'Unknown Error'), fg="gray").pack(anchor=tk.W)
                
        # Close button
        ttk.Button(main_frame, text="Close Report", command=window.destroy).pack(side=tk.BOTTOM, pady=10)
        self.vt_button.config(state=tk.NORMAL)
    
    def show_about(self):
        """Display About dialog."""
        from config import ABOUT_TEXT
        messagebox.showinfo("About", ABOUT_TEXT)
    
    def exit_application(self):
        """Exit the application."""
        if messagebox.askokcancel("Quit", "Are you sure you want to exit?"):
            self.root.quit()


def launch_gui():
    """Launch the main GUI application."""
    root = tk.Tk()
    app = SteganographyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
