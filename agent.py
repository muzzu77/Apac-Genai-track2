import os
import argparse
from google.cloud import bigquery
import google.generativeai as genai

# ==============================================================================
# AI-Powered Business Data Agent
# Google Cloud Gen AI Academy APAC Cohort 3 — Track 2
# ==============================================================================

# 1. Configuration and Setup
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize BigQuery Client
bq_client = bigquery.Client(project=PROJECT_ID)

# Initialize Gemini Client
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY environment variable not set. Gemini API calls will fail if not authenticated through other means.")

# We use the Gemini 1.5 Pro model for complex reasoning and SQL generation
model = genai.GenerativeModel('gemini-1.5-pro')

# The public dataset to analyze
DATASET = "bigquery-public-data.austin_bikeshare"
TRIPS_TABLE = f"{DATASET}.bikeshare_trips"
STATIONS_TABLE = f"{DATASET}.bikeshare_stations"

# Dataset Schema Context to help Gemini generate accurate SQL
SCHEMA_CONTEXT = f"""
You are an expert data analyst and BigQuery SQL developer.
You have access to the following BigQuery public dataset for Austin Bikeshare:

1. Table: `{TRIPS_TABLE}`
   Columns:
   - trip_id (INT64)
   - subscriber_type (STRING)
   - bike_id (STRING)
   - bike_type (STRING)
   - start_time (TIMESTAMP)
   - start_station_id (INT64)
   - start_station_name (STRING)
   - end_station_id (INT64)
   - end_station_name (STRING)
   - duration_minutes (INT64)

2. Table: `{STATIONS_TABLE}`
   Columns:
   - station_id (INT64)
   - name (STRING)
   - status (STRING)
   - address (STRING)
   - alternate_name (STRING)
   - city_asset_number (INT64)
   - property_type (STRING)
   - number_of_docks (INT64)
   - power_type (STRING)
   - footprint_length (INT64)
   - footprint_width (INT64)
   - notes (STRING)
   - council_district (INT64)
   - modified_date (TIMESTAMP)

IMPORTANT RULES FOR SQL GENERATION:
- Return ONLY the raw SQL query. Do not include markdown formatting (like ```sql).
- The query MUST be READ-ONLY (SELECT only).
- Do not use DML or DDL statements.
- Ensure the query uses standard BigQuery SQL syntax.
"""

def generate_sql(business_question: str) -> str:
    """Uses Gemini to translate a natural language question into a BigQuery SQL query."""
    print(f"\n[1] Analyzing business question: '{business_question}'...")
    
    prompt = f"""
    {SCHEMA_CONTEXT}

    Based on the schema provided, write a BigQuery SQL query to answer the following business question:
    "{business_question}"
    
    Remember: Return ONLY the raw SQL query without markdown formatting.
    """
    
    response = model.generate_content(prompt)
    sql_query = response.text.strip()
    
    # Clean up markdown if the model accidentally included it
    if sql_query.startswith("```sql"):
        sql_query = sql_query[6:]
    if sql_query.startswith("```"):
        sql_query = sql_query[3:]
    if sql_query.endswith("```"):
        sql_query = sql_query[:-3]
        
    print("[2] Generated SQL Query:")
    print("-" * 40)
    print(sql_query.strip())
    print("-" * 40)
    
    return sql_query.strip()

def execute_query(sql_query: str):
    """Executes the provided SQL query against BigQuery and returns the results."""
    print("\n[3] Executing query in BigQuery...")
    try:
        query_job = bq_client.query(sql_query)
        results = query_job.result()  # Waits for job to complete.
        
        # Convert results to a list of dictionaries for easier processing
        rows = [dict(row) for row in results]
        print(f"    -> Query returned {len(rows)} rows.")
        return rows
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def generate_recommendation(business_question: str, data: list) -> str:
    """Uses Gemini to interpret the data and provide a strategic recommendation."""
    print("\n[4] Generating strategic business recommendation...")
    
    prompt = f"""
    You are a strategic business consultant advising a coffee company on where to expand.
    
    The client asked this business question:
    "{business_question}"
    
    We queried the Austin Bikeshare public data and got the following results:
    {data}
    
    Please provide a concise, data-backed strategic recommendation.
    Your response should include:
    1. The top recommended locations based on the data.
    2. The relevant metrics supporting these recommendations.
    3. A clear explanation of WHY these locations are ideal for a coffee business (e.g., high commuter traffic).
    4. Any important limitations or assumptions in this analysis (e.g., high bike traffic doesn't guarantee coffee sales).
    
    Format the output clearly using Markdown.
    """
    
    response = model.generate_content(prompt)
    return response.text

def main():
    parser = argparse.ArgumentParser(description="AI-Powered Business Data Agent")
    parser.add_argument(
        "--question", 
        type=str, 
        default="We have budget to open 3 coffee trucks. Analyze the available bike-share data to find the most popular starting stations, and recommend the three best locations.",
        help="The business question to ask the agent."
    )
    args = parser.parse_args()
    
    business_question = args.question
    
    # Step 1: Understand question and generate SQL
    sql_query = generate_sql(business_question)
    
    # Step 2: Execute query to inspect/discover data
    data_results = execute_query(sql_query)
    
    if data_results is not None:
        # Step 3: Formulate strategic recommendation
        recommendation = generate_recommendation(business_question, data_results)
        
        print("\n==================================================")
        print("💡 STRATEGIC RECOMMENDATION")
        print("==================================================\n")
        print(recommendation)
        print("\n==================================================")
    else:
        print("\n❌ Failed to retrieve data. Cannot generate recommendation.")

if __name__ == "__main__":
    main()
