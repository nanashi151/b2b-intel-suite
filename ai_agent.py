"""
Module: ai_agent.py
Description: smart AI Agent that auto-detects available Gemini models to avoid 404 errors.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_available_model(api_key):
    """
    Dynamically finds a working model name for the user's API key.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json().get('models', [])
            for model in models:
                # Look for a model that supports generation and is 'gemini'
                if 'generateContent' in model['supportedGenerationMethods'] and 'gemini' in model['name']:
                    # Return the clean model name (e.g., 'models/gemini-pro')
                    return model['name']
    except Exception:
        pass
    
    # Fallback if auto-discovery fails
    return "models/gemini-2.0-flash" 

def generate_website_strategy(business_name, location, reviews):
    """
    Generates a website strategy using the best available Gemini model.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return "ERROR: API Key not found. Please check your .env file."

    # 1. Auto-Detect Model
    print("[?] Detecting available AI models...", end=" ")
    model_name = get_available_model(api_key)
    print(f"Using: {model_name}")

    # 2. The Endpoint
    # Note: model_name already contains 'models/', so we don't add it again
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"

    # 3. The Headers
    headers = {"Content-Type": "application/json"}

    # 4. The Prompt
    prompt_text = f"""
    You are a Senior Digital Marketing Strategist. 
    A business named '{business_name}' in '{location}' has no website, but they have these Google Reviews:
    "{reviews}"

    Based ONLY on these reviews, create a brief Website Proposal. 
    Format the output exactly like this:
    
    1. PROPOSED DOMAIN: (Suggest a catchy .com)
    2. HERO HEADLINE: (A catchy 1-sentence hook based on their strengths)
    3. "ABOUT US" DRAFT: (A 2-sentence bio emphasizing what customers love)
    4. KEY SELLING POINT: (The #1 thing mentioned in reviews)
    """

    # 5. The Payload
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }

    try:
        print(f"[?] Sending request to {model_name}...")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error {response.status_code}: {response.text}"

    except Exception as e:
        return f"Connection Error: {e}"