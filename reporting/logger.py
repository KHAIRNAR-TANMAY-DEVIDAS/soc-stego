"""
CSV Logging Module for SOC Steganography Detection Tool.
Handles logging of analysis results to CSV files for audit trails and reporting.
"""

import csv
import os
from datetime import datetime
from config import CSV_FIELDS, MESSAGE_PREVIEW_LENGTH, get_default_csv_path


def log_analysis_to_csv(analysis_result, csv_path=None):
    """
    Logs analysis results to a CSV file for audit trail purposes.
    
    Args:
        analysis_result (dict): Output from analyze_image() function containing:
            - status: 'success' or 'error'
            - file_path: Path to analyzed file
            - file_hash: SHA-256 hash
            - file_size: Size in bytes
            - metadata: Image metadata dict
            - hidden_message: Extracted message or None
            - has_hidden_data: Boolean
            - timestamp: Analysis timestamp
            - error: Error message if status is 'error'
        
        csv_path (str, optional): Path to CSV file. If None, uses default path.
    
    Returns:
        dict: Result dictionary with keys:
            - success: Boolean indicating if logging succeeded
            - csv_path: Path where data was logged
            - error: Error message if success is False
    """
    result = {
        'success': False,
        'csv_path': csv_path,
        'error': None
    }
    
    # Use default CSV path if none provided
    if csv_path is None:
        csv_path = get_default_csv_path()
        result['csv_path'] = csv_path
    
    # Ensure directory exists
    csv_dir = os.path.dirname(csv_path)
    if csv_dir and not os.path.exists(csv_dir):
        try:
            os.makedirs(csv_dir, exist_ok=True)
        except Exception as e:
            result['error'] = f"Failed to create directory: {str(e)}"
            return result
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.exists(csv_path)
    
    try:
        # Prepare row data from analysis result
        row_data = prepare_csv_row(analysis_result)
        
        # Open CSV file in append mode
        with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write the analysis data
            writer.writerow(row_data)
        
        result['success'] = True
        return result
        
    except PermissionError:
        result['error'] = f"Permission denied: Cannot write to {csv_path}"
        return result
    except Exception as e:
        result['error'] = f"Failed to log to CSV: {str(e)}"
        return result


def prepare_csv_row(analysis_result):
    """
    Converts analysis result dictionary to CSV row format.
    
    Args:
        analysis_result (dict): Output from analyze_image()
    
    Returns:
        dict: Dictionary matching CSV_FIELDS structure
    """
    metadata = analysis_result.get('metadata', {})
    hidden_message = analysis_result.get('hidden_message', '')
    
    # Prepare message preview (truncate if too long)
    if hidden_message and hidden_message != "No hidden message detected":
        if len(hidden_message) > MESSAGE_PREVIEW_LENGTH:
            message_preview = hidden_message[:MESSAGE_PREVIEW_LENGTH] + "..."
        else:
            message_preview = hidden_message
        message_length = len(hidden_message)
    else:
        message_preview = hidden_message if hidden_message else "None"
        message_length = 0
    
    # Extract file name from path
    file_path = analysis_result.get('file_path', '')
    file_name = os.path.basename(file_path) if file_path else 'Unknown'
    
    # Build CSV row
    row = {
        'timestamp': analysis_result.get('timestamp', datetime.now().isoformat()),
        'file_path': file_path,
        'file_name': file_name,
        'file_hash': analysis_result.get('file_hash', 'N/A'),
        'file_size_bytes': analysis_result.get('file_size', 0),
        'image_format': metadata.get('format', 'N/A'),
        'image_dimensions': metadata.get('dimensions', 'N/A'),
        'image_mode': metadata.get('mode', 'N/A'),
        'max_capacity_bytes': metadata.get('max_capacity_bytes', 0),
        'has_hidden_data': analysis_result.get('has_hidden_data', False),
        'hidden_message_length': message_length,
        'hidden_message_preview': message_preview,
        'decryption_key_used': 'No',  # Will be enhanced in future phases
        'analysis_status': analysis_result.get('status', 'unknown'),
        'error_message': analysis_result.get('error', '')
    }
    
    return row


def log_batch_results(analysis_results, csv_path=None):
    """
    Logs multiple analysis results to CSV in a single operation.
    More efficient than calling log_analysis_to_csv() multiple times.
    
    Args:
        analysis_results (list): List of analysis result dictionaries
        csv_path (str, optional): Path to CSV file. If None, uses default.
    
    Returns:
        dict: Result dictionary with keys:
            - success: Boolean
            - csv_path: Path where data was logged
            - logged_count: Number of results logged
            - error: Error message if any
    """
    result = {
        'success': False,
        'csv_path': csv_path,
        'logged_count': 0,
        'error': None
    }
    
    if not analysis_results:
        result['error'] = "No results to log"
        return result
    
    # Use default CSV path if none provided
    if csv_path is None:
        csv_path = get_default_csv_path()
        result['csv_path'] = csv_path
    
    # Ensure directory exists
    csv_dir = os.path.dirname(csv_path)
    if csv_dir and not os.path.exists(csv_dir):
        try:
            os.makedirs(csv_dir, exist_ok=True)
        except Exception as e:
            result['error'] = f"Failed to create directory: {str(e)}"
            return result
    
    # Check if file exists
    file_exists = os.path.exists(csv_path)
    
    try:
        # Open CSV file in append mode
        with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write all results
            for analysis_result in analysis_results:
                row_data = prepare_csv_row(analysis_result)
                writer.writerow(row_data)
                result['logged_count'] += 1
        
        result['success'] = True
        return result
        
    except Exception as e:
        result['error'] = f"Failed to log batch results: {str(e)}"
        return result


def get_csv_files(logs_dir=None):
    """
    Lists all CSV log files in the logs directory.
    
    Args:
        logs_dir (str, optional): Directory to search. Uses config default if None.
    
    Returns:
        list: List of CSV file paths
    """
    if logs_dir is None:
        from config import LOGS_DIR
        logs_dir = LOGS_DIR
    
    if not os.path.exists(logs_dir):
        return []
    
    csv_files = []
    for filename in os.listdir(logs_dir):
        if filename.endswith('.csv'):
            csv_files.append(os.path.join(logs_dir, filename))
    
    return sorted(csv_files, reverse=True)  # Most recent first
