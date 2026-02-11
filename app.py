"""
Module: app.py
Description: The "Auto-Consultant" Dashboard (Competitor Filtering Fixed)
"""
import streamlit as st
import pandas as pd
import re
import os
from scanner import find_business_url, find_competitors, find_social_links
from analyzer import check_ssl, check_seo, detect_tech_stack
from network_scanner import scan_common_ports
from ai_agent import generate_audit_narrative, generate_seo_fixes, identify_industry
from reporter import create_pdf

# --- PAGE CONFIG ---
st.set_page_config(page_title="RevenueRecon", page_icon="🕵️", layout="wide")

st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50;}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
keys = ['scan_complete', 'target_data', 'competitors', 'audit_results', 'ai_report', 'pdf_path']
for k in keys:
    if k not in st.session_state: st.session_state[k] = None
if 'scan_complete' not in st.session_state: st.session_state.scan_complete = False

# --- SIDEBAR ---
with st.sidebar:
    st.title("🕵️ RevenueRecon")
    mode = st.radio("Mode", ["Auto-Discovery", "Direct Audit"])
    if st.button("🔄 Reset / New Search"):
        for k in keys: st.session_state[k] = None
        st.session_state.scan_complete = False
        st.rerun()

# --- INPUT SECTION ---
if not st.session_state.scan_complete:
    st.header("🚀 Target Acquisition")
    target_name, location, manual_url = "", "", ""
    
    if mode == "Auto-Discovery":
        c1, c2 = st.columns(2)
        with c1: target_name = st.text_input("Business Name", placeholder="e.g. Solaire Resort North")
        with c2:
            maps_link = st.text_input("Google Maps Link (Optional)")
            if maps_link:
                loc = re.search(r'place/([^/]+)', maps_link)
                location = loc.group(1).replace('+', ' ').split(',')[0] if loc else ""
                if location: st.success(f"📍 Location: {location}")
            if not location: location = st.text_input("Location/City", placeholder="e.g. Quezon City")
    else:
        c1, c2 = st.columns(2)
        with c1: target_name = st.text_input("Business Name", placeholder="e.g. Solaire Resort")
        with c2: location = st.text_input("Location", placeholder="e.g. Quezon City")
        manual_url = st.text_input("Direct Website URL", placeholder="https://www.solaireresort.com")

    if st.button("⚡ Run Intelligence Scan"):
        # 1. IDENTIFY URL
        url = manual_url
        if not url:
            if not target_name:
                st.error("Please enter a Business Name.")
                st.stop()
            with st.spinner("📡 Triangulating digital assets..."):
                url = find_business_url(target_name, location)
                if not url:
                    st.error("❌ Website not found.")
                    st.stop()
        
        # 2. PERFORM DEEP SCAN
        with st.spinner(f"🛡️ Infiltrating public data for {url}..."):
            with st.spinner("🧠 Analyzing Industry Type..."):
                industry_type = identify_industry(target_name)
                if not industry_type or industry_type == "Direct Audit":
                    industry_type = target_name 
            
            socials = find_social_links(target_name, location)
            ssl = check_ssl(url)
            seo = check_seo(url)
            tech = detect_tech_stack(url)
            ports = scan_common_ports(url)
            
            # C. COMPETITORS (Fixed Logic)
            comps = []
            if location:
                clean_domain = url.replace("https://", "").replace("http://", "").split("/")[0]
                # Updated Call: Passing target_name for filtering
                comps = find_competitors(target_name, industry_type, location, clean_domain)

        # 3. SAVE STATE
        st.session_state.target_data = {"name": target_name, "url": url, "location": location, "socials": socials, "industry": industry_type}
        st.session_state.audit_results = {"ssl": ssl, "seo": seo, "tech": tech, "ports": ports}
        st.session_state.competitors = comps
        st.session_state.scan_complete = True
        st.rerun() 

# --- RESULTS DASHBOARD ---
if st.session_state.scan_complete:
    data = st.session_state.target_data
    audit = st.session_state.audit_results
    
    st.title(f"📊 Audit Report: {data['name']}")
    st.caption(f"Target URL: {data['url']} | Detected Market: **{data.get('industry', 'Unknown')}**")
    
    col1, col2, col3, col4 = st.columns(4)
    score = 100
    if not audit['ssl']: score -= 30
    if not audit['seo'].get('description'): score -= 15
    if "Risk" in str(audit['ports']): score -= 20
    
    col1.metric("Digital Health Score", f"{score}/100")
    col2.metric("SSL Security", "Secure" if audit['ssl'] else "Vulnerable", delta_color="normal" if audit['ssl'] else "inverse")
    col3.metric("Tech Stack", f"{len(audit['tech'])} Detected")
    col4.metric("Social Footprint", f"{len(data['socials'])} Channels")

    tab1, tab2, tab3 = st.tabs(["⚔️ Market Radar", "🛡️ Security & OSINT", "🔧 SEO Engine"])
    
    with tab1:
        st.subheader(f"Top '{data.get('industry')}' Competitors in {data['location']}")
        if st.session_state.competitors:
            df = pd.DataFrame(st.session_state.competitors)
            st.dataframe(
                df,
                column_config={
                    "name": "Competitor Name",
                    "url": st.column_config.LinkColumn("Website")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info(f"No direct '{data.get('industry')}' competitors found.")
            
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📡 Social Profiles")
            if data['socials']:
                for p, l in data['socials'].items(): st.markdown(f"**{p}:** [{l}]({l})")
            else: st.warning("No social media found.")
        with c2:
            st.subheader("🔓 Port Scan")
            if audit['ports']: st.json(audit['ports'])
            else: st.success("No high-risk ports.")
        st.subheader("💻 Tech Stack")
        st.write(", ".join(audit['tech']) if audit['tech'] else "Unknown Framework")

    with tab3:
        st.subheader("SEO Check")
        t = audit['seo'].get('title')
        d = audit['seo'].get('description')
        st.markdown(f"**Title:** {'✅' if t else '❌'} `{t or 'MISSING'}`")
        st.markdown(f"**Desc:** {'✅' if d else '❌'} `{d or 'MISSING'}`")
        
        if st.button("✨ Generate AI SEO Fixes"):
            with st.spinner("Optimizing..."):
                fixes = generate_seo_fixes(data['url'], t, d, data['industry'], data['location'])
                st.code(fixes)

    st.divider()
    st.subheader("📄 Executive Deliverable")
    
    if st.session_state.ai_report is None:
        if st.button("📝 Draft Strategy"):
            with st.spinner("Drafting..."):
                st.session_state.ai_report = generate_audit_narrative(data['name'], data['url'], score, audit['ssl'], audit['ports'], audit['seo'], audit['tech'])
                st.rerun()
    else:
        st.info(st.session_state.ai_report)
        if st.session_state.pdf_path is None:
            st.session_state.pdf_path = create_pdf(data['name'], data['url'], score, st.session_state.ai_report, audit['ssl'], audit['seo'], audit['tech'])
            
        with open(st.session_state.pdf_path, "rb") as f:
            st.download_button("⬇️ Download PDF Report", data=f, file_name=st.session_state.pdf_path, mime="application/pdf")