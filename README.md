# B2B Threat & Opportunity Intelligence Tool

## 🚀 Project Overview
A Python-based automated "Sales Engineer" that performs open-source intelligence (OSINT) on target businesses. The tool analyzes a company's digital footprint and programmatically generates a "Value-Add" PDF report to assist in B2B sales or technical consulting.

**The Logic Flow:**
1.  **Search:** It scans the web to find the official business website.
2.  **Branch A (Website Exists):** Runs a **Technical Audit** (SSL Security & SEO Metadata check).
3.  **Branch B (No Website):** Uses **GenAI (Gemini)** to analyze Google Reviews and generate a "Website Strategy Proposal."

## 🛠 Tech Stack
* **Core:** Python 3.10+
* **Intelligence:** `duckduckgo-search` (OSINT), `requests` (Scraping)
* **Security:** `ssl`, `socket` (Network Analysis)
* **AI Engine:** Google Gemini API (via direct REST implementation for stability)
* **Reporting:** `fpdf` (PDF Generation)

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/b2b-intel-tool.git](https://github.com/yourusername/b2b-intel-tool.git)
    cd b2b-intel-tool
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment:**
    Create a `.env` file and add your Google Gemini API key:
    ```ini
    GEMINI_API_KEY=your_key_here
    ```

## ⚡ Usage

Run the main script:
```bash
python main.py