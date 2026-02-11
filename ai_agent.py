"""
Module: ai_agent.py
Description: Uses Gemini with automatic fallback to older models to prevent 404s.
"""
import google.generativeai as genai
import os
import streamlit as st

# Configure Gemini
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        genai.configure(api_key=api_key)
    else:
        print("[!] GEMINI_API_KEY is missing.")
except Exception as e:
    print(f"[!] Gemini Config Error: {e}")

def generate_with_fallback(prompt):
    """
    Tries multiple model versions to find one that works.
    """
    # Priority list: Newest Fast -> Stable -> Old Reliable
    models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            # If 404 or other error, try the next model in the list
            continue
            
    return "AI Unavailable: Could not connect to any Gemini model. Please check API Key."

def generate_audit_narrative(business_name, url, score, ssl, ports, seo, tech):
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
    return generate_with_fallback(prompt)

def generate_seo_fixes(url, current_title, current_desc, industry, location):
    prompt = f"""
    You are a Google SEO Expert. Rewrite the meta tags for a website to rank #1.
    
    TARGET:
    - Industry: {industry}
    - Location: {location}
    - URL: {url}
    
    CURRENT (BAD) TAGS:
    - Title: {current_title}
    - Description: {current_desc}
    
    TASK:
    Write 3 options for a new, high-converting <title> and <meta description>.
    """
    return generate_with_fallback(prompt)