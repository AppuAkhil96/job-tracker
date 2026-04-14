# seed_sample_data.py
#
# Run this ONCE on the deployed Streamlit Cloud app to populate it with
# realistic sample data for portfolio/demo purposes.
#
# HOW TO USE ON STREAMLIT CLOUD:
# 1. Push this file to your GitHub repo
# 2. In your Streamlit app, temporarily change app.py to call seed_sample_data()
#    on first load — OR just run it as a one-off via the Streamlit Cloud terminal
#
# HOW TO USE LOCALLY (for testing):
#   python seed_sample_data.py

import sqlite3
from datetime import datetime

DB_PATH = "jobs.db"

SAMPLE_APPLICATIONS = [
    {
        "company": "Deloitte UK",
        "role": "Data Analyst",
        "location": "London (Hybrid)",
        "salary": "£40,000 – £50,000",
        "platform": "LinkedIn",
        "status": "Interview",
        "date_applied": "2026-03-10",
        "job_url": "",
        "notes": "Match: 92% | Second round interview scheduled"
    },
    {
        "company": "NHS Digital",
        "role": "BI Analyst",
        "location": "Leeds (Hybrid)",
        "salary": "Band 6 – £35,392",
        "platform": "NHS Jobs",
        "status": "Assessment",
        "date_applied": "2026-03-12",
        "job_url": "",
        "notes": "Match: 88% | Online assessment completed"
    },
    {
        "company": "KPMG",
        "role": "Data Engineer",
        "location": "Manchester (Hybrid)",
        "salary": "£45,000 – £55,000",
        "platform": "Indeed",
        "status": "Recruiter Call",
        "date_applied": "2026-03-15",
        "job_url": "",
        "notes": "Match: 85% | Spoke with recruiter Sarah — moving to technical stage"
    },
    {
        "company": "Barclays",
        "role": "SQL Developer",
        "location": "Remote UK",
        "salary": "£38,000 – £45,000",
        "platform": "CWJobs",
        "status": "Applied",
        "date_applied": "2026-03-18",
        "job_url": "",
        "notes": "Match: 80%"
    },
    {
        "company": "Lloyds Banking Group",
        "role": "Data Analyst",
        "location": "Edinburgh (Hybrid)",
        "salary": "£42,000 – £48,000",
        "platform": "Reed",
        "status": "Rejected",
        "date_applied": "2026-03-20",
        "job_url": "",
        "notes": "Match: 78% | No feedback provided"
    },
    {
        "company": "PwC",
        "role": "Business Intelligence Analyst",
        "location": "Birmingham (Hybrid)",
        "salary": "£40,000 – £50,000",
        "platform": "LinkedIn",
        "status": "Applied",
        "date_applied": "2026-03-22",
        "job_url": "",
        "notes": "Match: 82%"
    },
    {
        "company": "AstraZeneca",
        "role": "Data Science Analyst",
        "location": "Cambridge (Hybrid)",
        "salary": "£45,000 – £55,000",
        "platform": "Indeed",
        "status": "Interview",
        "date_applied": "2026-03-25",
        "job_url": "",
        "notes": "Match: 87% | First interview went well — awaiting second round"
    },
    {
        "company": "Transport for London",
        "role": "Data Analyst",
        "location": "London (Hybrid)",
        "salary": "£38,000 – £44,000",
        "platform": "Direct / Company Website",
        "status": "Applied",
        "date_applied": "2026-03-28",
        "job_url": "",
        "notes": "Match: 79%"
    },
    {
        "company": "Boots UK",
        "role": "Power BI Developer",
        "location": "Nottingham (Hybrid)",
        "salary": "£40,000 – £48,000",
        "platform": "Reed",
        "status": "Rejected",
        "date_applied": "2026-04-01",
        "job_url": "",
        "notes": "Match: 76% | Oversubscribed role"
    },
    {
        "company": "Harnham",
        "role": "Data Analyst",
        "location": "Remote UK",
        "salary": "£35,000 – £45,000",
        "platform": "Reed",
        "status": "Recruiter Call",
        "date_applied": "2026-04-03",
        "job_url": "",
        "notes": "Match: 83% | Recruiter call booked for next week"
    },
    {
        "company": "Marks & Spencer",
        "role": "Insight Analyst",
        "location": "London (Hybrid)",
        "salary": "£38,000 – £45,000",
        "platform": "LinkedIn",
        "status": "Applied",
        "date_applied": "2026-04-05",
        "job_url": "",
        "notes": "Match: 80%"
    },
    {
        "company": "Virgin Media O2",
        "role": "Data Engineer",
        "location": "Remote UK",
        "salary": "£45,000 – £55,000",
        "platform": "Indeed",
        "status": "Applied",
        "date_applied": "2026-04-07",
        "job_url": "",
        "notes": "Match: 84% | Fully remote — ideal"
    },
    {
        "company": "Experian",
        "role": "Data Analyst",
        "location": "Nottingham (Hybrid)",
        "salary": "£40,000 – £50,000",
        "platform": "Glassdoor",
        "status": "Assessment",
        "date_applied": "2026-04-08",
        "job_url": "",
        "notes": "Match: 86% | Online test completed — SQL and Python"
    },
    {
        "company": "JPMorgan Chase",
        "role": "Data Engineer",
        "location": "London (Hybrid)",
        "salary": "Competitive",
        "platform": "Indeed",
        "status": "Applied",
        "date_applied": "2026-04-10",
        "job_url": "",
        "notes": "Match: 78% | Prestigious — worth applying"
    },
    {
        "company": "Pardoe Wray (SQL Developer)",
        "role": "SQL Developer",
        "location": "Bedale, N. Yorkshire (Hybrid)",
        "salary": "£35,000 – £45,000",
        "platform": "TotalJobs",
        "status": "Recruiter Call",
        "date_applied": "2026-04-10",
        "job_url": "",
        "notes": "Match: 85% | Spoke with Nathan Pardoe (MD) — awaiting client feedback on sponsorship"
    },
]


def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            company      TEXT NOT NULL,
            role         TEXT NOT NULL,
            location     TEXT,
            salary       TEXT,
            platform     TEXT,
            status       TEXT NOT NULL DEFAULT 'Applied',
            date_applied TEXT NOT NULL,
            job_url      TEXT,
            notes        TEXT,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def seed():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    existing = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    if existing > 0:
        print(f"⚠️  Database already has {existing} record(s). Skipping seed to avoid duplicates.")
        conn.close()
        return

    for app in SAMPLE_APPLICATIONS:
        conn.execute("""
            INSERT INTO applications
                (company, role, location, salary, platform, status, date_applied, job_url, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            app["company"], app["role"], app["location"], app["salary"],
            app["platform"], app["status"], app["date_applied"],
            app["job_url"], app["notes"]
        ))

    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(SAMPLE_APPLICATIONS)} sample applications into {DB_PATH}")


if __name__ == "__main__":
    seed()
