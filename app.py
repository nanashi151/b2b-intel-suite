"""
Module: app.py
Description: The "Auto-Consultant" Dashboard (Final Edition)
"""
import streamlit as st
import pandas as pd
import re
from scanner import find_business_url, find_competitors
from analyzer import check_ssl, check_seo, detect_tech_stack
from network_scanner import scan_common_ports
from ai_agent import generate_audit_narrative, generate_seo_fixes
from reporter import create_pdf  # Correctly imports the PDF engine

# --- HELPER: GOOGLE MAPS PARSER ---
def extract_location_from_maps(url):
    """Extracts city/area from Google Maps URL"""
    if not url: return ""
    try:
        match = re.search(r'place/([^/]+)', url)
        if match:
            return match.group(1).replace('+', ' ').split(',')[0]
    except:
        pass
    return ""

# --- PAGE CONFIG ---
st.set_page_config(page_title="RevenueRecon", page_icon="🚀", layout="wide")
st.title("🚀 RevenueRecon: Automated Growth Engine")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    mode = st.radio("Select Operation Mode", ["🏢 Business Search (Auto-Discovery)", "🔗 Self-Audit (Direct URL)"])
    st.info("💡 **Pro Tip:** If Auto-Discovery finds the US site, use the Manual Override below!")

# --- INPUT VARIABLES ---
target_name = ""
maps_link = ""
direct_url = ""
run_scan = False
location_query = ""

# --- MODE 1: BUSINESS SEARCH ---
if mode == "🏢 Business Search (Auto-Discovery)":
    c1, c2 = st.columns(2)
    with c1:
        target_name = st.text_input("Business Name", placeholder="e.g. Accenture Philippines")
    with c2:
        maps_link = st.text_input("Google Maps Link", placeholder="Paste the full maps link here...")
    
    if maps_link:
        location_query = extract_location_from_maps(maps_link)
        if location_query:
            st.success(f"📍 Detected Location: **{location_query}**")
        else:
            st.warning("⚠️ Could not read location. (Scan will still proceed)")
            location_query = st.text_input("Enter City/Area manually:", placeholder="e.g. Manila")
    
    if st.button("🚀 Launch Scan"):
        run_scan = True

# --- MODE 2: SELF AUDIT ---
elif mode == "🔗 Self-Audit (Direct URL)":
    direct_url = st.text_input("Enter Website URL", placeholder="https://www.example.com")
    location_query = st.text_input("Target Location", placeholder="e.g. Quezon City")
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
        
        search_loc = location_query if location_query else ""
        
        # Use Serper Scanner
        with st.spinner(f"📡 Locating digital assets for {target_name}..."):
            user_url = find_business_url(target_name, search_loc)

        # Smart Fallback
        if not user_url:
            st.warning(f"⚠️ We couldn't auto-detect a website for '{target_name}'.")
            st.info("They might not have one (Sales Opportunity!), or the search failed.")
            manual_override = st.text_input("👇 If they have a website, paste it here:", placeholder="https://...")
            if manual_override:
                user_url = manual_override
                st.success(f"✅ Manual Override Accepted. Scanning {user_url}...")
            else:
                st.stop()
        else:
            st.success(f"✅ Target Locked: {user_url}")
            # --- OVERRIDE OPTION FOR WRONG TARGETS ---
            st.caption(f"Is {user_url} the wrong site? (e.g. US instead of PH?)")
            manual_correction = st.text_input("Correct the URL here if needed:", placeholder="Paste correct URL...")
            if manual_correction:
                user_url = manual_correction
                st.success(f"✅ Correction Applied. Scanning {user_url}...")

    # 2. COMPETITOR RADAR
    comp_data = []
    if location_query:
        industry_guess = target_name.split(' ')[-1] 
        with st.spinner(f"⚔️ Radar Active: Scanning competitors in {location_query}..."):
            domain_clean = user_url.replace("https://", "").replace("http://", "").split("/")[0]
            competitors = find_competitors(industry_guess, location_query, domain_clean)
            
            for comp in competitors:
                c_ssl = check_ssl(comp['url'])
                c_tech = detect_tech_stack(comp['url'])
                c_score = 90 if c_ssl else 40 
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
    progress.progress(100, text="Analysis Complete.")

    # Scoring
    score = 100
    if not ssl: score -= 30
    if not seo.get('description'): score -= 15
    if "Risk" in str(ports): score -= 20
    if score < 0: score = 0

    # --- DISPLAY RESULTS ---
    if comp_data:
        st.subheader("⚔️ Market Battlefield")
        all_data = [{"Name": f"{target_name} (You)", "URL": user_url, "Score": score, "Tech": len(tech), "SSL": "✅" if ssl else "❌"}] + comp_data
        df = pd.DataFrame(all_data)
        st.dataframe(df.style.highlight_max(axis=0, subset=['Score'], color='#d4edda'), use_container_width=True)

    st.divider()

    # --- SEO SECTION ---
    st.subheader("🛠️ Automated SEO Fixer")
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Current Meta Data")
        if not seo.get('title'): st.error("Title: Missing ❌")
        else: st.info(f"Title: {seo.get('title')}")
        if not seo.get('description'): st.error("Desc: Missing ❌")
        else: st.info(f"Desc: {seo.get('description')}")
    
    with col2:
        st.caption("AI Optimization")
        if st.button("✨ Generate Google-Ranking Tags"):
            with st.spinner("Rewriting content..."):
                fixed_content = generate_seo_fixes(user_url, seo.get('title'), seo.get('description'), target_name, location_query)
                st.code(fixed_content, language="markdown")

    st.divider()

    # --- PDF REPORT SECTION ---
    st.subheader("📄 Executive Audit Report")
    
    ai_summary = ""
    with st.spinner("Drafting Strategic Analysis..."):
        ai_summary = generate_audit_narrative(target_name, user_url, score, ssl, ports, seo, tech)
    
    st.info(ai_summary)
    
    # DOWNLOAD BUTTON
    if st.button("⬇️ Download PDF Report"):
        with st.spinner("Rendering PDF Document..."):
            try:
                pdf_filename = create_pdf(target_name, user_url, score, ai_summary, ssl, seo, tech)
                with open(pdf_filename, "rb") as f:
                    st.download_button(
                        label="Click to Download PDF",
                        data=f,
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"PDF Generation Failed: {e}")