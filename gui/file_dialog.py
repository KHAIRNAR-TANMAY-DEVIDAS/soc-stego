"""
File Dialog Module for SOC Steganography Detection Tool.
Handles file and folder selection dialogs.
"""

import tkinter as tk
from tkinter import filedialog
import os


def select_image_file(initial_dir=None):
    """
    Opens a file dialog to select an image file.
    
    Args:
        initial_dir (str, optional): Initial directory to open. Defaults to current directory.
    
    Returns:
        str: Selected file path, or empty string if cancelled
    """
    # Create a temporary root window (hidden)
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
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
    
    # Set initial directory
    if initial_dir is None:
        initial_dir = os.getcwd()
    
    # Open file dialog
    file_path = filedialog.askopenfilename(
        title="Select Image to Analyze",
        initialdir=initial_dir,
        filetypes=filetypes
    )
    
    # Clean up temporary root
    root.destroy()
    
    return file_path


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
