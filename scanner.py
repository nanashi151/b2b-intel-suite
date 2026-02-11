"""
Module: scanner.py
Description: Serper.dev API with Multi-Pass Competitor Discovery
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

# --- 3. COMPETITOR FINDER (Multi-Pass Fix) ---

def find_competitors(target_name, industry, location, user_domain):
    """
    Attempts to find competitors using specific industry terms first.
    If none found (likely because the target is the only one),
    falls back to broader terms (e.g. "Integrated Resort" -> "Resort").
    """
    competitors = []
    seen_urls = set()
    
    # Define exclusion keywords (e.g., "Solaire")
    exclusion_keywords = target_name.lower().split()[:2]
    
    # Strategy: Try specific first, then broad
    # 1. "Integrated Resort in Quezon City"
    # 2. "Resort in Quezon City" (The broad fallback)
    search_queries = [
        f"{industry} in {location}",
        f"{industry.split()[-1]} in {location}" # Grabs the last word (e.g. "Resort" from "Integrated Resort")
    ]
    
    print(f"[*] Competitor Radar: Targets {exclusion_keywords}")

    for query in search_queries:
        if len(competitors) >= 4:
            break
            
        print(f"[*] Trying Query: {query}")
        places = serper_places(query, num_results=15)
        
        for p in places:
            name = p.get('title', 'Unknown')
            website = p.get('website', '') 
            
            # --- FILTERS ---
            # 1. Self-Destruct: Skip if name contains target keywords
            if any(keyword in name.lower() for keyword in exclusion_keywords):
                continue
            
            # 2. Domain Filter: Skip if URL matches user
            if user_domain and website and (user_domain in website):
                continue
                
            # 3. Duplicate Filter: Skip if we already have this competitor
            # (Checks both name and website to be safe)
            if website in seen_urls:
                continue
            if any(c['name'] == name for c in competitors):
                continue

            # Add to list
            competitors.append({"name": name, "url": website or "No Website Listed"})
            if website: seen_urls.add(website)
            
            if len(competitors) >= 4: 
                break
    
    return competitors