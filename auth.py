"""
Authentication and user management for the MedMinder app
"""

import sqlite3
import hashlib
import re
from datetime import datetime

DB_FILE = "medminder.db"

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
            email TEXT PRIMARY KEY REFERENCES users(email),
            dob TEXT,
            gender TEXT,
            phone TEXT,
            address TEXT,
            speciality TEXT,
            office_hours TEXT
        )
    ''')
    
    # Patient Profiles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            email TEXT PRIMARY KEY REFERENCES users(email),
            dob TEXT,
            gender TEXT,
            phone TEXT,
            address TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

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
    return hashlib.sha256(password.encode()).hexdigest()

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
                "INSERT INTO doctors (email, dob, gender, phone, address, speciality, office_hours) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (email, profile_data.get('dob'), profile_data.get('gender'), 
                 profile_data.get('phone'), profile_data.get('address'), 
                 profile_data.get('speciality'), profile_data.get('office_hours'))
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