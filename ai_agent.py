"""
Module: ai_agent.py
Description: Generates Audit Narratives and SEO Fixes using Gemini AI.
"""
import google.generativeai as genai
import os

# Configure Gemini
# Ensure you have set GEMINI_API_KEY in your Streamlit Secrets!
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_audit_narrative(business_name, url, score, ssl, ports, seo, tech):
    """
    Generates the Executive Summary for the PDF Report.
    """
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    You are a Senior Cyber Security & Digital Strategist.
    Write a 3-paragraph executive summary for a client named '{business_name}'.
    
    DATA:
    - Website: {url}
    - Security Score: {score}/100
    - SSL Secure: {ssl}
    - Open Ports: {ports}
    - Tech Stack: {tech}
    - SEO Data: {seo}
    
    TONE: Professional, urgent, but constructive.
    STRUCTURE:
    1. The Good: What they are doing right.
    2. The Bad: The critical risks (Score, SSL, Ports).
    3. The Opportunity: How fixing SEO/Tech will increase revenue.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {e}"

def generate_seo_fixes(url, current_title, current_desc, industry, location):
    """
    NEW FUNCTION: Automatically rewrites bad SEO tags to rank higher on Google.
    """
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    You are a Google SEO Expert. I need you to rewrite the meta tags for a website to rank #1.
    
    TARGET:
    - Industry: {industry}
    - Location: {location}
    - URL: {url}
    
    CURRENT (BAD) TAGS:
    - Title: {current_title}
    - Description: {current_desc}
    
    TASK:
    Write 3 options for a new, high-converting <title> and <meta description>.
    Include keywords for {industry} in {location}.
    
    FORMAT:
    Option 1: [Aggressive Growth]
    Title: ...
    Desc: ...
    
    Option 2: [Trust & Authority]
    Title: ...
    Desc: ...
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Could not generate SEO fixes due to an API error."