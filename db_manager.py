"""
SQLite database manager for the Maternal Care platform.

This module owns the single source of truth for persisted data:

    * users               -> accounts created through the auth system
    * predictions         -> every risk prediction made by a logged-in user
    * chat_messages       -> every message exchanged with the AI assistant

Design notes
------------
* Streamlit re-runs the whole script on every interaction, so we open a
  short-lived connection per call instead of holding one open globally.
  SQLite handles this fine for a single-user / small-team app.
* `init_db()` is idempotent — it can be called at the top of every page
  and will only create tables the first time.
* All functions return plain Python types (dicts / lists / None) so the
  rest of the app never has to deal with sqlite3.Row objects directly.
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

# The DB file lives inside the project's data/ folder so it survives
# app restarts but stays isolated from source code.
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "maternal_care.db")


@contextmanager
def get_connection():
    """Yield a SQLite connection with row access by column name."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create all required tables if they do not already exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                age INTEGER,
                systolic_bp INTEGER,
                diastolic_bp INTEGER,
                blood_sugar REAL,
                body_temperature REAL,
                heart_rate INTEGER,
                predicted_risk TEXT,
                risk_level TEXT,
                confidence REAL,
                recommendation TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """
        )


# -----------------------------------------------------------------------
# Users
# -----------------------------------------------------------------------
def create_user(full_name: str, email: str, password_hash: str) -> dict:
    """Insert a new user. Raises sqlite3.IntegrityError if email exists."""
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO users (full_name, email, password_hash, created_at) "
            "VALUES (?, ?, ?, ?)",
            (full_name.strip(), email.strip().lower(), password_hash, datetime.now().isoformat()),
        )
        return {"id": cur.lastrowid, "full_name": full_name, "email": email}


def get_user_by_email(email: str):
    """Return the user row (as dict) for the given email, or None."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
        return dict(row) if row else None


def verify_password(email: str, checker) -> dict:
    """
    Look up a user by email and run `checker(password_hash) -> bool`
    against the stored hash. Kept generic so this module never has to
    import bcrypt itself (that stays in the auth layer).
    """
    user = get_user_by_email(email)
    if user and checker(user["password_hash"]):
        return user
    return None


# -----------------------------------------------------------------------
# Predictions / Pregnancy History
# -----------------------------------------------------------------------
def save_prediction(
    user_id: int,
    age: int,
    systolic_bp: int,
    diastolic_bp: int,
    blood_sugar: float,
    body_temperature: float,
    heart_rate: int,
    predicted_risk: str,
    risk_level: str,
    confidence,
    recommendation: str,
):
    """Persist a single risk-prediction result for the pregnancy history page."""
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO predictions (
                user_id, created_at, age, systolic_bp, diastolic_bp,
                blood_sugar, body_temperature, heart_rate,
                predicted_risk, risk_level, confidence, recommendation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                datetime.now().isoformat(timespec="seconds"),
                age,
                systolic_bp,
                diastolic_bp,
                blood_sugar,
                body_temperature,
                heart_rate,
                predicted_risk,
                risk_level,
                confidence,
                recommendation,
            ),
        )


def get_predictions(user_id: int) -> list:
    """Return all predictions for a user, newest first."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def delete_prediction(prediction_id: int, user_id: int):
    """Delete a single prediction, scoped to the owning user for safety."""
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM predictions WHERE id = ? AND user_id = ?",
            (prediction_id, user_id),
        )


def get_prediction_stats(user_id: int) -> dict:
    """Aggregate stats used by the Pregnancy History and Dashboard pages."""
    rows = get_predictions(user_id)
    if not rows:
        return {
            "count": 0,
            "avg_systolic": None,
            "avg_diastolic": None,
            "avg_glucose": None,
            "risk_distribution": {"Low": 0, "Moderate": 0, "High": 0},
            "latest": None,
        }

    count = len(rows)
    avg_systolic = sum(r["systolic_bp"] or 0 for r in rows) / count
    avg_diastolic = sum(r["diastolic_bp"] or 0 for r in rows) / count
    avg_glucose = sum(r["blood_sugar"] or 0 for r in rows) / count

    distribution = {"Low": 0, "Moderate": 0, "High": 0}
    for r in rows:
        level = (r["risk_level"] or "").capitalize()
        if level in distribution:
            distribution[level] += 1

    return {
        "count": count,
        "avg_systolic": round(avg_systolic, 1),
        "avg_diastolic": round(avg_diastolic, 1),
        "avg_glucose": round(avg_glucose, 1),
        "risk_distribution": distribution,
        "latest": rows[0],
    }


# -----------------------------------------------------------------------
# AI Assistant chat history
# -----------------------------------------------------------------------
def save_chat_message(user_id: int, role: str, content: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, created_at, role, content) "
            "VALUES (?, ?, ?, ?)",
            (user_id, datetime.now().isoformat(timespec="seconds"), role, content),
        )


def get_chat_history(user_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM chat_messages WHERE user_id = ? ORDER BY id ASC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_last_chat_summary(user_id: int):
    """Return the most recent user question + assistant answer, if any."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM chat_messages WHERE user_id = ? AND role = 'user' "
            "ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        if not row:
            return None
        answer_row = conn.execute(
            "SELECT * FROM chat_messages WHERE user_id = ? AND role = 'assistant' "
            "AND id > ? ORDER BY id ASC LIMIT 1",
            (user_id, row["id"]),
        ).fetchone()
        return {
            "question": row["content"],
            "answer": answer_row["content"] if answer_row else None,
            "created_at": row["created_at"],
        }


def clear_chat_history(user_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM chat_messages WHERE user_id = ?", (user_id,))
