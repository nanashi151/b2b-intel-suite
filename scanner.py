"""
Module: scanner.py
Description: Serper.dev API (Web & Places Edition) with Smart Filtering
"""
import requests
import json
import streamlit as st

# --- 1. CORE SEARCH FUNCTIONS ---

def serper_search(query, num_results=5):
    if "SERPER_API_KEY" not in st.secrets:
        return []
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "num": num_results})
    headers = {'X-API-KEY': st.secrets["SERPER_API_KEY"], 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        return response.json().get('organic', [])
    except:
        return []

def serper_places(query, num_results=10):
    if "SERPER_API_KEY" not in st.secrets:
        return []
    url = "https://google.serper.dev/places"
    payload = json.dumps({"q": query, "num": num_results})
    headers = {'X-API-KEY': st.secrets["SERPER_API_KEY"], 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        return response.json().get('places', [])
    except:
        return []

# --- 2. BUSINESS LOCATORS ---

def find_business_url(name, location):
    query = f"{name} {location} official website"
    results = serper_search(query)
    skip = ['facebook', 'instagram', 'linkedin', 'yelp', 'tripadvisor', 'youtube', 'tiktok', 'wikipedia']
    for r in results:
        link = r.get('link', '')
        if not any(x in link for x in skip):
            return link
    return None

def find_social_links(name, location):
    query = f"{name} {location} social media profile"
    results = serper_search(query, num_results=10)
    socials = {}
    targets = {
        "facebook.com": "Facebook", "instagram.com": "Instagram", 
        "linkedin.com": "LinkedIn", "twitter.com": "X (Twitter)",
        "tiktok.com": "TikTok", "youtube.com": "YouTube"
    }
    for r in results:
        link = r.get('link', '')
        for domain, platform in targets.items():
            if domain in link and platform not in socials:
                socials[platform] = link
    return socials

# --- 3. COMPETITOR FINDER (The Aggressive Fix) ---

def find_competitors(target_name, industry, location, user_domain):
    """
    Finds competitors and aggressively removes the user's own business.
    """
    query = f"{industry} in {location}"
    print(f"[*] Searching Places for: {query}")
    
    places = serper_places(query, num_results=15) # Fetch more to allow for filtering
    competitors = []
    
    # Create exclusion keywords from the business name
    # e.g. "Solaire Resort North" -> ["solaire", "resort"]
    exclusion_keywords = target_name.lower().split()[:2] 
    
    for p in places:
        name = p.get('title', 'Unknown')
        website = p.get('website', '') 
        address = p.get('address', '')
        
        # --- FILTERS ---
        
        # 1. Name Filter: If result title contains "Solaire", skip it.
        if any(keyword in name.lower() for keyword in exclusion_keywords):
            continue
            
        # 2. Domain Filter: If website matches user's site, skip it.
        if user_domain and website and (user_domain in website or website in user_domain):
            continue
            
        # 3. Duplicate Filter
        if any(c['name'] == name for c in competitors):
            continue

        competitors.append({"name": name, "url": website or "No Website Listed"})
        
        if len(competitors) >= 4: 
            break
            
    return competitors