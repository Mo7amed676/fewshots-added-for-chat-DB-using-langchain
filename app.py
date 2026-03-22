import streamlit as st
import google.generativeai as genai
import pandas as pd
from sqlalchemy import create_engine, text


GOOGLE_API_KEY = "AIzaSyAqLnPoIcjADSJINlLuDmsZLBLB6Dtbm_M"
DB_URL="postgresql://postgres:awJOVZjpuRXOkfjUOWZDGCYOTdKVtoeh@trolley.proxy.rlwy.net:20016/railway"


# Setup Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel("models/gemini-2.5-flash")


# Streamlit UI Configuration
st.set_page_config(page_title="Postgress SQL Chatbot")
st.title("Chat with DB")

# Database Connection Function
@st.cache_resource
def get_engine():
    return create_engine(DB_URL)

# Function to Retrieve Database Schema for Context in Prompts

@st.cache_data
def get_schema():

    engine=get_engine()
    inspector_query = text("""
                        SELECT table_name, column_name
                        FROM information_schema.columns 
                        WHERE table_schema = 'public'
                        ORDER BY table_name, ordinal_position;
                     """)
    
    schema_str = ""

    try:
        with engine.connect() as conn:
            result = conn.execute(inspector_query)
            current_table = ""
            for row in result:
                table_name, column_name = row[0], row[1]
                if table_name != current_table:
                    schema_str += f"\nTable: {table_name}\nColumns: "
                    current_table = table_name
                schema_str += f"{column_name}, "
    except Exception as e:
        st.error(f"ERROR reading schema: {e}")
    
    return schema_str

def generate_sql_query(user_input, schema_info):
    prompt = f"""
    You are an expert SQL generator. Given the following database schema and a user request, generate a valid SQL query that fulfills the request.

    Database Schema:
    {schema_info}

    User Request:
    {user_input}

    your task: 
    1. Generate the appropriate PostgresSQL query to answer the user's request based on the provided database schema. Ensure the query is syntactically correct and optimized for performance.
    2. IMPORTANT: the tables were created via pandas to_sql with if_exists='replace', so the table and column names are case-sensitive and should be enclosed in double quotes if they contain uppercase letters or special characters.
    3. Do not include any explanations or comments in your response, only provide the SQL query.
    SQL Query:
    """
    try:
        response = model.generate_content(prompt)
        clean_sql=response.text.replace("```sql", "").replace("```", "").strip()
        return clean_sql
    except Exception as e:
        st.error(f"ERROR generating SQL: {e}")
        return None

def run_query(sql_query):
    engine=get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df
    except Exception as e:
        st.error(f"ERROR executing SQL: {e}")
        return None

def get_natural_language_response(question,sql_query, data):
    prompt = f"""
    You are an expert data analyst. Given the following SQL query, its results, and a user's original question, provide a clear and concise natural language answer to the user's question based on the query results.

    User's Original Question:
    {question}

    SQL Query:
    {sql_query}

    Query Results:
    {data.to_string(index=False)}

    Your task:
    1. Analyze the SQL query and its results to understand what information is being retrieved.
    2. Provide a natural language response that directly answers the user's original question using the insights from the query results.
    3. Ensure your response is clear, concise, and directly addresses the user's question without including any SQL code or technical jargon.
    4. if the query results are empty, respond with "No data found for the given query."
    Natural Language Response:
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"ERROR generating natural language response: {e}")
        return None