"""
Main Window Module for SOC Steganography Detection Tool.
Implements the primary Tkinter GUI interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys

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
        
        # Results display area
        results_frame = ttk.LabelFrame(analysis_frame, text="Analysis Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Scrolled text widget for results
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, 
                                                       height=20, font=("Consolas", 9))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.results_text.tag_config("header", font=("Consolas", 10, "bold"))
        self.results_text.tag_config("success", foreground=COLOR_SUCCESS)
        self.results_text.tag_config("danger", foreground=COLOR_DANGER)
        self.results_text.tag_config("key", font=("Consolas", 9, "bold"))
        
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
        welcome = f"""
═══════════════════════════════════════════════════════════════════════
  {APP_NAME}
  Version {APP_VERSION}
═══════════════════════════════════════════════════════════════════════

Welcome to the SOC Steganography Detection Tool!

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

Ready to begin analysis...
═══════════════════════════════════════════════════════════════════════
"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, welcome)
    
    def select_image(self):
        """Handle image file selection."""
        initial_dir = os.path.dirname(self.current_image_path) if self.current_image_path else None
        
        file_path = select_image_file(initial_dir)
        
        if file_path:
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
        
        # Update UI
        self.update_status("Analyzing image... Please wait")
        self.analyze_button.config(state=tk.DISABLED)
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
            
            self.update_status("Analysis complete")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze image:\n{str(e)}")
            self.update_status("Analysis failed")
        finally:
            self.analyze_button.config(state=tk.NORMAL)
    
    def display_analysis_results(self, result):
        """
        Display analysis results in the text widget.
        
        Args:
            result (dict): Analysis result from analyze_image()
        """
        self.results_text.delete(1.0, tk.END)
        
        # Header
        self.results_text.insert(tk.END, "═" * 70 + "\n", "header")
        self.results_text.insert(tk.END, "  STEGANOGRAPHY ANALYSIS REPORT\n", "header")
        self.results_text.insert(tk.END, "═" * 70 + "\n\n", "header")
        
        # File Information
        self.results_text.insert(tk.END, "FILE INFORMATION\n", "key")
        self.results_text.insert(tk.END, "─" * 70 + "\n")
        self.results_text.insert(tk.END, f"File Name:      {os.path.basename(result.get('file_path', 'N/A'))}\n")
        self.results_text.insert(tk.END, f"File Path:      {result.get('file_path', 'N/A')}\n")
        self.results_text.insert(tk.END, f"File Hash:      {result.get('file_hash', 'N/A')[:HASH_DISPLAY_LENGTH]}...\n")
        self.results_text.insert(tk.END, f"File Size:      {result.get('file_size', 0):,} bytes\n")
        self.results_text.insert(tk.END, f"Analysis Time:  {result.get('timestamp', 'N/A')}\n\n")
        
        # Image Metadata
        metadata = result.get('metadata', {})
        self.results_text.insert(tk.END, "IMAGE METADATA\n", "key")
        self.results_text.insert(tk.END, "─" * 70 + "\n")
        self.results_text.insert(tk.END, f"Format:         {metadata.get('format', 'N/A')}\n")
        self.results_text.insert(tk.END, f"Dimensions:     {metadata.get('dimensions', 'N/A')}\n")
        self.results_text.insert(tk.END, f"Color Mode:     {metadata.get('mode', 'N/A')}\n")
        self.results_text.insert(tk.END, f"Total Pixels:   {metadata.get('total_pixels', 0):,}\n")
        self.results_text.insert(tk.END, f"Max Capacity:   {metadata.get('max_capacity_bytes', 0):,} bytes\n\n")
        
        # Detection Results
        self.results_text.insert(tk.END, "DETECTION RESULTS\n", "key")
        self.results_text.insert(tk.END, "─" * 70 + "\n")
        
        has_hidden_data = result.get('has_hidden_data', False)
        status = result.get('status', 'unknown')
        
        if status == 'error':
            self.results_text.insert(tk.END, "Status:         ERROR\n", "danger")
            self.results_text.insert(tk.END, f"Error Message:  {result.get('error', 'Unknown error')}\n", "danger")
        elif has_hidden_data:
            self.results_text.insert(tk.END, "Status:         ⚠ HIDDEN DATA DETECTED\n", "danger")
            self.results_text.insert(tk.END, f"Message Found:  YES\n", "danger")
            
            hidden_message = result.get('hidden_message', '')
            self.results_text.insert(tk.END, f"\nExtracted Message:\n")
            self.results_text.insert(tk.END, "─" * 70 + "\n")
            self.results_text.insert(tk.END, f"{hidden_message}\n", "danger")
            self.results_text.insert(tk.END, "─" * 70 + "\n")
        else:
            self.results_text.insert(tk.END, "Status:         ✓ CLEAN (No hidden data detected)\n", "success")
            self.results_text.insert(tk.END, f"Message Found:  NO\n", "success")
        
        self.results_text.insert(tk.END, "\n" + "═" * 70 + "\n")
        self.results_text.insert(tk.END, "End of Report\n")
        self.results_text.insert(tk.END, "═" * 70 + "\n")
    
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
        """Update the status bar message."""
        self.status_var.set(f"  {message}")
    
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
