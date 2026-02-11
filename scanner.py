"""
Module: scanner.py
Description: Serper.dev API (The "Bulletproof" Google Search for Agents)
"""
import requests
import json
import streamlit as st

def serper_search(query, num_results=5):
    """
    Searches the entire web using Serper.dev
    """
    if "SERPER_API_KEY" not in st.secrets:
        print("[!] ERROR: Missing SERPER_API_KEY in Secrets!")
        return []

    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "num": num_results
    })
    headers = {
        'X-API-KEY': st.secrets["SERPER_API_KEY"],
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        
        # Serper returns results in an 'organic' list
        if 'organic' in data:
            return data['organic']
        else:
            return []
            
    except Exception as e:
        print(f"[!] Serper API Error: {e}")
        return []

def find_business_url(name, location):
    """
    Finds the official website using Serper.
    """
    query = f"{name} {location} official website"
    print(f"[*] Radar: Searching for {query}...")
    
    # List of sites to IGNORE
    skip_list = [
        'facebook.com', 'instagram.com', 'linkedin.com', 
        'wikipedia.org', 'yelp.com', 'tripadvisor.com', 
        'yellowpages.com', 'youtube.com', 'tiktok.com',
        'glassdoor.com'
    ]

    results = serper_search(query, num_results=5)
    
    for r in results:
        link = r.get('link', '')
        # Filter out social media
        if not any(skip in link for skip in skip_list):
            return link
            
    return None

def find_competitors(industry, location, user_domain, limit=3):
    """
    Finds competitors using Serper.
    """
    query = f"top rated {industry} in {location}"
    competitors = []
    
    results = serper_search(query, num_results=10)
    
    skip_list = ['yelp', 'yellowpages', 'facebook', 'instagram', 'linkedin', 'tripadvisor', 'wikipedia']
    
    for r in results:
        link = r.get('link', '')
        title = r.get('title', 'Unknown Competitor')
        
        if user_domain in link: continue
        if any(x in link for x in skip_list): continue
        
        competitors.append({"name": title, "url": link})
        if len(competitors) >= limit: break
            
    return competitors