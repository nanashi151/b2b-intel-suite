"""
Module: app.py
Description: The "Auto-Consultant" Dashboard
"""
import streamlit as st
import pandas as pd
import re
from scanner import find_business_url, find_competitors
from analyzer import check_ssl, check_seo, detect_tech_stack
from network_scanner import scan_common_ports
from ai_agent import generate_audit_narrative, generate_seo_fixes
from reporter import save_audit_report

# --- HELPER: GOOGLE MAPS PARSER ---
def extract_location_from_maps(url):
    """
    Extracts the city/area from a Google Maps URL.
    Example: .../place/Dental+Clinic+Manila/@... -> Returns "Dental Clinic Manila"
    """
    try:
        # Regex to find text between 'place/' and the next '/'
        match = re.search(r'place/([^/]+)', url)
        if match:
            # Replace '+' with spaces to get readable text
            return match.group(1).replace('+', ' ')
    except:
        pass
    return "Unknown Location"

# --- PAGE CONFIG ---
st.set_page_config(page_title="RevenueRecon", page_icon="🚀", layout="wide")
st.title("🚀 RevenueRecon: Automated Growth Engine")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    mode = st.radio("Select Operation Mode", ["🏢 Business Search (Auto-Discovery)", "🔗 Self-Audit (Direct URL)"])
    st.info("💡 **New Feature:** Paste a Google Maps link to auto-detect location and competitors.")

# --- INPUT VARIABLES ---
target_name = ""
maps_link = ""
direct_url = ""
run_scan = False
location_query = "" # This will hold the extracted location

# --- MODE 1: BUSINESS SEARCH ---
if mode == "🏢 Business Search (Auto-Discovery)":
    c1, c2 = st.columns(2)
    with c1:
        target_name = st.text_input("Business Name", placeholder="e.g. Dr. Smile Dental")
    with c2:
        maps_link = st.text_input("Google Maps Link", placeholder="Paste the full maps link here...")
    
    # Auto-extract location if link is provided
    if maps_link:
        location_query = extract_location_from_maps(maps_link)
        st.caption(f"📍 Detected Search Area: **{location_query}**")
    
    if st.button("🚀 Launch Scan"):
        run_scan = True

# --- MODE 2: SELF AUDIT ---
elif mode == "🔗 Self-Audit (Direct URL)":
    direct_url = st.text_input("Enter Website URL", placeholder="https://www.example.com")
    location_query = st.text_input("Target Location (For Competitor Comparison)", placeholder="e.g. Chicago")
    if st.button("🔍 Run Audit"):
        run_scan = True
        target_name = "Direct Client"

# --- MAIN LOGIC ---
if run_scan:
    # 1. FIND THE URL
    user_url = None
    if direct_url:
        user_url = direct_url
    else:
        if not target_name:
            st.error("Please enter a Business Name.")
            st.stop()
        # Use the extracted location from Maps
        search_loc = location_query if location_query else "Global"
        with st.spinner(f"📡 Locating digital assets for {target_name} in {search_loc}..."):
            user_url = find_business_url(target_name, search_loc)

    if not user_url:
        st.error("❌ Could not find a website. Try Direct Mode.")
        st.stop()

    st.success(f"✅ Target Locked: {user_url}")

    # 2. COMPETITOR RADAR
    comp_data = []
    # If we have a location (from maps or input), run the radar
    if location_query:
        # Guess industry from name (Simple heuristic)
        industry_guess = target_name.split(' ')[-1] # Takes last word as industry "Dental", "Law", etc.
        
        with st.spinner(f"⚔️ Radar Active: Scanning for top-rated competitors in {location_query}..."):
            # Clean domain for filtering
            domain_clean = user_url.replace("https://", "").replace("http://", "").split("/")[0]
            competitors = find_competitors(industry_guess, location_query, domain_clean)
            
            # Lite Scan on Competitors
            for comp in competitors:
                c_ssl = check_ssl(comp['url'])
                c_tech = detect_tech_stack(comp['url'])
                c_score = 90 if c_ssl else 40 # Simple score for speed
                comp_data.append({
                    "Name": comp['name'],
                    "URL": comp['url'],
                    "Score": c_score,
                    "Tech": len(c_tech),
                    "SSL": "✅" if c_ssl else "❌"
                })

    # 3. DEEP USER SCAN
    progress = st.progress(0, text="Deep Audit in progress...")
    
    ssl = check_ssl(user_url)
    progress.progress(30, text="Checking Security Protocols...")
    seo = check_seo(user_url)
    progress.progress(60, text="Analyzing Content Strategy...")
    tech = detect_tech_stack(user_url)
    ports = scan_common_ports(user_url)
    progress.progress(100, text="Done.")

    # Scoring
    score = 100
    if not ssl: score -= 30
    if not seo.get('description'): score -= 15
    if "Risk" in str(ports): score -= 20
    if score < 0: score = 0

    # --- DISPLAY: BATTLEFIELD ---
    if comp_data:
        st.subheader("⚔️ Market Battlefield")
        # Add User
        all_data = [{"Name": f"{target_name} (You)", "URL": user_url, "Score": score, "Tech": len(tech), "SSL": "✅" if ssl else "❌"}] + comp_data
        df = pd.DataFrame(all_data)
        st.dataframe(df.style.highlight_max(axis=0, subset=['Score'], color='#d4edda'), use_container_width=True)

    st.divider()

    # --- DISPLAY: SEO AUTO-FIXER (The "Consultant" Feature) ---
    st.subheader("🛠️ Automated SEO Fixer")
    
    col1, col2 = st.columns(2)
    with col1:
        st.error(f"Current Title: {seo.get('title')}")
        st.error(f"Current Desc: {seo.get('description')}")
    
    with col2:
        if st.button("✨ Generate AI Optimization"):
            with st.spinner("Rewriting content for Google dominance..."):
                # Call the new AI function
                fixed_content = generate_seo_fixes(user_url, seo.get('title'), seo.get('description'), target_name, location_query)
                st.success("Optimization Complete!")
                st.code(fixed_content, language="markdown")

    st.divider()

    # --- EXECUTIVE REPORT ---
    with st.spinner("Drafting PDF Report..."):
        ai_summary = generate_audit_narrative(target_name, user_url, score, ssl, ports, seo, tech)
        
    st.info(ai_summary)
    
    # Save PDF (Simplified call)
    # pdf_file = save_audit_report(...) # Connect to reporter.py
    # st.download_button(...)