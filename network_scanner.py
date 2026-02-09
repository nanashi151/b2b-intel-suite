"""
Module: network_scanner.py
Description: Scans target for high-risk open ports using standard sockets.
"""
import socket
from urllib.parse import urlparse

def scan_common_ports(target_url):
    """
    Scans the Top 5 most critical ports for B2B security.
    Returns: A dictionary of {port: status_string}.
    """
    # 1. Extract Hostname (remove https://)
    try:
        hostname = urlparse(target_url).netloc
        # Handle cases where netloc might be empty if user entered "google.com" without https
        if not hostname:
            hostname = target_url.split("/")[0]
    except:
        return {}

    print(f"[?] scanning ports on: {hostname}...")

    # 2. Define High-Risk Ports
    # 21=FTP (Old/Insecure), 22=SSH (Admin Access), 3389=RDP (Remote Desktop)
    ports = [21, 22, 80, 443, 3389]
    results = {}

    # 3. The Scan Loop
    for port in ports:
        try:
            # Create a socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Short timeout (1s) so we don't hang the script
            s.settimeout(1.0)
            
            # Attempt Connection
            result = s.connect_ex((hostname, port))
            
            if result == 0:
                results[port] = "OPEN (Risk)"
            else:
                results[port] = "Closed"
            s.close()
        except:
            results[port] = "Error"
            
    return results