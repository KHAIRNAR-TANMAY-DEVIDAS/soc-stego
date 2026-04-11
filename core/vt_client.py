"""
VirusTotal REST API Client Module for SOC Steganography Tool
Handles querying the VT v3 API for file hashes and extracted payloads.
"""

import requests
import hashlib
import sys
import os

# Add parent directory to path to allow direct testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VT_API_KEY, VT_API_URL

def query_virustotal_hash(hash_str, api_key=None):
    """
    Query VT for a specific hash string.
    Returns structured results: {'success': bool, 'data': dict, 'error': str}
    """
    key = api_key or VT_API_KEY
    result = {'success': False, 'data': None, 'error': None, 'status_code': None}
    
    if not key or key == "":
        result['error'] = "Missing VT API Key. Please add it to config.py"
        return result
        
    headers = {"x-apikey": key}
    url = f"{VT_API_URL}{hash_str}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        result['status_code'] = response.status_code
        
        if response.status_code == 200:
            json_response = response.json()
            stats = json_response.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
            
            # Extract key stats
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            undetected = stats.get('undetected', 0)
            harmless = stats.get('harmless', 0)
            
            total = malicious + suspicious + undetected + harmless
            
            result['success'] = True
            result['data'] = {
                'malicious': malicious,
                'suspicious': suspicious,
                'undetected': undetected,
                'harmless': harmless,
                'total': total,
                'is_threat': malicious > 0 or suspicious > 0
            }
        elif response.status_code == 404:
            result['error'] = "File hash not found in VirusTotal database"
        elif response.status_code == 429:
            result['error'] = "API Rate Limit Exceeded (4/min on free tier)"
        elif response.status_code == 401:
            result['error'] = "Invalid API Key"
        else:
            result['error'] = f"API Error: HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        result['error'] = "Connection timeout checking VirusTotal"
    except requests.exceptions.RequestException as e:
        result['error'] = f"Network error: {str(e)}"
    except Exception as e:
        result['error'] = f"Unexpected VT error: {str(e)}"
        
    return result

def hash_payload_string(payload_string):
    """Generates a SHA-256 hash of extracted string payload for VT scanning."""
    if not payload_string:
        return None
    return hashlib.sha256(payload_string.encode('utf-8')).hexdigest()
