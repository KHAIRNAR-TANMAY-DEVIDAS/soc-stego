"""
Configuration module for SOC Steganography Detection Tool.
Contains application constants, paths, and settings.
"""

import os
from datetime import datetime

# Application Information
APP_NAME = "SOC Steganography Detection Tool"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Image Steganography Detection and Analysis Tool for SOC Operations"

# GUI Configuration
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# Color Scheme (Professional SOC Theme)
COLOR_PRIMARY = "#2C3E50"        # Dark blue-gray
COLOR_SECONDARY = "#34495E"      # Lighter blue-gray
COLOR_SUCCESS = "#27AE60"        # Green (clean/safe)
COLOR_WARNING = "#F39C12"        # Orange (suspicious)
COLOR_DANGER = "#E74C3C"         # Red (hidden data detected)
COLOR_INFO = "#3498DB"           # Blue (information)
COLOR_BACKGROUND = "#ECF0F1"     # Light gray background
COLOR_TEXT = "#2C3E50"           # Dark text

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
TESTS_DIR = os.path.join(BASE_DIR, "tests")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

# CSV Logging Configuration
CSV_FILENAME_PREFIX = "stego_analysis"
CSV_DATETIME_FORMAT = "%Y%m%d_%H%M%S"

def get_default_csv_path():
    """Generate default CSV log file path with timestamp."""
    timestamp = datetime.now().strftime(CSV_DATETIME_FORMAT)
    filename = f"{CSV_FILENAME_PREFIX}_{timestamp}.csv"
    return os.path.join(LOGS_DIR, filename)

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

# Image File Filters
SUPPORTED_IMAGE_FORMATS = [
    ("PNG files", "*.png"),
    ("JPEG files", "*.jpg *.jpeg"),
    ("BMP files", "*.bmp"),
    ("All supported images", "*.png *.jpg *.jpeg *.bmp"),
    ("All files", "*.*")
]

IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp']

# Analysis Configuration
MESSAGE_PREVIEW_LENGTH = 100  # Characters to show in preview
HASH_DISPLAY_LENGTH = 16      # Characters of hash to display in GUI

# Detection Thresholds (for future enhancements)
ENTROPY_THRESHOLD = 7.5       # Statistical entropy threshold
LSB_ANOMALY_THRESHOLD = 0.05  # LSB distribution anomaly threshold

# Batch Processing Configuration
BATCH_MAX_WORKERS = 4         # For parallel processing (future enhancement)
BATCH_TIMEOUT_SECONDS = 30    # Per-image analysis timeout

# Error Messages
ERROR_FILE_NOT_FOUND = "Image file not found"
ERROR_INVALID_IMAGE = "Invalid or corrupted image file"
ERROR_ANALYSIS_FAILED = "Analysis failed due to unexpected error"
ERROR_DECRYPTION_FAILED = "Decryption failed - possible wrong key"

# Success Messages
SUCCESS_ANALYSIS_COMPLETE = "Analysis completed successfully"
SUCCESS_LOGGED_TO_CSV = "Results logged to CSV successfully"
SUCCESS_BATCH_COMPLETE = "Batch analysis completed"

# GUI Labels
LABEL_SELECT_IMAGE = "Select Image"
LABEL_ANALYZE = "Analyze"
LABEL_EXPORT_CSV = "Export to CSV"
LABEL_CLEAR = "Clear"
LABEL_XOR_KEY = "XOR Decryption Key (Optional):"
LABEL_STATUS = "Ready"

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
