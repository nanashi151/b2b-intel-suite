"""
Module: scanner.py
Description: OSINT Discovery Engine with Competitor "Radar"
"""
from duckduckgo_search import DDGS
import time

def find_business_url(name, location):
    """
    Finds the official website of the target business.
    """
    query = f"{name} {location} official site"
    print(f"[*] Radar: Searching for {query}...")
    
    try:
        results = DDGS().text(query, max_results=3)
        if results:
            # Return the first result that looks like a homepage
            return results[0]['href']
    except Exception as e:
        print(f"[!] Radar Error: {e}")
    return None

def find_competitors(industry, location, user_domain, limit=2):
    """
    Automated Market Radar: Finds top competitors in the area.
    Excludes the user's own domain from results.
    """
    query = f"top rated {industry} in {location}"
    print(f"[*] Radar: Scanning market for '{query}'...")
    
    competitors = []
    try:
        with DDGS() as ddgs:
            # We fetch more results than needed because we have to filter out the user
            results = [r for r in ddgs.text(query, max_results=10)]
            
            for r in results:
                url = r['href']
                title = r['title']
                
                # FILTERS:
                # 1. Skip the user's own website
                if user_domain in url:
                    continue
                # 2. Skip directory sites (Yelp, YellowPages, etc.)
                skip_list = ['yelp', 'yellowpages', 'facebook', 'instagram', 'linkedin', 'tripadvisor']
                if any(x in url for x in skip_list):
                    continue
                    
                competitors.append({"name": title, "url": url})
                
                if len(competitors) >= limit:
                    break
                
    except Exception as e:
        print(f"[!] Competitor Scan Error: {e}")
        
    return competitors