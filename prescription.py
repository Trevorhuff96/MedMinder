"""
Prescription storage and management for the MedMinder app
"""

import json
import sqlite3
from datetime import datetime

DB_FILE = "medminder.db"


def init_db():
    """Initialize prescription table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prescription (
            prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            doctor_email TEXT,
            diagnosis TEXT,
            follow_up_days INTEGER,
            general_notes TEXT,
            medicines_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


init_db()


def save_prescription(patient_name, doctor_email, diagnosis, follow_up_days, general_notes, medicines):
    """
    Save a prescription entry into the database.

    Returns:
        tuple[bool, str, int | None]: (success, message, prescription_id)
    """
    if not patient_name or not patient_name.strip():
        return False, "Patient name is required.", None

    if not medicines:
        return False, "At least one medicine entry is required.", None

    created_at = datetime.now().isoformat()
    medicines_json = json.dumps(medicines)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO prescription
            (patient_name, doctor_email, diagnosis, follow_up_days, general_notes, medicines_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patient_name.strip(),
                (doctor_email or "").strip(),
                (diagnosis or "").strip(),
                int(follow_up_days) if follow_up_days is not None else None,
                (general_notes or "").strip(),
                medicines_json,
                created_at,
            ),
        )
        conn.commit()
        prescription_id = cursor.lastrowid
        return True, "Prescription saved successfully.", prescription_id
    except sqlite3.Error as exc:
        return False, f"Failed to save prescription: {exc}", None
    finally:
        conn.close()
