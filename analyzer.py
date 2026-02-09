"""
Module: analyzer.py
Description: Security, Marketing, and Contact Info Analysis.
"""

import socket
import ssl
import requests
import re  # <-- NEW: Regex for finding emails
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def check_ssl(url):
    """Checks if the target URL has a valid SSL certificate."""
    try:
        hostname = urlparse(url).netloc
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                return True
    except Exception:
        return False

def check_seo(url):
    """Checks for Meta Description."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200: return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'): return meta['content']
            
        meta_og = soup.find('meta', property='og:description')
        if meta_og and meta_og.get('content'): return meta_og['content']
    except:
        return None
    return None

def extract_emails(url): # <-- NEW FUNCTION
    """
    Scrapes the homepage for email addresses.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Shorter timeout to keep it snappy
        response = requests.get(url, headers=headers, timeout=5)
        
        # Regex pattern for standard emails
        # Looks for: text + @ + text + . + text
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        found_emails = set(re.findall(email_pattern, response.text))
        
        # Filter out garbage (e.g., "name@2x.png" or "user@example.com")
        clean_emails = []
        for email in found_emails:
            if not email.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                clean_emails.append(email)
                
        return list(clean_emails)
        
    except Exception as e:
        return []