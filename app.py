"""
Module: app.py
Description: The "Auto-Consultant" Dashboard (Maps Restored & AI Fixed)
"""
import streamlit as st
import pandas as pd
import re
import os
from scanner import find_business_url, find_competitors, find_social_links
from analyzer import check_ssl, check_seo, detect_tech_stack
from network_scanner import scan_common_ports
from ai_agent import generate_audit_narrative, generate_seo_fixes
from reporter import create_pdf

# --- HELPER: GOOGLE MAPS PARSER ---
def extract_location_from_maps(url):
    if not url: return ""
    try:
        match = re.search(r'place/([^/]+)', url)
        if match:
            return match.group(1).replace('+', ' ').split(',')[0]
    except:
        pass
    return ""

# --- PAGE CONFIG ---
st.set_page_config(page_title="RevenueRecon", page_icon="🕵️", layout="wide")

# --- CSS FOR "HACKER" VIBE ---
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50;}
    .risk-card {background-color: #fff0f0; padding: 15px; border-radius: 10px; border-left: 5px solid #FF5252;}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
keys = ['scan_complete', 'target_data', 'competitors', 'audit_results', 'ai_report', 'pdf_path']
for k in keys:
    if k not in st.session_state:
        st.session_state[k] = None
if 'scan_complete' not in st.session_state: st.session_state.scan_complete = False

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🕵️ RevenueRecon")
    mode = st.radio("Mode", ["Auto-Discovery", "Direct Audit"])
    
    if st.button("🔄 Reset / New Search"):
        for k in keys: st.session_state[k] = None
        st.session_state.scan_complete = False
        st.rerun()

# --- INPUT SECTION (Only shows if scan NOT complete) ---
if not st.session_state.scan_complete:
    st.header("🚀 Target Acquisition")
    
    target_name = ""
    location = ""
    manual_url = ""
    
    if mode == "Auto-Discovery":
        c1, c2 = st.columns(2)
        with c1:
            target_name = st.text_input("Business Name", placeholder="e.g. Accenture Philippines")
        with c2:
            # RESTORED: Google Maps Link Input
            maps_link = st.text_input("Google Maps Link (Optional)", placeholder="Paste Maps URL to auto-detect city...")
            
            if maps_link:
                detected_loc = extract_location_from_maps(maps_link)
                if detected_loc:
                    st.success(f"📍 Location Detected: {detected_loc}")
                    location = detected_loc
                else:
                    location = st.text_input("Location/City", placeholder="e.g. Manila")
            else:
                location = st.text_input("Location/City", placeholder="e.g. Manila")

    else:
        manual_url = st.text_input("Direct Website URL", placeholder="https://example.com")
        location = st.text_input("Location (For Competitor Analysis)")
        target_name = "Direct Audit"

    # --- EXECUTION LOGIC ---
    if st.button("⚡ Run Intelligence Scan"):
        # 1. IDENTIFY URL
        url = manual_url
        if not url:
            with st.spinner("📡 Triangulating digital assets..."):
                url = find_business_url(target_name, location)
                if not url:
                    st.error("❌ No official website found. Try 'Direct Audit' mode.")
                    st.stop()
        
        # 2. PERFORM DEEP SCAN
        with st.spinner(f"🛡️ Infiltrating public data for {url}..."):
            socials = find_social_links(target_name, location)
            ssl = check_ssl(url)
            seo = check_seo(url)
            tech = detect_tech_stack(url)
            ports = scan_common_ports(url)
            
            comps = []
            if location:
                clean_domain = url.replace("https://", "").split("/")[0]
                comps = find_competitors(target_name, location, clean_domain)

        # 3. SAVE TO STATE
        st.session_state.target_data = {
            "name": target_name, "url": url, "location": location,
            "socials": socials
        }
        st.session_state.audit_results = {
            "ssl": ssl, "seo": seo, "tech": tech, "ports": ports
        }
        st.session_state.competitors = comps
        st.session_state.scan_complete = True
        st.rerun() 

# --- RESULTS DASHBOARD ---
if st.session_state.scan_complete:
    data = st.session_state.target_data
    audit = st.session_state.audit_results
    
    st.title(f"📊 Audit Report: {data['name']}")
    st.caption(f"Target URL: {data['url']}")
    
    # METRICS
    col1, col2, col3, col4 = st.columns(4)
    score = 100
    if not audit['ssl']: score -= 30
    if not audit['seo'].get('description'): score -= 15
    if "Risk" in str(audit['ports']): score -= 20
    
    col1.metric("Digital Health Score", f"{score}/100")
    col2.metric("SSL Security", "Secure" if audit['ssl'] else "Vulnerable", delta_color="normal" if audit['ssl'] else "inverse")
    col3.metric("Tech Stack", f"{len(audit['tech'])} Detected")
    col4.metric("Social Footprint", f"{len(data['socials'])} Channels")

    # TABS
    tab1, tab2, tab3 = st.tabs(["⚔️ Market Radar", "🛡️ Security & OSINT", "🔧 SEO Engine"])
    
    with tab1:
        st.subheader("Competitor Landscape")
        if st.session_state.competitors:
            comp_rows = []
            for c in st.session_state.competitors:
                comp_rows.append({"Competitor": c['name'], "Website": c['url'], "Threat Level": "High"})
            st.dataframe(pd.DataFrame(comp_rows), use_container_width=True)
        else:
            st.info("No direct local competitors detected.")
            
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📡 OSINT: Social Profiles")
            if data['socials']:
                for platform, link in data['socials'].items():
                    st.markdown(f"**{platform}:** [{link}]({link})")
            else:
                st.warning("No social media accounts found.")
        
        with c2:
            st.subheader("🔓 Port Scan Results")
            if audit['ports']:
                st.json(audit['ports'])
            else:
                st.success("No high-risk ports exposed.")
                
        st.subheader("💻 Technology Stack")
        st.write(", ".join(audit['tech']) if audit['tech'] else "No specific framework detected.")

    with tab3:
        st.subheader("SEO Metadata Check")
        t_check = "✅" if audit['seo'].get('title') else "❌"
        d_check = "✅" if audit['seo'].get('description') else "❌"
        
        st.markdown(f"**Title Tag:** {t_check} `{audit['seo'].get('title', 'MISSING')}`")
        st.markdown(f"**Meta Description:** {d_check} `{audit['seo'].get('description', 'MISSING')}`")
        
        if st.button("✨ Generate AI SEO Fixes"):
            with st.spinner("Consulting Gemini..."):
                fixes = generate_seo_fixes(data['url'], audit['seo'].get('title'), audit['seo'].get('description'), data['name'], data['location'])
                st.code(fixes)

    st.divider()

    # --- REPORT GENERATION ---
    st.subheader("📄 Executive Deliverable")
    
    # 1. Generate Text (If not already done)
    if st.session_state.ai_report is None:
        if st.button("📝 Draft Executive Analysis"):
            with st.spinner("Drafting Strategy..."):
                st.session_state.ai_report = generate_audit_narrative(
                    data['name'], data['url'], score, audit['ssl'], 
                    audit['ports'], audit['seo'], audit['tech']
                )
                st.rerun()
    else:
        # Show Text
        st.info(st.session_state.ai_report)
        
        # 2. Generate PDF (If text exists)
        if st.session_state.pdf_path is None:
            st.session_state.pdf_path = create_pdf(
                data['name'], data['url'], score, st.session_state.ai_report, 
                audit['ssl'], audit['seo'], audit['tech']
            )
            
        # 3. Download Button (Persistent)
        if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
            with open(st.session_state.pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=f,
                    file_name=st.session_state.pdf_path,
                    mime="application/pdf"
                )