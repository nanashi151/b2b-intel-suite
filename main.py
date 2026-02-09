"""
Project: B2B Threat & Opportunity Intelligence Tool
Author: [Your Name]
Description: Main entry point. Orchestrates Input -> Search -> Analysis -> Reporting.
"""

import sys
from scanner import find_business_url
from analyzer import check_ssl, check_seo
from ai_agent import generate_website_strategy
from reporter import save_audit_report, save_strategy_proposal # <-- NEW IMPORT

def get_target_input():
    """Collects business data from the user via CLI."""
    print("\n--- B2B INTEL TOOL: INITIALIZING ---")
    
    target_name = input("[?] Target Business Name: ").strip()
    target_location = input("[?] Target Location (City, State): ").strip()
    
    print("[?] Paste 3-4 recent Google Reviews (Press Enter twice to finish):")
    reviews = []
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        reviews.append(line)
        
    return target_name, target_location, " ".join(reviews)

def main():
    # Step 1: Input
    name, location, reviews = get_target_input()

    print(f"\n[+] Processing Intelligence for: {name} ({location})...")

    # Step 2: OSINT Search
    website_url = find_business_url(name, location)

    # Step 3: Branching Logic
    if website_url:
        # BRANCH A: The Auditor
        print(f"\n[+] Official URL found: {website_url}")
        print("-" * 40)
        
        # Security Scan
        print("[+] Running Security Scan...", end=" ")
        is_secure = check_ssl(website_url)
        if is_secure:
            print("PASS (SSL Valid)")
        else:
            print("FAIL (SSL Expired/Missing)")

        # Marketing Scan
        print("[+] Running Marketing Scan...", end=" ")
        seo_text = check_seo(website_url)
        if seo_text:
            print("PASS (SEO Detected)")
            print(f"    -> Meta Description: {seo_text[:60]}...") 
        else:
            print("FAIL (Missing Meta Description)")
            
        print("-" * 40)
        print("[+] Audit Complete. Generating PDF Report...")
        
        # REPORT GENERATION
        filename = save_audit_report(name, website_url, is_secure, seo_text)
        print(f"[SUCCESS] Report saved as: {filename}")
        
    else:
        # BRANCH B: The Architect (Gemini AI)
        print("\n[-] No official website detected.")
        print("[+] Initiating AI Strategy Proposal (Branch B)...")
        print("-" * 40)
        
        # Fallback for empty reviews
        if len(reviews) < 5:
            reviews = "Customer service was great. Best food in town. Highly recommended."
            
        proposal = generate_website_strategy(name, location, reviews)
        print(proposal) # Show in terminal
        
        print("\n[+] Strategy Generated. Saving PDF...")
        filename = save_strategy_proposal(name, proposal)
        print(f"[SUCCESS] Proposal saved as: {filename}")

    print("\n[+] Intelligence run complete.")

if __name__ == "__main__":
    main()