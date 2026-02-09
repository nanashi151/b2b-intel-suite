"""
Module: app.py
Description: Streamlit Web Dashboard for B2B Intelligence Suite.
"""
import streamlit as st
import time
from scanner import find_business_url
from analyzer import check_ssl, check_security_headers, check_email_security, check_seo, extract_emails, detect_tech_stack, extract_socials
from network_scanner import scan_common_ports
from ai_agent import generate_website_strategy, generate_audit_narrative
from reporter import save_audit_report, save_strategy_proposal

# --- PAGE CONFIG ---
st.set_page_config(page_title="B2B Intel Suite", page_icon="🕵️‍♂️", layout="wide")
st.title("🕵️‍♂️ B2B Threat & Opportunity Intelligence Suite")
st.markdown("---")

# --- TABS FOR USER MODE ---
tab1, tab2 = st.tabs(["🏢 Business Search (OSINT)", "🔗 Self-Audit (Direct URL)"])

target_name = ""
target_location = ""
direct_url = ""
run_scan = False
mode = ""

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        target_name = st.text_input("Business Name", placeholder="e.g. Accenture")
    with col2:
        target_location = st.text_input("Location", placeholder="e.g. Manila")
    reviews = st.text_area("Paste Google Reviews (Optional for AI Strategy)", height=100)
    if st.button("🚀 Run OSINT Scan"):
        run_scan = True
        mode = "OSINT"

with tab2:
    direct_url = st.text_input("Enter Website URL", placeholder="https://www.example.com")
    if st.button("🔍 Run Self-Audit"):
        run_scan = True
        mode = "DIRECT"

# --- MAIN LOGIC ---
if run_scan:
    website_url = None
    
    # DETERMINE URL BASED ON MODE
    if mode == "OSINT":
        if not target_name or not target_location:
            st.error("Please provide Name and Location.")
            st.stop()
        with st.spinner(f"Searching digital footprint for {target_name}..."):
            website_url = find_business_url(target_name, target_location)
    
    elif mode == "DIRECT":
        if not direct_url:
            st.error("Please enter a URL.")
            st.stop()
        website_url = direct_url
        target_name = "Target Business" # Placeholder name for direct scans

    # --- BRANCH A: WEBSITE FOUND (AUDIT) ---
    if website_url:
        st.success(f"✅ Target Locked: {website_url}")
        
        # PROGRESS BAR
        my_bar = st.progress(0, text="Initiating Enterprise Scan...")

        with st.spinner("Running Deep Audit (SSL, DNS, SEO, Tech Stack)..."):
            # 1. RUN ALL SCANS
            ssl_valid = check_ssl(website_url)
            headers = check_security_headers(website_url)
            email_sec = check_email_security(website_url)
            ports = scan_common_ports(website_url)
            
            seo = check_seo(website_url)
            emails = extract_emails(website_url)
            tech = detect_tech_stack(website_url)
            socials = extract_socials(website_url)
            
            my_bar.progress(60, text="Consulting AI Analyst...")

        # 2. CALCULATE SCORE
        score = 100
        if not ssl_valid: score -= 30
        if "Risk" in str(ports): score -= 20
        if not seo.get('description'): score -= 10
        if score < 0: score = 0

        # 3. RUN AI NARRATIVE GENERATION
        with st.spinner("Drafting Executive Summary..."):
            ai_report = generate_audit_narrative(target_name, website_url, score, ssl_valid, ports, seo, tech)
            my_bar.progress(100, text="Analysis Complete.")

        # --- DASHBOARD UI ---
        # KPI ROW
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Security Score", f"{score}/100", delta_color="normal" if score > 70 else "inverse")
        k2.metric("SSL Status", "Secure" if ssl_valid else "Vulnerable", delta_color="normal" if ssl_valid else "inverse")
        k3.metric("Tech Stack", f"{len(tech)} Detected", help=str(tech))
        k4.metric("Leads Found", f"{len(emails)} Emails")

        st.divider()

        # AI EXECUTIVE SUMMARY SECTION
        st.subheader("📝 Executive AI Analysis")
        st.info(ai_report)

        # DETAILED COLUMNS
        with st.expander("See Raw Technical Data"):
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("🛡 Security Analysis")
                st.write("**HTTP Security Headers:**")
                st.json(headers)
                st.write("**Email Security (DNS):**")
                st.json(email_sec)
                st.write("**Port Scan:**")
                st.json(ports)

            with c2:
                st.subheader("📢 Marketing & Sales Intel")
                st.write("**SEO Health:**")
                st.json(seo)
                st.write("**Tech Stack:**")
                for item in tech: st.caption(f"🔹 {item}")
                st.write("**Social & Contact:**")
                if socials: st.write(socials)
                if emails: st.write(emails)

        # GENERATE PDF (Passing ALL data now)
        pdf_file = save_audit_report(
            target_name, 
            website_url, 
            score, 
            ai_report, 
            ssl_valid, 
            seo, 
            ports,
            headers,     # <--- Passed to PDF
            email_sec,   # <--- Passed to PDF
            tech,        # <--- Passed to PDF
            emails,      # <--- Passed to PDF
            socials      # <--- Passed to PDF
        )
            
        # DOWNLOAD BUTTON
        with open(pdf_file, "rb") as file:
            st.download_button(
                label="📥 Download Executive Report (PDF)",
                data=file,
                file_name=pdf_file,
                mime="application/pdf"
            )

    # --- BRANCH B: NO WEBSITE (OSINT ONLY) ---
    else:
        st.warning("🔻 No Official Website Detected.")
        if mode == "OSINT":
            st.info("Generating AI Strategy...")
            
            # AI Strategy Generation
            if len(reviews) < 5: reviews = "Standard service."
            strategy = generate_website_strategy(target_name, target_location, reviews)
            
            st.markdown("### 🤖 AI-Generated Proposal")
            st.text_area("Strategy Preview", value=strategy, height=300)
            
            # GENERATE PDF
            pdf_file = save_strategy_proposal(target_name, strategy)
            
            # DOWNLOAD BUTTON
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="📥 Download Strategy Proposal (PDF)",
                    data=file,
                    file_name=pdf_file,
                    mime="application/pdf"
                )