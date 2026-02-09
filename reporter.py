"""
Module: reporter.py
Description: Generates professional PDF reports for the B2B Intelligence Tool.
"""

from fpdf import FPDF
import os

class PDFReport(FPDF):
    def header(self):
        # Standard Header for all pages
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'B2B Threat & Opportunity Intelligence', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        # Page footer
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def save_audit_report(name, url, ssl_status, seo_text):
    """
    Generates a PDF for Branch A (Existing Website Audit).
    """
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title Section
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Audit Report: {name}", 0, 1, 'L')
    pdf.ln(5)

    # Target Info
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Target URL: {url}", 0, 1)
    pdf.ln(5)

    # Section 1: Security
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. Security Analysis (SSL/TLS)", 0, 1)
    pdf.set_font("Arial", size=12)
    
    if ssl_status:
        status = "PASS (Secure)"
        color = "This site uses a valid SSL certificate (HTTPS). Data is encrypted."
    else:
        status = "FAIL (Not Secure)"
        color = "CRITICAL: This site is using HTTP. User data is vulnerable to interception."
    
    pdf.cell(0, 10, f"Status: {status}", 0, 1)
    pdf.multi_cell(0, 10, color)
    pdf.ln(5)

    # Section 2: Marketing
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. SEO & Marketing Analysis", 0, 1)
    pdf.set_font("Arial", size=12)

    if seo_text:
        pdf.cell(0, 10, "Status: PASS (Meta Description Detected)", 0, 1)
        pdf.set_font("Arial", 'I', 11)
        pdf.multi_cell(0, 10, f"Current Description: {seo_text}")
    else:
        pdf.cell(0, 10, "Status: FAIL (Missing Meta Description)", 0, 1)
        pdf.multi_cell(0, 10, "Impact: Google cannot accurately summarize this site in search results, leading to lower click-through rates.")

    # Save
    filename = f"{name.replace(' ', '_')}_Audit_Report.pdf"
    pdf.output(filename)
    return filename

def save_strategy_proposal(name, ai_content):
    """
    Generates a PDF for Branch B (New Website Strategy).
    """
    pdf = PDFReport()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Digital Strategy Proposal: {name}", 0, 1, 'L')
    pdf.ln(10)

    # AI Content
    pdf.set_font("Arial", size=12)
    # multi_cell handles text wrapping automatically
    pdf.multi_cell(0, 8, ai_content)

    # Save
    filename = f"{name.replace(' ', '_')}_Strategy.pdf"
    pdf.output(filename)
    return filename