import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# =====================
# ENV
# =====================
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DB_URL = os.getenv("DB_URL")

# json

import json

def load_fewshots():
    with open("fewshots.json", "r", encoding="utf-8") as f:
        return json.load(f)

def format_fewshots(fewshots, k=5):

    prompt_examples = ""

    for ex in fewshots[:k]:

        prompt_examples += f"""
Question:
{ex['naturalQuestion']}

SQL:
{ex['sqlQuery']}

"""

    return prompt_examples


# =====================
# Streamlit Config
# =====================
st.set_page_config(page_title="Postgres SQL Chatbot", layout="wide")
st.title("💬 Chat with PostgreSQL DB")

# =====================
# LLM (LangChain + Gemini)
# =====================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0,
    google_api_key=GOOGLE_API_KEY
)

# =====================
# DB Engine
# =====================
@st.cache_resource
def get_engine():
    return create_engine(DB_URL)

# =====================
# Load DB Schema
# =====================
@st.cache_data
def get_schema():
    engine = get_engine()

    query = text("""
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """)

    schema = ""

    with engine.connect() as conn:
        result = conn.execute(query)

        tables = {}

        for table, column in result:
            if table not in tables:
                tables[table] = []
            tables[table].append(column)

        for table, cols in tables.items():
            schema += f'\nTable "{table}" Columns:\n'
            schema += ", ".join([f'"{c}"' for c in cols])
            schema += "\n"

    return schema


schema_info = get_schema()

# =====================
# Prompt Templates
# =====================
sql_prompt = PromptTemplate(
    input_variables=["schema", "question", "examples"],
    template="""
You are a PostgreSQL SQL expert.

Database schema:
{schema}

Examples:
{examples}

User question:
{question}

Rules:
- Only generate SELECT queries
- Use ONLY tables and columns from the schema
- PostgreSQL is CASE-SENSITIVE
- ALWAYS wrap table and column names with double quotes
- NEVER change column names
- NEVER use lowercase versions
- Only output SQL

SQL:
"""
)

answer_prompt = PromptTemplate(
    input_variables=["question", "sql", "data"],
    template="""
You are an expert data analyst.

User question:
{question}

SQL query:
{sql}

Query result:
{data}

Rules:
- Answer in natural language
- Be concise and clear
- If data is empty say: "No data found for the given query."

Final Answer:
"""
)

# =====================
# Functions
# =====================
fewshots = load_fewshots()

def generate_sql(question):

    chain = sql_prompt | llm
    examples = format_fewshots(fewshots, k=5)
    
    response = chain.invoke({
        "schema": schema_info,
        "question": question,
        "examples": examples
    })
    return response.content.strip().replace("```sql", "").replace("```", "").rstrip(";")


def run_query(sql):
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))

        # Check if query returns rows
        if not result.returns_rows:
            return pd.DataFrame()

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df

def generate_answer(question, sql, df):
    chain = answer_prompt | llm
    response = chain.invoke({
        "question": question,
        "sql": sql,
        "data": df.to_string(index=False) if not df.empty else "EMPTY"
    })
    return response.content.strip()


# =====================
# Relevance Check
# =====================
def is_question_relevant(question, schema):
    """
    Check if the user question can be answered using the database schema.
    Returns True if relevant, False otherwise.
    """
    question_lower = question.lower()
    # Flatten schema to a list of tables and columns
    schema_items = [item.lower() for item in schema.replace('"', '').replace('\n', ' ').split()]
    for word in schema_items:
        if word in question_lower:
            return True
    return False


# =====================
# UI
# =====================
question = st.text_input("Ask a question about your database")

if st.button("Run"):
    if not question:
        st.warning("Please enter a question")
    else:
        # 1️⃣ Relevance check
        if not is_question_relevant(question, schema_info):
            st.error("⚠️ This question is not relevant to your database. Cannot generate SQL.")
            st.stop()

        # 2️⃣ Generate SQL safely
        with st.spinner("Generating SQL..."):
            sql = generate_sql(question)

        st.subheader("🧾 Generated SQL")
        st.code(sql, language="sql")

        # 3️⃣ Run query
        with st.spinner("Running query..."):
            df = run_query(sql)

        st.subheader("📊 Query Result")
        st.dataframe(df)

        # 4️⃣ Generate answer
        with st.spinner("Generating answer..."):
            answer = generate_answer(question, sql, df)

        st.subheader("✅ Answer")
        st.write(answer)