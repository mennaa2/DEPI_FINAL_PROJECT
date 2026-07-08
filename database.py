"""
Persistence for the Medical Report Scanner.

Kept as its own module (per the requested `database.py` separation) but
reuses the same SQLite file and connection helper as the rest of the
app (`database.db_manager`) so there is still only one .db file on disk.

Stores everything the scanner needs to show a report again later:
uploaded file (saved to disk, path stored here), raw OCR text, the
structured extracted values, the AI summary, and the resulting risk
prediction — all linked to the user's account.
"""

import json
import os
from datetime import datetime

from database.db_manager import get_connection, DB_DIR

UPLOAD_DIR = os.path.join(DB_DIR, "uploaded_reports")


def init_reports_table():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS medical_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                file_name TEXT,
                file_path TEXT,
                ocr_engine TEXT,
                ocr_confidence REAL,
                ocr_text TEXT,
                extracted_values TEXT,
                missing_fields TEXT,
                ai_summary TEXT,
                prediction_label TEXT,
                prediction_confidence REAL,
                recommendation TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """
        )


def save_uploaded_file(user_id: int, file_name: str, file_bytes: bytes) -> str:
    """Persist the raw uploaded file to disk and return its path."""
    user_dir = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    safe_name = "".join(c for c in file_name if c.isalnum() or c in "._-") or "report"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(user_dir, f"{timestamp}_{safe_name}")

    with open(path, "wb") as f:
        f.write(file_bytes)
    return path


def save_report(
    user_id: int,
    file_name: str,
    file_path: str,
    ocr_engine: str,
    ocr_confidence: float,
    ocr_text: str,
    extracted_values: dict,
    missing_fields: list,
    ai_summary: list,
    prediction_label: str = None,
    prediction_confidence: float = None,
    recommendation: str = None,
) -> int:
    """Save a scanned report and return its new row id."""
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO medical_reports (
                user_id, created_at, file_name, file_path, ocr_engine,
                ocr_confidence, ocr_text, extracted_values, missing_fields,
                ai_summary, prediction_label, prediction_confidence, recommendation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                datetime.now().isoformat(timespec="seconds"),
                file_name,
                file_path,
                ocr_engine,
                ocr_confidence,
                ocr_text,
                json.dumps(extracted_values),
                json.dumps(missing_fields),
                json.dumps(ai_summary),
                prediction_label,
                prediction_confidence,
                recommendation,
            ),
        )
        return cur.lastrowid


def update_report_prediction(report_id: int, prediction_label: str, prediction_confidence: float, recommendation: str):
    """Attach a risk prediction result to an already-saved report."""
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE medical_reports
            SET prediction_label = ?, prediction_confidence = ?, recommendation = ?
            WHERE id = ?
            """,
            (prediction_label, prediction_confidence, recommendation, report_id),
        )


def get_reports(user_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM medical_reports WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [_deserialize(dict(r)) for r in rows]


def get_report(report_id: int, user_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM medical_reports WHERE id = ? AND user_id = ?",
            (report_id, user_id),
        ).fetchone()
        return _deserialize(dict(row)) if row else None


def delete_report(report_id: int, user_id: int):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM medical_reports WHERE id = ? AND user_id = ?",
            (report_id, user_id),
        )


def _deserialize(row: dict) -> dict:
    for json_field in ("extracted_values", "missing_fields", "ai_summary"):
        try:
            row[json_field] = json.loads(row[json_field]) if row[json_field] else (
                [] if json_field != "extracted_values" else {}
            )
        except (json.JSONDecodeError, TypeError):
            row[json_field] = [] if json_field != "extracted_values" else {}
    return row
