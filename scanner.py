"""
Module: scanner.py
Description: Official Google API Search (Debug Version)
"""
import requests
import streamlit as st

def google_search_api(query, num_results=5):
    """
    Uses the Official Google Custom Search JSON API.
    """
    # 1. Check if Secrets exist
    if "GOOGLE_API_KEY" not in st.secrets or "GOOGLE_CX" not in st.secrets:
        print("[!] ERROR: Missing Google API Secrets in Streamlit!")
        return []

    api_key = st.secrets["GOOGLE_API_KEY"]
    cx = st.secrets["GOOGLE_CX"]
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cx,
        'q': query,
        'num': num_results
    }
    
    try:
        print(f"[*] API Request: Searching for '{query}'...")
        response = requests.get(url, params=params)
        data = response.json()
        
        # 2. Check for API Errors (Quota, Invalid Key, etc.)
        if 'error' in data:
            error_msg = data['error']['message']
            print(f"[!] API ERROR: {error_msg}")
            return []
            
        # 3. Return Items
        if 'items' in data:
            print(f"[*] API Success: Found {len(data['items'])} results.")
            return data['items']
        else:
            print("[!] API Warning: No 'items' found in response.")
            return []
            
    except Exception as e:
        print(f"[!] Network Error: {e}")
        return []

def find_business_url(name, location):
    """
    Finds the official website using Google API.
    """
    # Create a specific query
    query = f"{name} {location} official website"
    
    # List of sites to IGNORE
    skip_list = [
        'facebook.com', 'instagram.com', 'linkedin.com', 
        'wikipedia.org', 'yelp.com', 'tripadvisor.com', 
        'yellowpages.com', 'youtube.com', 'tiktok.com'
    ]

    results = google_search_api(query, num_results=5)
    
    for r in results:
        link = r.get('link', '')
        title = r.get('title', '')
        print(f"[*] Checking Result: {title} ({link})")
        
        # Filter out social media
        if not any(skip in link for skip in skip_list):
            print(f"[*] MATCH FOUND: {link}")
            return link
            
    print("[!] No valid website found in top 5 results.")
    return None

def find_competitors(industry, location, user_domain, limit=3):
    """
    Finds competitors using Google API.
    """
    query = f"top rated {industry} in {location}"
    competitors = []
    
    results = google_search_api(query, num_results=10)
    
    skip_list = ['yelp', 'yellowpages', 'facebook', 'instagram', 'linkedin', 'tripadvisor', 'wikipedia']
    
    for r in results:
        link = r.get('link', '')
        title = r.get('title', 'Unknown Competitor')
        
        if user_domain in link: continue
        if any(x in link for x in skip_list): continue
        
        competitors.append({"name": title, "url": link})
        if len(competitors) >= limit: break
            
    return competitors