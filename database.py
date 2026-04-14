# ─────────────────────────────────────────────────────────────────────────────
# DATABASE.PY
#
# This file is the "data layer" of the app — it handles everything to do with
# storing and retrieving data. The rest of the app (app.py) never touches the
# database directly; it just calls these functions. This separation is good
# practice — if you ever swap SQLite for a proper database like PostgreSQL,
# you'd only need to change THIS file, not app.py.
#
# SQLite is a lightweight database that lives in a single file (jobs.db) on
# your computer. No server needed, no setup — Python includes it built-in.
# ─────────────────────────────────────────────────────────────────────────────

import sqlite3                    # Built into Python — no install needed. Lets us talk to SQLite.
from typing import List, Dict, Any  # These are "type hints" — they don't change behaviour,
                                    # but tell you (and your editor) what type each function
                                    # expects and returns. Good habit for readable code.

# The name of the database file that SQLite will create on your machine.
# If this file doesn't exist yet, SQLite creates it automatically on first run.
DB_PATH = "jobs.db"


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTION 1: init_db()
# Called once when the app starts up. Creates the database table if it doesn't
# already exist. Think of a table like a sheet in Excel — rows are records,
# columns are fields (company, role, status, etc.)
# ─────────────────────────────────────────────────────────────────────────────

def init_db():
    # "with sqlite3.connect(...) as conn" opens a connection to the database file.
    # Using "with" means Python automatically closes the connection when done,
    # even if something goes wrong — like a try/finally block but cleaner.
    with sqlite3.connect(DB_PATH) as conn:

        # conn.execute() sends a SQL command to the database.
        # "CREATE TABLE IF NOT EXISTS" means: only create the table if it
        # doesn't already exist — so running this 100 times won't break anything
        # or delete existing data.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                -- id: a unique number for each application.
                -- AUTOINCREMENT means SQLite assigns the next number automatically (1, 2, 3...).
                -- PRIMARY KEY means this column uniquely identifies each row.

                company      TEXT NOT NULL,
                -- TEXT = stores text. NOT NULL = this field is mandatory (can't be empty).

                role         TEXT NOT NULL,

                location     TEXT,
                -- No NOT NULL here = this field is optional (can be left blank).

                salary       TEXT,
                platform     TEXT,

                status       TEXT NOT NULL DEFAULT 'Applied',
                -- DEFAULT 'Applied' means if no status is provided, it automatically
                -- gets set to 'Applied'. Handy fallback.

                date_applied TEXT NOT NULL,
                -- Stored as text in "YYYY-MM-DD" format (e.g. "2026-04-14").
                -- SQLite doesn't have a true date type, so text is the standard approach.

                job_url      TEXT,
                notes        TEXT,

                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                -- Automatically records the exact date+time each row was inserted.
                -- Useful for auditing — we don't display it in the app but it's there.
            )
        """)

        # conn.commit() saves the changes permanently to the file.
        # Without commit(), changes exist only in memory and are lost when the
        # connection closes. Always commit after writes.
        conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTION 2: add_application()
# Inserts one new job application into the database.
# Takes all the form field values from app.py and saves them as a new row.
# Returns the ID of the newly created row (useful if you need to reference it).
# ─────────────────────────────────────────────────────────────────────────────

def add_application(
    company: str,       # Each parameter has a type hint (str = string/text)
    role: str,
    location: str,
    salary: str,
    platform: str,
    status: str,
    date_applied: str,
    job_url: str,
    notes: str
) -> int:               # -> int means this function returns an integer (the new row's ID)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            INSERT INTO applications
                (company, role, location, salary, platform, status, date_applied, job_url, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            # The VALUES line uses ? as placeholders — never put variables directly
            # into SQL strings! That would open you up to "SQL injection" attacks
            # where malicious input can break or hijack your database.
            # Instead, pass the actual values as a separate tuple — SQLite handles
            # the safe substitution automatically.
            (company, role, location, salary, platform, status, date_applied, job_url, notes)
        )
        conn.commit()

        # cursor.lastrowid gives you the auto-assigned ID of the row just inserted.
        # We return it in case the caller needs it (e.g. to immediately link to it).
        return cursor.lastrowid


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTION 3: get_all_applications()
# Fetches every row from the applications table and returns them as a list
# of dictionaries — one dict per application.
#
# Example return value:
# [
#   {"id": 1, "company": "Deloitte", "role": "Data Analyst", "status": "Applied", ...},
#   {"id": 2, "company": "NHS", "role": "SQL Developer", "status": "Interview", ...},
# ]
#
# app.py then wraps this list in a Pandas DataFrame for filtering and charting.
# ─────────────────────────────────────────────────────────────────────────────

def get_all_applications() -> List[Dict[str, Any]]:
    # List[Dict[str, Any]] = a list of dictionaries where keys are strings
    # and values can be anything (int, str, None, etc.)

    with sqlite3.connect(DB_PATH) as conn:

        # By default, SQLite returns rows as tuples: ("Deloitte", "Analyst", ...)
        # Setting row_factory = sqlite3.Row makes each row behave like a dict,
        # so you can access values by column name: row["company"] instead of row[0].
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            # SELECT * = give me all columns
            # ORDER BY date_applied DESC = newest applications first
            "SELECT * FROM applications ORDER BY date_applied DESC"
        ).fetchall()
        # .fetchall() gets every matching row at once as a list.
        # (The alternative is .fetchone() for a single row.)

        # Convert each sqlite3.Row object into a plain Python dict.
        # This makes it easier to work with in app.py (Pandas loves dicts).
        return [dict(row) for row in rows]
        # This is a "list comprehension" — a compact loop.
        # It's equivalent to:
        #   result = []
        #   for row in rows:
        #       result.append(dict(row))
        #   return result


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTION 4: update_status()
# Changes the status of a specific application (identified by its ID).
# Called when the user clicks "✅ Update" on the Applications page.
# ─────────────────────────────────────────────────────────────────────────────

def update_status(app_id: int, new_status: str):
    # app_id: int — the unique database ID of the application to update
    # new_status: str — the new status string, e.g. "Interview"

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            # UPDATE ... SET ... WHERE is SQL for "change this column
            # but only for the row where id matches".
            # Without the WHERE clause, you'd update EVERY row — a common mistake!
            "UPDATE applications SET status = ? WHERE id = ?",
            (new_status, app_id)
            # Again using ? placeholders for safety.
            # Order matters — first ? gets new_status, second ? gets app_id.
        )
        conn.commit()  # Save the change to disk


# ─────────────────────────────────────────────────────────────────────────────
# FUNCTION 5: delete_application()
# Permanently removes one application row from the database.
# Called when the user clicks "🗑️ Delete" on the Applications page.
# ─────────────────────────────────────────────────────────────────────────────

def delete_application(app_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            # DELETE FROM ... WHERE id = ? removes only the row with this ID.
            # Again — WHERE is critical here. Without it, you'd delete everything.
            "DELETE FROM applications WHERE id = ?",
            (app_id,)
            # Note the trailing comma in (app_id,) — this makes it a tuple.
            # Python requires a comma for single-item tuples, otherwise it's
            # just a number in brackets: (app_id) == app_id. Easy gotcha.
        )
        conn.commit()
