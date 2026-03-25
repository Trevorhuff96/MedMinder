"""
Authentication and user management for the MedMinder app
"""

import sqlite3
import hashlib
import re
from datetime import datetime

DB_FILE = "medminder.db"
DEFAULT_SPECIALITIES = [
    "Cardiologist",
    "Dentist",
    "Neurologist",
    "Pediatrician",
    "General Practitioner",
]

def _column_exists(cursor, table_name, column_name):
    """Check whether a column exists in a SQLite table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)


def _migrate_doctors_table(cursor):
    """Migrate doctors table to use doctor_id primary key while preserving data."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS doctors_new (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE REFERENCES users(email),
            dob TEXT,
            gender TEXT,
            phone TEXT,
            address TEXT,
            speciality TEXT,
            office_hours TEXT,
            off_day TEXT
        )
        """
    )
    cursor.execute(
        """
        INSERT INTO doctors_new (email, dob, gender, phone, address, speciality, office_hours, off_day)
        SELECT email, dob, gender, phone, address, speciality, office_hours, NULL
        FROM doctors
        """
    )
    cursor.execute("DROP TABLE doctors")
    cursor.execute("ALTER TABLE doctors_new RENAME TO doctors")


def _migrate_patients_table(cursor):
    """Migrate patients table to use patient_id primary key while preserving data."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients_new (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE REFERENCES users(email),
            dob TEXT,
            gender TEXT,
            phone TEXT,
            address TEXT
        )
        """
    )
    cursor.execute(
        """
        INSERT INTO patients_new (email, dob, gender, phone, address)
        SELECT email, dob, gender, phone, address
        FROM patients
        """
    )
    cursor.execute("DROP TABLE patients")
    cursor.execute("ALTER TABLE patients_new RENAME TO patients")


def init_db():
    """Initialize the SQLite database with normalized tables for roles."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Core Authentication Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Doctor Profiles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE REFERENCES users(email),
            dob TEXT,
            gender TEXT,
            phone TEXT,
            address TEXT,
            speciality TEXT,
            office_hours TEXT,
            off_day TEXT
        )
    ''')
    
    # Patient Profiles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE REFERENCES users(email),
            dob TEXT,
            gender TEXT,
            phone TEXT,
            address TEXT
        )
    ''')

    # Doctor specialities lookup table used by onboarding and chatbot options.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Specialities (
            speciality_name TEXT PRIMARY KEY
        )
        """
    )
    cursor.executemany(
        "INSERT OR IGNORE INTO Specialities (speciality_name) VALUES (?)",
        [(speciality,) for speciality in DEFAULT_SPECIALITIES],
    )

    # Migrate old schemas (email-as-primary-key) to new id-based schemas
    if not _column_exists(cursor, "doctors", "doctor_id"):
        _migrate_doctors_table(cursor)
    if not _column_exists(cursor, "doctors", "off_day"):
        cursor.execute("ALTER TABLE doctors ADD COLUMN off_day TEXT")
    if not _column_exists(cursor, "patients", "patient_id"):
        _migrate_patients_table(cursor)

    conn.commit()
    conn.close()

init_db()


def get_specialities():
    """Fetch all configured doctor specialities from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT speciality_name
        FROM Specialities
        WHERE TRIM(speciality_name) <> ''
        ORDER BY speciality_name COLLATE NOCASE ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_doctors_by_speciality():
    """Fetch available doctors grouped by speciality for appointment discovery."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            TRIM(COALESCE(d.speciality, '')) AS speciality,
            TRIM(COALESCE(u.name, '')) AS doctor_name,
            TRIM(COALESCE(d.email, '')) AS doctor_email,
            TRIM(COALESCE(d.office_hours, '')) AS office_hours
        FROM doctors d
        JOIN users u ON u.email = d.email
        WHERE u.role = 'Doctor'
          AND TRIM(COALESCE(d.speciality, '')) <> ''
        ORDER BY speciality COLLATE NOCASE ASC, doctor_name COLLATE NOCASE ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()

    doctors_by_speciality = {}
    for speciality, doctor_name, doctor_email, office_hours in rows:
        doctors_by_speciality.setdefault(speciality, []).append(
            {
                "name": doctor_name or "Unknown doctor",
                "email": doctor_email,
                "office_hours": office_hours,
            }
        )

    return doctors_by_speciality

def get_patient_count_for_doctor(doctor_email):
    """
    Get count of unique patients linked to a doctor.
    
    Args:
        doctor_email: Email of the doctor
        
    Returns:
        int: Count of unique patients
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT COUNT(DISTINCT patient_email)
        FROM care_team
        WHERE doctor_email = ?
        """,
        (doctor_email,)
    )
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count

def get_patients_for_doctor(doctor_email):
    """
    Get all patients linked to a specific doctor via care team.
    
    Args:
        doctor_email: Email of the doctor
        
    Returns:
        list[dict]: List of patient details with prescription count
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT 
            p.patient_id,
            u.name,
            u.email,
            p.dob,
            p.gender,
            p.phone,
            p.address,
            COALESCE(prx.prescription_count, 0) as prescription_count
        FROM care_team ct
        JOIN users u ON u.email = ct.patient_email
        LEFT JOIN patients p ON p.email = u.email
        LEFT JOIN (
            SELECT patient_id, doctor_email, COUNT(*) as prescription_count
            FROM prescription
            WHERE doctor_email = ?
            GROUP BY patient_id, doctor_email
        ) prx ON prx.patient_id = p.patient_id AND prx.doctor_email = ct.doctor_email
        WHERE ct.doctor_email = ?
        ORDER BY u.name ASC
        """,
        (doctor_email, doctor_email)
    )

    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "patient_id": row[0],
            "name": row[1],
            "email": row[2],
            "dob": row[3],
            "gender": row[4],
            "phone": row[5],
            "address": row[6],
            "prescription_count": row[7]
        }
        for row in rows
    ]

def is_valid_email(email: str) -> bool:
    """
    Validate email format using regex
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email format is valid, False otherwise
    """

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None

def hash_password(password):
    """
    Hash password using SHA-256

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password
    """
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    """
    Verify password against hashed version
    
    Args:
        password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return hash_password(password) == hashed_password

def create_user(name, email, password, role, profile_data):
    """
    Create a new user and insert their role-specific demographic data.
    """
    if not is_valid_email(email):
        return False, "Invalid email format!"
    
    hashed_pw = hash_password(password)
    created_at = datetime.now().isoformat()
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 1. Insert into core users table
        cursor.execute(
            "INSERT INTO users (email, name, password, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (email, name, hashed_pw, role, created_at)
        )
        
        # 2. Insert into the appropriate profile table
        if role == "Doctor":
            cursor.execute(
                "INSERT INTO doctors (email, dob, gender, phone, address, speciality, office_hours, off_day) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (email, profile_data.get('dob'), profile_data.get('gender'),
                 profile_data.get('phone'), profile_data.get('address'),
                 profile_data.get('speciality'), profile_data.get('office_hours'), profile_data.get('off_day'))
            )
        elif role == "Patient":
            cursor.execute(
                "INSERT INTO patients (email, dob, gender, phone, address) VALUES (?, ?, ?, ?, ?)",
                (email, profile_data.get('dob'), profile_data.get('gender'), 
                 profile_data.get('phone'), profile_data.get('address'))
            )
            
        conn.commit()
        return True, "Account created successfully!"
        
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists!"
    finally:
        conn.close()

def authenticate_user(email, password):
    """
    Authenticate user and return their name AND role for UI routing.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, password, role FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    
    if result is None:
        return False, "No account found with this email!"
        
    stored_name, stored_hashed_password, stored_role = result
    
    if not verify_password(password, stored_hashed_password):
        return False, "Incorrect password!"
        
    # Returning a dictionary so the frontend knows exactly who logged in and what UI to show
    user_info = {
        "name": stored_name,
        "role": stored_role
    }
    return True, user_info


def get_all_patients():
    """
    Fetch all registered patients for doctor-side listing.

    Returns:
        list[dict]: [{patient_id, name, email}, ...]
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT p.patient_id, u.name, u.email
        FROM patients p
        JOIN users u ON u.email = p.email
        WHERE u.role = 'Patient'
        ORDER BY u.name ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {"patient_id": row[0], "name": row[1], "email": row[2]}
        for row in rows
    ]



def get_all_doctors():
    """
    Fetch all registered doctors for patient appointment booking.

    Returns:
        list[dict]: [{doctor_id, name, email, speciality, office_hours}, ...]
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT d.doctor_id, u.name, u.email, d.speciality, d.office_hours
        FROM doctors d
        JOIN users u ON u.email = d.email
        WHERE u.role = 'Doctor'
        ORDER BY u.name COLLATE NOCASE ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "doctor_id": row[0],
            "name": row[1],
            "email": row[2],
            "speciality": row[3],
            "office_hours": row[4],
        }
        for row in rows
    ]
def get_doctors_by_speciality(speciality):
    """
    Fetch doctors matching a speciality.

    Returns:
        list[dict]: [{name, email, speciality}, ...]
    """
    if not speciality or not str(speciality).strip():
        return []

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT u.name, u.email, d.speciality
        FROM doctors d
        JOIN users u ON u.email = d.email
        WHERE u.role = 'Doctor' AND d.speciality = ?
        ORDER BY u.name COLLATE NOCASE ASC
        """,
        (str(speciality).strip(),),
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {"name": row[0], "email": row[1], "speciality": row[2]}
        for row in rows
    ]


def get_doctor_by_email(email):
    """
    Fetch a single doctor by email.

    Returns:
        dict | None: {name, email, speciality, office_hours}
    """
    if not email or not str(email).strip():
        return None

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT u.name, u.email, d.speciality, d.office_hours
        FROM doctors d
        JOIN users u ON u.email = d.email
        WHERE u.role = 'Doctor' AND u.email = ?
        LIMIT 1
        """,
        (str(email).strip(),),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "name": row[0],
        "email": row[1],
        "speciality": row[2],
        "office_hours": row[3],
    }


def get_user_profile(email):
    """
    Fetch user profile information by email.
    
    Args:
        email: User email
        
    Returns:
        dict: User profile data or None if not found
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get user basic info
    cursor.execute("SELECT name, role FROM users WHERE email = ?", (email,))
    user_result = cursor.fetchone()
    
    if not user_result:
        conn.close()
        return None
    
    name, role = user_result
    
    # Get role-specific profile data
    if role == "Doctor":
        cursor.execute(
            "SELECT dob, gender, phone, address, speciality, office_hours, off_day FROM doctors WHERE email = ?",
            (email,)
        )
        profile_result = cursor.fetchone()
        if profile_result:
            return {
                "name": name,
                "email": email,
                "role": role,
                "dob": profile_result[0],
                "gender": profile_result[1],
                "phone": profile_result[2],
                "address": profile_result[3],
                "speciality": profile_result[4],
                "office_hours": profile_result[5],
                "off_day": profile_result[6],
            }
    elif role == "Patient":
        cursor.execute(
            "SELECT dob, gender, phone, address FROM patients WHERE email = ?",
            (email,)
        )
        profile_result = cursor.fetchone()
        if profile_result:
            return {
                "name": name,
                "email": email,
                "role": role,
                "dob": profile_result[0],
                "gender": profile_result[1],
                "phone": profile_result[2],
                "address": profile_result[3]
            }
    
    conn.close()
    return None


def update_user_profile(email, name=None, new_email=None, address=None, office_hours=None, off_day=None):
    """
    Update user profile information.
    
    Args:
        email: Current user email
        name: New name (optional)
        new_email: New email (optional)
        address: New address (optional)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if new_email and not is_valid_email(new_email):
        return False, "Invalid email format!"
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get current user role first
        cursor.execute("SELECT role FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False, "User not found!"
        
        role = result[0]
        
        # Update users table
        if name and new_email:
            cursor.execute(
                "UPDATE users SET name = ?, email = ? WHERE email = ?",
                (name, new_email, email)
            )
            updated_email = new_email
        elif name:
            cursor.execute(
                "UPDATE users SET name = ? WHERE email = ?",
                (name, email)
            )
            updated_email = email
        elif new_email:
            cursor.execute(
                "UPDATE users SET email = ? WHERE email = ?",
                (new_email, email)
            )
            updated_email = new_email
        else:
            updated_email = email
        
        # Update profile table fields
        if role == "Doctor":
            doctor_updates = []
            doctor_values = []
            if address is not None:
                doctor_updates.append("address = ?")
                doctor_values.append(address)
            if office_hours is not None:
                doctor_updates.append("office_hours = ?")
                doctor_values.append(office_hours)
            if off_day is not None:
                doctor_updates.append("off_day = ?")
                doctor_values.append(off_day)
            if doctor_updates:
                doctor_values.append(email)
                cursor.execute(
                    f"UPDATE doctors SET {', '.join(doctor_updates)} WHERE email = ?",
                    tuple(doctor_values),
                )
        elif role == "Patient" and address is not None:
            cursor.execute(
                "UPDATE patients SET address = ? WHERE email = ?",
                (address, email)
            )
        
        # If email changed, update profile table reference too
        if new_email and new_email != email:
            if role == "Doctor":
                cursor.execute(
                    "UPDATE doctors SET email = ? WHERE email = ?",
                    (new_email, email)
                )
            elif role == "Patient":
                cursor.execute(
                    "UPDATE patients SET email = ? WHERE email = ?",
                    (new_email, email)
                )
        
        conn.commit()
        return True, "Profile updated successfully!"
        
    except sqlite3.IntegrityError:
        return False, "Email already in use by another account!"
    except Exception as e:
        return False, f"Error updating profile: {str(e)}"
    finally:
        conn.close()
