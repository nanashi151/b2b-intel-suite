import streamlit as st
import time
from scanner import find_business_url
from analyzer import check_ssl, check_security_headers, check_email_security, check_seo, extract_emails, detect_tech_stack, extract_socials
from network_scanner import scan_common_ports
from ai_agent import generate_website_strategy
from reporter import save_audit_report, save_strategy_proposal

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
        target_name = "Self-Audit Target" # Placeholder name

    # --- BRANCH A: WEBSITE FOUND (AUDIT) ---
    if website_url:
        st.success(f"✅ Target Locked: {website_url}")
        
        # PROGRESS BAR
        my_bar = st.progress(0, text="Initiating Enterprise Scan...")

        with st.spinner("Running Deep Audit (SSL, DNS, SEO, Tech Stack)..."):
            # 1. RUN ALL SCANS
            ssl_valid = check_ssl(website_url)
            headers_status = check_security_headers(website_url)
            email_security = check_email_security(website_url)
            open_ports = scan_common_ports(website_url)
            
            seo_data = check_seo(website_url)
            emails = extract_emails(website_url)
            tech_stack = detect_tech_stack(website_url)
            socials = extract_socials(website_url)
            
            my_bar.progress(100, text="Analysis Complete.")

        # --- SCORE ALGORITHM ---
        score = 100
        if not ssl_valid: score -= 20
        if "MISSING" in headers_status.values(): score -= 10
        if email_security["SPF"] == "MISSING": score -= 10
        if email_security["DMARC"] == "MISSING": score -= 10
        if "Risk" in str(open_ports): score -= 15
        if not seo_data.get('description'): score -= 10
        if seo_data.get('h1') == "MISSING": score -= 5
        if score < 0: score = 0

        # --- DASHBOARD UI ---
        # KPI ROW
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Security Score", f"{score}/100", delta_color="normal" if score > 70 else "inverse")
        k2.metric("SSL Status", "Secure" if ssl_valid else "Vulnerable", delta_color="normal" if ssl_valid else "inverse")
        k3.metric("Tech Stack", f"{len(tech_stack)} Detected", help=str(tech_stack))
        k4.metric("Leads Found", f"{len(emails)} Emails")

        st.divider()

        # DETAILED COLUMNS
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("🛡 Security Analysis")
            st.write("**HTTP Security Headers:**")
            st.json(headers_status)
            st.write("**Email Security (DNS):**")
            st.json(email_security)
            st.write("**Port Scan:**")
            st.json(open_ports)

        with c2:
            st.subheader("📢 Marketing & Sales Intel")
            st.write("**SEO Health:**")
            st.json(seo_data)
            st.write("**Tech Stack:**")
            for tech in tech_stack: st.caption(f"🔹 {tech}")
            st.write("**Social & Contact:**")
            if socials: st.write(socials)
            if emails: st.write(emails)

    # --- BRANCH B: NO WEBSITE (OSINT ONLY) ---
    else:
        st.warning("🔻 No Official Website Detected.")
        if mode == "OSINT":
            # ... (Keep existing AI Strategy Logic here from previous steps) ...
            # For brevity, I am not repeating the AI code block, but you should keep it!
            st.info("Generating AI Strategy...")
            strategy = generate_website_strategy(target_name, target_location, reviews if reviews else "Great service.")
            st.markdown(strategy)