"""
Appointments and patient-doctor care team management for MedMinder
"""

import sqlite3
from datetime import datetime, timedelta

DB_FILE = "medminder.db"


def init_appointments_db():
    """Initialize appointments and care_team tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    # Appointments table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_email TEXT NOT NULL,
            doctor_email TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT DEFAULT 'confirmed',
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (patient_email) REFERENCES users(email),
            FOREIGN KEY (doctor_email) REFERENCES users(email)
        )
        """
    )

    # Care team table - links patients to their doctors
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS care_team (
            care_team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_email TEXT NOT NULL,
            doctor_email TEXT NOT NULL,
            linked_at TEXT NOT NULL,
            UNIQUE(patient_email, doctor_email),
            FOREIGN KEY (patient_email) REFERENCES users(email),
            FOREIGN KEY (doctor_email) REFERENCES users(email)
        )
        """
    )

    conn.commit()
    conn.close()


def save_appointment(patient_email, doctor_email, appointment_datetime, notes=""):
    """
    Save a new appointment and link patient to doctor in care team.
    
    Args:
        patient_email: Patient's email
        doctor_email: Doctor's email
        appointment_datetime: Full datetime string (ISO format)
        notes: Optional appointment notes
        
    Returns:
        tuple: (success: bool, message: str, appointment_id: int or None)
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        # Parse datetime
        dt_obj = datetime.fromisoformat(appointment_datetime.replace("Z", "+00:00"))
        appointment_date = dt_obj.strftime("%Y-%m-%d")
        appointment_time = dt_obj.strftime("%H:%M")
        created_at = datetime.now().isoformat()
        # Check if appointment already exists
        cursor.execute(
            """
            SELECT appointment_id FROM appointments 
            WHERE patient_email = ? 
            AND doctor_email = ? 
            AND appointment_date = ? 
            AND appointment_time = ?
            AND status != 'cancelled'
            """,
            (patient_email, doctor_email, appointment_date, appointment_time)
        )
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return False, "This appointment slot is already booked", None


        # Save appointment
        cursor.execute(
            """
            INSERT INTO appointments 
            (patient_email, doctor_email, appointment_date, appointment_time, status, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (patient_email, doctor_email, appointment_date, appointment_time, "confirmed", notes, created_at)
        )
        appointment_id = cursor.lastrowid

        # Link patient to doctor in care team (if not already linked)
        cursor.execute(
            """
            INSERT OR IGNORE INTO care_team (patient_email, doctor_email, linked_at)
            VALUES (?, ?, ?)
            """,
            (patient_email, doctor_email, created_at)
        )

        conn.commit()
        conn.close()

        return True, "Appointment saved successfully", appointment_id

    except Exception as e:
        return False, f"Error saving appointment: {str(e)}", None


def cancel_appointment(appointment_id, requester_email):
    """
    Cancel an existing appointment if requester is the patient or doctor on the appointment.
    Removes doctor from care team if no other appointments exist.

    Args:
        appointment_id: Appointment ID
        requester_email: Email of user requesting cancellation

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # First, get the appointment details before cancelling
        cursor.execute(
            """
            SELECT patient_email, doctor_email
            FROM appointments
            WHERE appointment_id = ?
            AND status != 'cancelled'
            """,
            (appointment_id,),
        )
        
        appointment_details = cursor.fetchone()
        if not appointment_details:
            conn.close()
            return False, "Appointment not found or already cancelled"
        
        patient_email, doctor_email = appointment_details
        if requester_email not in {patient_email, doctor_email}:
            conn.close()
            return False, "Appointment not found, already cancelled, or not allowed"

        # Cancel the appointment
        cursor.execute(
            """
            UPDATE appointments
            SET status = 'cancelled'
            WHERE appointment_id = ?
            """,
            (appointment_id,),
        )

        # Check if there are any other confirmed appointments with this doctor
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM appointments
            WHERE patient_email = ?
            AND doctor_email = ?
            AND status = 'confirmed'
            """,
            (patient_email, doctor_email),
        )
        
        other_appointments_count = cursor.fetchone()[0]
        
        # If no other confirmed appointments exist, remove from care team
        if other_appointments_count == 0:
            cursor.execute(
                """
                DELETE FROM care_team
                WHERE patient_email = ?
                AND doctor_email = ?
                """,
                (patient_email, doctor_email),
            )

        conn.commit()
        conn.close()
        return True, "Appointment cancelled successfully"
    except Exception as e:
        return False, f"Error cancelling appointment: {str(e)}"


def get_appointments_for_patient(patient_email):
    """
    Get upcoming/future appointments for a patient (today and beyond).
    
    Args:
        patient_email: Patient's email
        
    Returns:
        list[dict]: List of appointment dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        SELECT 
            a.appointment_id,
            a.appointment_date,
            a.appointment_time,
            a.status,
            a.notes,
            u.name as doctor_name,
            a.doctor_email,
            d.speciality
        FROM appointments a
        JOIN users u ON a.doctor_email = u.email
        LEFT JOIN doctors d ON d.email = a.doctor_email
        WHERE a.patient_email = ?
            AND datetime(a.appointment_date || ' ' || a.appointment_time) >= datetime(?)
            AND a.status != 'cancelled'
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
        """,
        (patient_email, now_dt)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "appointment_id": row[0],
            "date": row[1],
            "time": row[2],
            "status": row[3],
            "notes": row[4],
            "doctor_name": row[5],
            "doctor_email": row[6],
            "speciality": row[7] or "General",
        }
        for row in rows
    ]


def get_appointments_for_doctor(doctor_email):
    """
    Get upcoming/future appointments for a doctor (today and beyond).
    
    Args:
        doctor_email: Doctor's email
        
    Returns:
        list[dict]: List of appointment dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        SELECT 
            a.appointment_id,
            a.appointment_date,
            a.appointment_time,
            a.status,
            a.notes,
            u.name as patient_name,
            a.patient_email
        FROM appointments a
        JOIN users u ON a.patient_email = u.email
        WHERE a.doctor_email = ?
            AND datetime(a.appointment_date || ' ' || a.appointment_time) >= datetime(?)
            AND a.status != 'cancelled'
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
        """,
        (doctor_email, now_dt)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "appointment_id": row[0],
            "date": row[1],
            "time": row[2],
            "status": row[3],
            "notes": row[4],
            "patient_name": row[5],
            "patient_email": row[6],
        }
        for row in rows
    ]


def get_care_team_for_patient(patient_email):
    """
    Get all doctors in a patient's care team.
    
    Args:
        patient_email: Patient's email
        
    Returns:
        list[dict]: List of doctor dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            u.name,
            u.email,
            d.speciality,
            d.office_hours,
            ct.linked_at
        FROM care_team ct
        JOIN users u ON ct.doctor_email = u.email
        LEFT JOIN doctors d ON d.email = ct.doctor_email
        WHERE ct.patient_email = ?
        ORDER BY ct.linked_at DESC
        """,
        (patient_email,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "name": row[0],
            "email": row[1],
            "speciality": row[2] or "General",
            "office_hours": row[3],
            "linked_at": row[4],
        }
        for row in rows
    ]


def get_booked_slots_for_doctor(doctor_email):
    """
    Get confirmed appointment slots for a doctor.

    Args:
        doctor_email: Doctor's email

    Returns:
        set[tuple[str, str]]: Set of (appointment_date, appointment_time)
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT appointment_date, appointment_time
        FROM appointments
        WHERE doctor_email = ?
          AND status = 'confirmed'
        """,
        (doctor_email,)
    )

    rows = cursor.fetchall()
    conn.close()

    return {(row[0], row[1]) for row in rows}


def update_appointment_notes(appointment_id, notes):
    """
    Update notes for an appointment.
    
    Args:
        appointment_id: The appointment ID
        notes: The notes text to save
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            UPDATE appointments
            SET notes = ?
            WHERE appointment_id = ?
            """,
            (notes, appointment_id)
        )
        
        conn.commit()
        conn.close()
        
        return True, "Notes updated successfully"
    except Exception as e:
        return False, f"Error updating notes: {str(e)}"


def get_cancelled_appointments_for_patient(patient_email, limit=5):
    """
    Get cancelled appointments for a patient, newest first.

    Args:
        patient_email: Patient's email
        limit: Maximum number of records to return

    Returns:
        list[dict]: Cancelled appointment dictionaries
    """
    if not patient_email:
        return []

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            a.appointment_id,
            a.appointment_date,
            a.appointment_time,
            a.status,
            a.notes,
            u.name as doctor_name,
            a.doctor_email,
            d.speciality
        FROM appointments a
        JOIN users u ON a.doctor_email = u.email
        LEFT JOIN doctors d ON d.email = a.doctor_email
        WHERE a.patient_email = ?
          AND a.status = 'cancelled'
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        LIMIT ?
        """,
        (patient_email, limit),
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "appointment_id": row[0],
            "date": row[1],
            "time": row[2],
            "status": row[3],
            "notes": row[4],
            "doctor_name": row[5],
            "doctor_email": row[6],
            "speciality": row[7] or "General",
        }
        for row in rows
    ]


def get_past_appointments_for_patient(patient_email, days_back=None):
    """
    Get past appointments for a patient from the database, optionally filtered by days back.
    
    Args:
        patient_email: Patient's email
        days_back: Optional number of days to look back (None = all past appointments)
        
    Returns:
        list[dict]: List of past appointment dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if days_back:
        cutoff_dt = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            SELECT 
                a.appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.status,
                a.notes,
                u.name as doctor_name,
                a.doctor_email,
                d.speciality
            FROM appointments a
            JOIN users u ON a.doctor_email = u.email
            LEFT JOIN doctors d ON d.email = a.doctor_email
            WHERE a.patient_email = ?
                AND datetime(a.appointment_date || ' ' || a.appointment_time) < datetime(?)
                AND datetime(a.appointment_date || ' ' || a.appointment_time) >= datetime(?)
                AND a.status != 'cancelled'
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """,
            (patient_email, now_dt, cutoff_dt)
        )
    else:
        cursor.execute(
            """
            SELECT 
                a.appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.status,
                a.notes,
                u.name as doctor_name,
                a.doctor_email,
                d.speciality
            FROM appointments a
            JOIN users u ON a.doctor_email = u.email
            LEFT JOIN doctors d ON d.email = a.doctor_email
            WHERE a.patient_email = ?
                AND datetime(a.appointment_date || ' ' || a.appointment_time) < datetime(?)
                AND a.status != 'cancelled'
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """,
            (patient_email, now_dt)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "appointment_id": row[0],
            "date": row[1],
            "time": row[2],
            "status": row[3],
            "notes": row[4],
            "doctor_name": row[5],
            "doctor_email": row[6],
            "speciality": row[7] or "General",
        }
        for row in rows
    ]


def get_past_appointments_for_doctor(doctor_email, days_back=None):
    """
    Get past appointments for a doctor from the database, optionally filtered by days back.
    
    Args:
        doctor_email: Doctor's email
        days_back: Optional number of days to look back (None = all past appointments)
        
    Returns:
        list[dict]: List of past appointment dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if days_back:
        cutoff_dt = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            SELECT 
                a.appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.status,
                a.notes,
                u.name as patient_name,
                a.patient_email
            FROM appointments a
            JOIN users u ON a.patient_email = u.email
            WHERE a.doctor_email = ?
                AND datetime(a.appointment_date || ' ' || a.appointment_time) < datetime(?)
                AND datetime(a.appointment_date || ' ' || a.appointment_time) >= datetime(?)
                AND a.status != 'cancelled'
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """,
            (doctor_email, now_dt, cutoff_dt)
        )
    else:
        cursor.execute(
            """
            SELECT 
                a.appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.status,
                a.notes,
                u.name as patient_name,
                a.patient_email
            FROM appointments a
            JOIN users u ON a.patient_email = u.email
            WHERE a.doctor_email = ?
                AND datetime(a.appointment_date || ' ' || a.appointment_time) < datetime(?)
                AND a.status != 'cancelled'
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """,
            (doctor_email, now_dt)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "appointment_id": row[0],
            "date": row[1],
            "time": row[2],
            "status": row[3],
            "notes": row[4],
            "patient_name": row[5],
            "patient_email": row[6],
        }
        for row in rows
    ]


# Initialize database tables when module is imported
init_appointments_db()
