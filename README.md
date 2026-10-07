# AI-Powered Business Data Agent

This project is a solution for the **Google Cloud Gen AI Academy APAC Cohort 3 — Track 2: "Turn Business Data into Strategic Decisions."**

It builds an AI-powered Business Data Agent that analyzes public bike-share data in Google Cloud BigQuery and converts natural-language business questions into data-backed strategic recommendations for a coffee business expansion.

## Technologies Used
- Python
- Google Gemini API (`google-generativeai`)
- Google Cloud BigQuery (`google-cloud-bigquery`)
- BigQuery Public Datasets (`bigquery-public-data.austin_bikeshare`)

## Prerequisites
1. A Google Cloud Project with the BigQuery API enabled.
2. A Gemini API Key from Google AI Studio.
3. Python 3.8+ installed locally.

## Setup Instructions

1. **Install Dependencies**
   Open your terminal and run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Authentication**
   Since `gcloud` is not installed locally, you must provide authentication credentials via environment variables.

   **For BigQuery:**
   Set your Google Cloud Project ID and Service Account JSON key path:
   ```powershell
   # Windows PowerShell
   $env:GOOGLE_CLOUD_PROJECT="your-google-cloud-project-id"
   $env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\service-account-key.json"
   ```

   **For Gemini API:**
   Set your Gemini API Key:
   ```powershell
   # Windows PowerShell
   $env:GEMINI_API_KEY="your-gemini-api-key"
   ```

## Running the Agent

To run the agent with the default business question ("We have budget to open 3 coffee trucks. Analyze the available bike-share data to find the most popular starting stations, and recommend the three best locations."):

```bash
python agent.py
```

To ask a custom business question:

```bash
python agent.py --question "Which stations have the most trips exceeding 30 minutes?"
```

## How It Works
1. **Understand**: The agent takes your natural language question.
2. **Discover & Formulate SQL**: Gemini uses the BigQuery schema context to formulate a READ-ONLY standard SQL query.
3. **Execute**: The Python script executes the SQL against BigQuery.
4. **Analyze**: The results are fed back into Gemini.
5. **Recommend**: Gemini produces a concise, strategic business recommendation based on factual data.
