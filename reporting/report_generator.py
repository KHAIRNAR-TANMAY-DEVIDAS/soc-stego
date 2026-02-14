"""
Report Generator Module for SOC Steganography Detection Tool.
Generates summary reports and statistics from CSV log files.
"""

import csv
import os
from datetime import datetime
from collections import Counter


def generate_summary_report(csv_path):
    """
    Generates a comprehensive summary report from a CSV log file.
    
    Args:
        csv_path (str): Path to the CSV log file
    
    Returns:
        dict: Summary statistics containing:
            - success: Boolean indicating if report generation succeeded
            - total_scans: Total number of images analyzed
            - suspicious_count: Images with hidden data detected
            - clean_count: Images with no hidden data
            - error_count: Failed analyses
            - format_breakdown: Count by image format
            - total_size_mb: Total size of analyzed files in MB
            - detection_rate: Percentage of images with hidden data
            - hidden_messages: List of detected messages (preview)
            - csv_path: Path to source CSV
            - report_timestamp: When report was generated
            - error: Error message if success is False
    """
    report = {
        'success': False,
        'total_scans': 0,
        'suspicious_count': 0,
        'clean_count': 0,
        'error_count': 0,
        'format_breakdown': {},
        'total_size_mb': 0.0,
        'detection_rate': 0.0,
        'hidden_messages': [],
        'csv_path': csv_path,
        'report_timestamp': datetime.now().isoformat(),
        'error': None
    }
    
    # Validate file exists
    if not os.path.exists(csv_path):
        report['error'] = f"CSV file not found: {csv_path}"
        return report
    
    try:
        format_counter = Counter()
        total_size_bytes = 0
        
        # Read and process CSV file
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                report['total_scans'] += 1
                
                # Count by detection status
                has_hidden_data = row.get('has_hidden_data', 'False')
                if has_hidden_data in ['True', 'true', '1', 'yes']:
                    report['suspicious_count'] += 1
                    
                    # Store message preview if available
                    message_preview = row.get('hidden_message_preview', '')
                    if message_preview and message_preview not in ['None', 'No hidden message detected', '']:
                        report['hidden_messages'].append({
                            'file_name': row.get('file_name', 'Unknown'),
                            'timestamp': row.get('timestamp', 'N/A'),
                            'message_preview': message_preview,
                            'message_length': int(row.get('hidden_message_length', 0))
                        })
                else:
                    report['clean_count'] += 1
                
                # Count errors
                analysis_status = row.get('analysis_status', 'success')
                if analysis_status == 'error':
                    report['error_count'] += 1
                
                # Format breakdown
                img_format = row.get('image_format', 'Unknown')
                format_counter[img_format] += 1
                
                # Total size calculation
                try:
                    file_size = int(row.get('file_size_bytes', 0))
                    total_size_bytes += file_size
                except (ValueError, TypeError):
                    pass
        
        # Calculate derived statistics
        report['format_breakdown'] = dict(format_counter)
        report['total_size_mb'] = round(total_size_bytes / (1024 * 1024), 2)
        
        if report['total_scans'] > 0:
            report['detection_rate'] = round(
                (report['suspicious_count'] / report['total_scans']) * 100, 2
            )
        
        report['success'] = True
        return report
        
    except Exception as e:
        report['error'] = f"Failed to generate report: {str(e)}"
        return report


def format_report_text(report):
    """
    Formats a summary report dictionary into human-readable text.
    
    Args:
        report (dict): Output from generate_summary_report()
    
    Returns:
        str: Formatted report text
    """
    if not report.get('success'):
        return f"Report Generation Failed: {report.get('error', 'Unknown error')}"
    
    lines = []
    lines.append("=" * 70)
    lines.append("SOC STEGANOGRAPHY DETECTION - ANALYSIS SUMMARY REPORT")
    lines.append("=" * 70)
    lines.append(f"Report Generated: {report['report_timestamp']}")
    lines.append(f"Source CSV: {report['csv_path']}")
    lines.append("")
    
    lines.append("SCAN STATISTICS")
    lines.append("-" * 70)
    lines.append(f"Total Images Scanned:      {report['total_scans']}")
    lines.append(f"Suspicious (Hidden Data):  {report['suspicious_count']} ({report['detection_rate']}%)")
    lines.append(f"Clean (No Hidden Data):    {report['clean_count']}")
    lines.append(f"Analysis Errors:           {report['error_count']}")
    lines.append(f"Total Data Analyzed:       {report['total_size_mb']} MB")
    lines.append("")
    
    # Format breakdown
    if report['format_breakdown']:
        lines.append("IMAGE FORMAT BREAKDOWN")
        lines.append("-" * 70)
        for img_format, count in sorted(report['format_breakdown'].items()):
            lines.append(f"  {img_format}: {count} images")
        lines.append("")
    
    # Hidden messages found
    if report['hidden_messages']:
        lines.append("HIDDEN MESSAGES DETECTED")
        lines.append("-" * 70)
        for idx, msg in enumerate(report['hidden_messages'], 1):
            lines.append(f"\n[{idx}] File: {msg['file_name']}")
            lines.append(f"    Timestamp: {msg['timestamp']}")
            lines.append(f"    Message Length: {msg['message_length']} characters")
            lines.append(f"    Preview: {msg['message_preview']}")
    else:
        lines.append("HIDDEN MESSAGES DETECTED")
        lines.append("-" * 70)
        lines.append("No hidden messages found in scanned images.")
    
    lines.append("")
    lines.append("=" * 70)
    lines.append("END OF REPORT")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def export_report_to_file(report, output_path):
    """
    Exports a formatted report to a text file.
    
    Args:
        report (dict): Output from generate_summary_report()
        output_path (str): Path where report should be saved
    
    Returns:
        dict: Result with success status and error message if any
    """
    result = {
        'success': False,
        'output_path': output_path,
        'error': None
    }
    
    try:
        report_text = format_report_text(report)
        
        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        result['success'] = True
        return result
        
    except Exception as e:
        result['error'] = f"Failed to export report: {str(e)}"
        return result


def compare_csv_logs(csv_paths):
    """
    Compares statistics across multiple CSV log files.
    Useful for tracking detection trends over time.
    
    Args:
        csv_paths (list): List of CSV file paths to compare
    
    Returns:
        dict: Comparison data with statistics for each file
    """
    comparison = {
        'success': False,
        'files_compared': len(csv_paths),
        'reports': [],
        'aggregate': {
            'total_scans': 0,
            'total_suspicious': 0,
            'total_clean': 0,
            'overall_detection_rate': 0.0
        },
        'error': None
    }
    
    try:
        for csv_path in csv_paths:
            report = generate_summary_report(csv_path)
            if report['success']:
                comparison['reports'].append({
                    'file': os.path.basename(csv_path),
                    'total_scans': report['total_scans'],
                    'suspicious_count': report['suspicious_count'],
                    'detection_rate': report['detection_rate']
                })
                
                # Aggregate statistics
                comparison['aggregate']['total_scans'] += report['total_scans']
                comparison['aggregate']['total_suspicious'] += report['suspicious_count']
                comparison['aggregate']['total_clean'] += report['clean_count']
        
        # Calculate overall detection rate
        if comparison['aggregate']['total_scans'] > 0:
            comparison['aggregate']['overall_detection_rate'] = round(
                (comparison['aggregate']['total_suspicious'] / comparison['aggregate']['total_scans']) * 100,
                2
            )
        
        comparison['success'] = True
        return comparison
        
    except Exception as e:
        comparison['error'] = f"Comparison failed: {str(e)}"
        return comparison
