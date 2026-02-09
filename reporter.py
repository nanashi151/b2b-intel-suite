"""
Module: reporter.py
Description: Generates professional PDF reports with Executive Summary & Raw Data Appendix.
"""
from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'B2B Threat & Opportunity Intelligence', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def save_audit_report(name, url, score, ai_text, ssl_status, seo_data, ports, headers, email_sec, tech, emails, socials):
    """Generates the Executive Audit PDF with full technical appendix."""
    pdf = PDFReport()
    pdf.add_page()
    
    # --- PAGE 1: EXECUTIVE SUMMARY ---
    # Title & Score
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Audit Report: {name}", 0, 1)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Target: {url}", 0, 1)
    pdf.ln(5)
    
    # Score
    pdf.set_font("Arial", 'B', 14)
    status = "EXCELLENT" if score > 80 else "CRITICAL RISK" if score < 50 else "NEEDS IMPROVEMENT"
    pdf.cell(0, 10, f"Risk Score: {score}/100 ({status})", 0, 1)
    pdf.ln(5)

    # AI Narrative
    pdf.set_fill_color(240, 240, 240) # Light gray background
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Executive Summary", 0, 1)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, ai_text, border=0, fill=True)
    pdf.ln(10)

    # --- PAGE 2: TECHNICAL APPENDIX ---
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Appendix: Raw Technical Data", 0, 1)
    pdf.ln(5)
    
    # Section 1: Network Security
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Network & Security Infrastructure", 0, 1)
    pdf.set_font("Arial", size=10)
    
    secure_str = "PASS (Encrypted)" if ssl_status else "FAIL (Unencrypted)"
    pdf.cell(0, 8, f"- SSL/TLS Certificate: {secure_str}", 0, 1)
    
    open_p = [p for p in ports if ports[p] != "Closed"]
    pdf.multi_cell(0, 8, f"- Open Ports: {open_p if open_p else 'None Detected (Secure)'}")
    
    # Headers Loop
    pdf.cell(0, 8, "- Security Headers:", 0, 1)
    for header, status in headers.items():
         pdf.cell(10) # Indent
         pdf.cell(0, 6, f"{header}: {status}", 0, 1)

    # DNS Loop
    pdf.cell(0, 8, "- DNS Email Security:", 0, 1)
    for record, status in email_sec.items():
        pdf.cell(10) # Indent
        pdf.cell(0, 6, f"{record}: {status}", 0, 1)
    
    pdf.ln(5)

    # Section 2: Marketing & Digital Footprint
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. Marketing & SEO Health", 0, 1)
    pdf.set_font("Arial", size=10)
    
    seo_str = "PASS" if seo_data.get('description') else "FAIL (Missing Description)"
    pdf.cell(0, 8, f"- Meta Description: {seo_str}", 0, 1)
    pdf.cell(0, 8, f"- H1 Header Tag: {seo_data.get('h1', 'Unknown')}", 0, 1)
    pdf.cell(0, 8, f"- Mobile Viewport: {seo_data.get('viewport', 'Unknown')}", 0, 1)
    
    pdf.ln(5)

    # Section 3: Tech Stack & Leads
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "3. Technology & Leads", 0, 1)
    pdf.set_font("Arial", size=10)
    
    tech_str = ", ".join(tech) if tech else "Unknown"
    pdf.multi_cell(0, 8, f"- Tech Stack Detected: {tech_str}")
    
    email_str = ", ".join(emails) if emails else "No public emails found."
    pdf.multi_cell(0, 8, f"- Contact Emails: {email_str}")
    
    social_str = ", ".join(socials) if socials else "No social links found."
    pdf.multi_cell(0, 8, f"- Social Accounts: {social_str}")

    filename = f"{name.replace(' ', '_')}_Full_Audit.pdf"
    pdf.output(filename)
    return filename

def save_strategy_proposal(name, ai_content):
    """Generates the Strategy PDF (Branch B)."""
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Digital Strategy: {name}", 0, 1)
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, ai_content)
    filename = f"{name.replace(' ', '_')}_Strategy.pdf"
    pdf.output(filename)
    return filename