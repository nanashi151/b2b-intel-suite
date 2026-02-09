"""
Module: scanner.py
Description: Official Google API Search (Never Blocked)
"""
import requests
import os
import streamlit as st

def google_search_api(query, num_results=3):
    """
    Uses the Official Google Custom Search JSON API.
    Requires GOOGLE_API_KEY and GOOGLE_CX in Secrets.
    """
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
        response = requests.get(url, params=params)
        data = response.json()
        
        # Check for errors (like Quota exceeded)
        if 'error' in data:
            print(f"[!] Google API Error: {data['error']['message']}")
            return []
            
        if 'items' in data:
            return data['items'] # Returns a list of dicts with 'title' and 'link'
            
    except Exception as e:
        print(f"[!] API Request Failed: {e}")
        
    return []

def find_business_url(name, location):
    """
    Finds the official website using Google API.
    """
    query = f"{name} {location} official website"
    print(f"[*] API Radar: Searching for {query}...")
    
    # List of sites to IGNORE
    skip_list = [
        'facebook.com', 'instagram.com', 'linkedin.com', 
        'wikipedia.org', 'yelp.com', 'tripadvisor.com', 
        'yellowpages.com', 'youtube.com', 'tiktok.com'
    ]

    results = google_search_api(query, num_results=5)
    
    for r in results:
        link = r.get('link', '')
        # Filter out social media
        if not any(skip in link for skip in skip_list):
            return link
            
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