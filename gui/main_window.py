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
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === Single Image Analysis Section ===
        analysis_frame = ttk.LabelFrame(main_frame, text="Single Image Analysis", padding="10")
        analysis_frame.pack(fill=tk.BOTH, expand=True)
        
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
        
        ttk.Button(button_frame, text="Clear", command=self.clear_results).pack(side=tk.LEFT)
        
        # Results display area - Phase 4 Enhanced Structured Panel
        results_frame = ttk.LabelFrame(analysis_frame, text="Analysis Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create scrollable container for results
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
        
        # Store canvas reference for later use
        self.results_canvas = canvas
        
        # Initial welcome message
        self.display_welcome_message()
    
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
        
        try:
            # Get XOR key if provided
            xor_key = self.xor_key_var.get().strip()
            decode_key = xor_key if xor_key else None
            
            # Perform analysis
            self.current_analysis_result = analyze_image(self.current_image_path, decode_key)
            
            # Display results
            self.display_analysis_results(self.current_analysis_result)
            
            # Enable export button
            self.export_button.config(state=tk.NORMAL)
            self.file_menu.entryconfig("Export to CSV...", state=tk.NORMAL)
            
            # Success status
            has_hidden = self.current_analysis_result.get('has_hidden_data', False)
            if has_hidden:
                self.update_status("⚠️ Analysis complete - Hidden data detected!")
            else:
                self.update_status("✓ Analysis complete - Image is clean")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze image:\n{str(e)}")
            self.update_status("❌ Analysis failed")
            self.display_welcome_message()
        finally:
            self.analyze_button.config(state=tk.NORMAL)
    
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
        
        if status == 'error':
            error_label = ttk.Label(detect_section, 
                                   text=f"Error: {result.get('error', 'Unknown error')}",
                                   foreground=COLOR_DANGER, font=("Arial", 10))
            error_label.pack(anchor=tk.W)
        elif has_hidden_data:
            detect_grid = ttk.Frame(detect_section)
            detect_grid.pack(fill=tk.X)
            
            self._add_info_row(detect_grid, 0, "Hidden Data:", "YES", value_color=COLOR_DANGER, value_bold=True)
            
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
            
            clean_label = ttk.Label(detect_section, 
                                   text="✓ No steganographic content detected in this image.",
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
        self.file_menu.entryconfig("Export to CSV...", state=tk.DISABLED)
        self.display_welcome_message()
        self.update_status("Cleared - Ready for new analysis")
    
    def update_status(self, message):
        """Update the status bar message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"  [{timestamp}] {message}")
    
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
