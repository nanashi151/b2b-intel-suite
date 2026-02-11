"""
Module: reporter.py
Description: Generates professional PDF Audit Reports
"""
from fpdf import FPDF
import os

def clean_text(text):
    """
    Removes emojis and special characters that crash FPDF.
    """
    if not text: return ""
    # Replace common emojis with text
    replacements = {
        "✅": "[PASS]", "❌": "[FAIL]", "⚠️": "[WARN]",
        "🚀": "", "🔥": "", "💰": "$", "📉": ""
    }
    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)
    
    # Force ASCII to prevent encoding errors
    return text.encode('latin-1', 'replace').decode('latin-1')

class AuditReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Digital Growth Audit', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(business_name, url, score, ai_summary, ssl, seo, tech):
    """
    Generates the PDF file and returns the filename.
    """
    pdf = AuditReport()
    pdf.add_page()
    
    # 1. Title Section
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Audit Report: {clean_text(business_name)}", 0, 1, 'L')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Target URL: {clean_text(url)}", 0, 1, 'L')
    pdf.ln(5)
    
    # 2. Scorecard
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Overall Digital Health Score: {score}/100", 0, 1, 'L', 1)
    pdf.ln(5)
    
    # 3. Technical Breakdown
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Technical Analysis:", 0, 1)
    pdf.set_font("Arial", '', 11)
    
    ssl_status = "Secure (HTTPS)" if ssl else "Not Secure (HTTP)"
    pdf.cell(0, 8, f"- SSL Security: {ssl_status}", 0, 1)
    
    seo_status = "Present" if seo.get('title') else "Missing (Critical)"
    pdf.cell(0, 8, f"- SEO Title Tag: {seo_status}", 0, 1)
    
    tech_list = ", ".join(tech) if tech else "None Detected"
    pdf.cell(0, 8, f"- Technology Stack: {clean_text(tech_list)}", 0, 1)
    pdf.ln(5)
    
    # 4. AI Executive Summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Executive Summary & Strategy:", 0, 1)
    pdf.set_font("Arial", '', 11)
    
    # Multi-cell allows text wrapping for long AI paragraphs
    pdf.multi_cell(0, 7, clean_text(ai_summary))
    pdf.ln(5)
    
    # 5. Call to Action
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 10, "RECOMMENDATION: Immediate Website Optimization Required.", 0, 1)
    
    # Save File
    filename = f"{clean_text(business_name).replace(' ', '_')}_Audit.pdf"
    pdf.output(filename)
    return filename