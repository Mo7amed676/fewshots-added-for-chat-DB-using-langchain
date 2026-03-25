# 💬 PostgreSQL SQL Chatbot using LLM  

Interact with your PostgreSQL database using **natural language**, powered by **Google Gemini (gemini-2.5-flash)**. This project supports **LangChain** and **direct Gemini API** approaches, with a CSV deployment utility.  

---

## 📌 Project Overview
This project allows users to:  
- 🔎 **Generate SQL automatically** from natural language questions  
- 📊 **View query results** in an interactive Streamlit interface  
- 🧠 **Get natural language answers** explaining the results  
- ⚡ **Leverage schema awareness** to ensure relevant queries  
- 📂 **Upload CSV files** into PostgreSQL and verify schema  

---

## 🧰 Features
- Automatic SQL query generation from plain text  
- Case-sensitive table/column handling (`pandas.to_sql`)  
- Relevance check to prevent invalid queries  
- Natural language explanation of query results  
- Streamlit interface for easy interaction  
- CSV data upload & schema verification  

---

## 📝 Prompt Strategy
The LLM is instructed to:  
1. Generate **valid PostgreSQL SELECT queries**  
2. Use **double quotes** for table and column names  
3. Output **only SQL** (for `app_langC.py`)  
4. Convert query results into **clear, concise answers**  
5. Return `"No data found for the given query."` if results are empty  

---


# Chinook Database Chatbot

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)

A Streamlit-powered chatbot that allows natural language queries against the [Chinook Music Store Database](https://www.sqlitetutorial.net/sqlite-sample-database/) hosted on PostgreSQL (Railway). Uses LangChain + Google Gemini to generate SQL queries and provide insightful natural language responses.

![Database Schema](Schema.jpg)

## 🏗️ Project Structure

```
Chinook/
├── app_langC.py          # Main Streamlit app (LangChain + Gemini version)
├── app.py                # Alternative Streamlit app (direct Gemini API)
├── deploy.py             # Script to upload CSV data to Railway Postgres
├── requirements.txt      # Python dependencies
├── fewshots.json         # Few-shot examples for SQL generation
├── data/                 # Chinook CSV database files (11 tables)
│   ├── Album.csv
│   ├── Artist.csv
│   ├── Customer.csv
│   ├── Employee.csv
│   ├── Genre.csv
│   ├── Invoice.csv
│   ├── InvoiceLine.csv
│   ├── MediaType.csv
│   ├── Playlist.csv
│   ├── PlaylistTrack.csv
│   └── Track.csv
├── Schema.jpg            # Database schema diagram
├── test.py               # Test utilities
└── readme.md             # This file
```

## 🔗 How Components Connect

1. **Data Layer (`data/`)**: CSV files containing Chinook database (standard sample DB with music store data).
2. **Upload/Deploy (`deploy.py`)**: Reads CSVs and uploads to PostgreSQL on Railway using `pandas.to_sql(if_exists='replace')`. Tables are case-sensitive (e.g., `"Artist"`).
3. **Query Layer (`app_langC.py` / `app.py`)**: Streamlit apps connect to Railway DB, fetch dynamic schema, use Gemini LLM to:
   - Generate PostgreSQL SELECT queries from natural language.
   - Execute queries.
   - Summarize results in natural language.
4. **DB Connection**: `postgresql://postgres:...@trolley.proxy.rlwy.net:20016/railway` (update `.env` for your instance).

## 🚀 Quick Start

### 1. Clone & Setup Environment
```bash
git clone https://github.com/Mo7amed676/fewshots-added-for-chat-DB-using-langchain.git
cd Chinook
python -m venv venv
# Windows
venv\\Scripts\\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env`:
```
DB_URL=postgresql://postgres:your-password@your-railway-proxy:port/railway
GOOGLE_API_KEY=your-google-api-key
```

### 3. Upload Data to Railway Postgres
```bash
python deploy.py
```
- Uploads all `data/*.csv` to DB tables.
- Verify: Check `Artist` table sample prints.

**Note**: Railway DB is pre-configured (e.g., trolley.proxy.rlwy.net). Get credentials from Railway dashboard. Tables use `if_exists='replace'` for fresh uploads.

### 4. Run the Chatbot
```bash
streamlit run app_langC.py
```
- Open `http://localhost:8501`.
- Ask: "Who are the top 5 artists by track count?" → Generates SQL, runs query, answers in NL.

## ⚙️ Features

- **Dynamic Schema Fetching**: Introspects DB tables/columns at runtime.
- **Case-Sensitive SQL**: Handles Postgres quoting (e.g., `"Track"."Name"`).
- **Relevance Check**: Validates questions match DB schema.
- **Few-Shot Prompting**: Uses `fewshots.json` for accurate SQL generation.
- **Error Handling**: Graceful fallbacks for empty results/SQL errors.
- **Streamlit UI**: Input question → SQL → Results → NL Answer.

## 🛠️ Deployment

### Railway (Data)
1. Create Postgres DB on [Railway](https://railway.app).
2. Update `DB_URL` in `.env` / `deploy.py`.
3. Run `python deploy.py`.

### Streamlit (App)
Deploy to [Streamlit Cloud](https://streamlit.io/cloud):
1. Push to GitHub.
2. Connect repo, set `app_langC.py` as entrypoint.
3. Add secrets: `DB_URL`, `GOOGLE_API_KEY`.

## 📊 Database Schema
See `Schema.jpg` for visual overview. Key tables:
- `Artist`, `Album`, `Track` (core music data)
- `Customer`, `Invoice`, `InvoiceLine` (sales)
- `Playlist`, `PlaylistTrack` (user playlists)
- `Employee`, `Genre`, `MediaType`

## 🔍 Example Queries
| Question | Generated SQL |
|----------|---------------|
| Top 5 customers by invoice total | `SELECT "Customer"."FirstName", ... FROM "Customer" ...` |
| Artists with most tracks | `SELECT "Artist"."Name", COUNT("Track"."TrackId") ...` |
| Invoice totals by country | `SELECT "Customer"."Country", SUM("Invoice"."Total") ...` |

## 🤝 Contributing
1. Fork & PR.
2. Update TODO.md for features.
3. Test with `streamlit run app_langC.py`.

## ⚠️ Limitations
- SELECT-only queries (no INSERT/UPDATE).
- Relies on Railway DB uptime.
- Google API key quota.

## 📄 License
MIT - See LICENSE for details.

## 🙏 Acknowledgments
- [Chinook DB](https://www.sqlitetutorial.net/sqlite-sample-database/)
- [LangChain](https://langchain.com), [Streamlit](https://streamlit.io), [Gemini API](https://ai.google.dev)

## 👤 Author
Mohamed Mahmoud
