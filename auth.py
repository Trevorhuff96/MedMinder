"""
Authentication and user management for the MedMinder app
"""

import json
import hashlib
import os
import re
from datetime import datetime


DB_FILE = "users_database.json"


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


def load_users():
    """
    Load users from the database file
    
    Returns:
        dict: Dictionary of users with email as key
    """
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_users(users):
    """
    Save users to the database file
    
    Args:
        users: Dictionary of users to save
    """
    with open(DB_FILE, 'w') as f:
        json.dump(users, f, indent=4)


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


def create_user(name, email, password):
    """
    Create a new user account
    
    Args:
        name: User's full name
        email: User's email address
        password: User's password
        
    Returns:
        tuple: (success: bool, message: str)
    """
    users = load_users()

    if not is_valid_email(email):
        return False, "Invalid email format!"
    
    if email in users:
        return False, "An account with this email already exists!"
    
    users[email] = {
        "name": name,
        "password": hash_password(password),
        "created_at": datetime.now().isoformat()
    }
    
    save_users(users)
    return True, "Account created successfully!"


def authenticate_user(email, password):
    """
    Authenticate user credentials
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        tuple: (success: bool, result: str or user_name: str)
    """
    users = load_users()
    
    if email not in users:
        return False, "No account found with this email!"
    
    if not verify_password(password, users[email]["password"]):
        return False, "Incorrect password!"
    
    return True, users[email]["name"]
