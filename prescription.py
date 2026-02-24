"""
Prescription storage and management for the MedMinder app
"""

import json
import sqlite3
from datetime import datetime

DB_FILE = "medminder.db"


def _column_exists(cursor, table_name, column_name):
    """Check whether a column exists in a SQLite table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)


def _migrate_prescription_table(cursor):
    """Migrate prescription table to include patient_id foreign key."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prescription_new (
            prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER REFERENCES patients(patient_id),
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
    cursor.execute(
        """
        INSERT INTO prescription_new
        (prescription_id, patient_name, doctor_email, diagnosis, follow_up_days, general_notes, medicines_json, created_at)
        SELECT prescription_id, patient_name, doctor_email, diagnosis, follow_up_days, general_notes, medicines_json, created_at
        FROM prescription
        """
    )
    cursor.execute("DROP TABLE prescription")
    cursor.execute("ALTER TABLE prescription_new RENAME TO prescription")


def init_db():
    """Initialize prescription table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prescription (
            prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER REFERENCES patients(patient_id),
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

    # Migrate old schema to include patient_id foreign key column
    if not _column_exists(cursor, "prescription", "patient_id"):
        _migrate_prescription_table(cursor)

    conn.commit()
    conn.close()


def _resolve_patient_id(cursor, patient_name):
    """Resolve patient_id from patient full name when available."""
    cursor.execute(
        """
        SELECT p.patient_id
        FROM patients p
        JOIN users u ON u.email = p.email
        WHERE u.role = 'Patient' AND u.name = ?
        ORDER BY p.patient_id ASC
        LIMIT 1
        """,
        (patient_name.strip(),),
    )
    row = cursor.fetchone()
    return row[0] if row else None


init_db()


def save_prescription(patient_name, doctor_email, diagnosis, follow_up_days, general_notes, medicines, patient_id=None):
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
    cursor.execute("PRAGMA foreign_keys = ON")

    try:
        resolved_patient_id = patient_id
        if resolved_patient_id is None:
            resolved_patient_id = _resolve_patient_id(cursor, patient_name)

        cursor.execute(
            """
            INSERT INTO prescription
            (patient_id, patient_name, doctor_email, diagnosis, follow_up_days, general_notes, medicines_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                resolved_patient_id,
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


def get_prescriptions_for_patient(patient_email):
    """
    Fetch prescriptions for a specific patient email.

    Returns:
        list[dict]: Prescriptions with parsed medicine entries.
    """
    if not patient_email:
        return []

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute(
        """
        SELECT p.patient_id, u.name
        FROM patients p
        JOIN users u ON u.email = p.email
        WHERE p.email = ? AND u.role = 'Patient'
        LIMIT 1
        """,
        (patient_email,),
    )
    patient_row = cursor.fetchone()
    if not patient_row:
        conn.close()
        return []

    patient_id, patient_name = patient_row

    cursor.execute(
        """
        SELECT
            prescription_id,
            diagnosis,
            follow_up_days,
            general_notes,
            medicines_json,
            created_at
        FROM prescription
        WHERE patient_id = ?
           OR (patient_id IS NULL AND patient_name = ?)
        ORDER BY created_at DESC
        """,
        (patient_id, patient_name),
    )
    rows = cursor.fetchall()
    conn.close()

    prescriptions = []
    for row in rows:
        medicines = []
        try:
            medicines = json.loads(row[4]) if row[4] else []
        except json.JSONDecodeError:
            medicines = []

        prescriptions.append(
            {
                "prescription_id": row[0],
                "diagnosis": row[1],
                "follow_up_days": row[2],
                "general_notes": row[3],
                "medicines": medicines,
                "created_at": row[5],
            }
        )

    return prescriptions
