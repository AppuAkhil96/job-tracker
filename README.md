# 💼 Job Application Tracker

A clean, interactive job search dashboard built with **Python**, **Streamlit**, **SQLite**, and **Plotly**.

Built to track applications during an active job search — and to demonstrate real-world Python/data skills on GitHub.

---

## Features

- ➕ **Add applications** — company, role, location, salary, platform, URL, notes
- 📋 **View & manage** — filter by status, search, sort, update status, delete
- 📊 **Analytics dashboard** — response rate, status breakdown donut chart, cumulative timeline, platform breakdown, weekly bar chart
- ⬇️ **Export to CSV** — one-click download of all application data
- 🗄️ **SQLite backend** — lightweight, no setup required, data persists locally

---

## Tech Stack

| Layer       | Tool           | Why                                              |
|-------------|----------------|--------------------------------------------------|
| Frontend    | Streamlit      | Turns Python into a web app with no HTML needed  |
| Database    | SQLite3        | Built into Python, stores data in a single file  |
| Charts      | Plotly Express | Interactive, good-looking charts in one line     |
| Data        | Pandas         | Filter, sort and analyse tabular data easily     |
| Language    | Python 3.10+   |                                                  |

---

## Project Structure

```
job-tracker/
├── app.py           # Main Streamlit app — all pages and UI logic
├── database.py      # All database operations (create, read, update, delete)
├── requirements.txt # Python package dependencies
├── .gitignore       # Tells Git to ignore the database file and cache
└── README.md        # This file
```

**Why two files?**
`database.py` is kept separate from `app.py` on purpose. This is called "separation of concerns" — the UI code doesn't need to know how data is stored. If you ever switch from SQLite to PostgreSQL, you only change `database.py`, not the whole app.

---

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/job-tracker.git
cd job-tracker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

Opens at `http://localhost:8501` in your browser. The `jobs.db` file is created automatically on first run.

---

## Deploy for Free (Streamlit Cloud)

1. Push this repo to GitHub (**must be public**)
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and sign in with GitHub
3. Click **New app** → select your repo → set main file to `app.py`
4. Click **Deploy**

> **Note on persistence:** Streamlit Cloud has an ephemeral filesystem — the SQLite database resets on each redeploy. For a persistent deployed version, swap the SQLite backend for a free cloud database like [Supabase](https://supabase.com) (PostgreSQL) or [Turso](https://turso.tech) (SQLite-compatible). The `database.py` file is the only thing you'd need to change.

---

## Key Concepts Used (Good for Interviews)

| Concept | Where used |
|---|---|
| SQLite CRUD operations | `database.py` — all 5 functions |
| SQL injection prevention (parameterised queries) | `database.py` — all INSERT/UPDATE/DELETE |
| Pandas DataFrame filtering | `app.py` — Applications page filters |
| Pandas groupby + aggregation | `app.py` — Analytics charts |
| Plotly Express charts | `app.py` — All 4 charts |
| Streamlit session state & reruns | `app.py` — Update/delete buttons |
| Python type hints | `database.py` — all function signatures |
| Separation of concerns | Two-file architecture |

---

## Author

**Akhil Denny** — Data Analyst | ex-Deloitte UK
[LinkedIn](https://linkedin.com/in/YOUR_PROFILE) · [GitHub](https://github.com/YOUR_USERNAME)
