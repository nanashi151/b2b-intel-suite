"""
Module: analyzer.py
Description: Enterprise-grade analysis (Security, SEO, Leads).
"""
import socket
import ssl
import requests
import re
import dns.resolver # New library for DNS checks
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# --- SECURITY FUNCTIONS ---
def check_ssl(url):
    """Checks for valid SSL/TLS certificate."""
    try:
        hostname = urlparse(url).netloc
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                return True
    except:
        return False

def check_security_headers(url):
    """
    [BitSight Feature] Checks for security headers that prevent XSS and Clickjacking.
    """
    try:
        response = requests.get(url, timeout=3)
        headers = response.headers
        results = {
            "X-Frame-Options": "MISSING (Clickjacking Risk)" if "X-Frame-Options" not in headers else "PASS",
            "Strict-Transport-Security": "MISSING (Man-in-Middle Risk)" if "Strict-Transport-Security" not in headers else "PASS",
            "Content-Security-Policy": "MISSING (XSS Risk)" if "Content-Security-Policy" not in headers else "PASS"
        }
        return results
    except:
        return {}

def check_email_security(url):
    """
    [SecurityScorecard Feature] Checks DNS records for SPF and DMARC (Email Security).
    """
    domain = urlparse(url).netloc.replace("www.", "")
    results = {"SPF": "MISSING", "DMARC": "MISSING"}
    
    try:
        # Check SPF
        answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in answers:
            if "v=spf1" in str(rdata):
                results["SPF"] = "PASS"
    except:
        pass

    try:
        # Check DMARC
        answers = dns.resolver.resolve(f"_dmarc.{domain}", 'TXT')
        for rdata in answers:
            if "v=DMARC1" in str(rdata):
                results["DMARC"] = "PASS"
    except:
        pass
        
    return results

# --- MARKETING FUNCTIONS ---
def check_seo(url):
    """[SEMrush Feature] Checks Meta Description, Title, and H1."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200: return {}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            "title": soup.title.string if soup.title else "MISSING",
            "description": None,
            "h1": soup.find('h1').get_text().strip() if soup.find('h1') else "MISSING",
            "viewport": "MISSING" # Mobile readiness
        }
        
        # Check Description
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'): data['description'] = meta['content']
        else:
            meta_og = soup.find('meta', property='og:description')
            if meta_og and meta_og.get('content'): data['description'] = meta_og['content']
            
        # Check Mobile Viewport
        if soup.find('meta', attrs={'name': 'viewport'}):
            data['viewport'] = "PASS (Mobile Optimized)"
            
        return data
    except:
        return {}

# --- SALES INTEL FUNCTIONS ---
def extract_emails(url):
    """[ZoomInfo Feature] Scrapes emails."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        found = set(re.findall(email_pattern, response.text))
        return [e for e in found if not e.endswith(('.png', '.jpg', '.gif'))]
    except:
        return []

def detect_tech_stack(url):
    """[BuiltWith Feature] Detects CMS (WordPress, Shopify, etc)."""
    try:
        response = requests.get(url, timeout=5)
        html = response.text.lower()
        stack = []
        
        if "wp-content" in html: stack.append("WordPress")
        if "shopify" in html: stack.append("Shopify")
        if "wix.com" in html: stack.append("Wix")
        if "squarespace" in html: stack.append("Squarespace")
        if "bootstrap" in html: stack.append("Bootstrap")
        if "react" in html: stack.append("React.js")
        
        return stack if stack else ["Unknown HTML/Custom"]
    except:
        return []

def extract_socials(url):
    """[Apollo Feature] Finds LinkedIn, Facebook, Twitter links."""
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        socials = []
        
        platforms = ['linkedin.com', 'facebook.com', 'twitter.com', 'instagram.com', 'youtube.com']
        
        for link in links:
            for platform in platforms:
                if platform in link and link not in socials:
                    socials.append(link)
        return list(set(socials)) # Remove duplicates
    except:
        return []