import streamlit as st
import json
import hashlib
import os
from datetime import datetime
import re


def run_app():
    # all streamlit UI logic here

    # Configuration
    st.set_page_config(page_title="Login Page", page_icon="🔐", layout="centered")

    # Database file
    DB_FILE = "users_database.json"

    # Helper Functions
    def load_users():
        """Load users from the database file"""
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        return {}


    def is_valid_email(email: str) -> bool:
        """Validate email format using regex"""
        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        return re.match(pattern, email) is not None


    def save_users(users):
        """Save users to the database file"""
        with open(DB_FILE, 'w') as f:
            json.dump(users, f, indent=4)

    def hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(password, hashed_password):
        """Verify password against hashed version"""
        return hash_password(password) == hashed_password

    def create_user(name, email, password):
        """Create a new user account"""
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
        """Authenticate user credentials"""
        users = load_users()
        
        if email not in users:
            return False, "No account found with this email!"
        
        if not verify_password(password, users[email]["password"]):
            return False, "Incorrect password!"
        
        return True, users[email]["name"]

    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""

    # Custom CSS for styling
    st.markdown("""
        <style>
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        div[data-testid="stForm"] {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }
        .welcome-container {
            background: white;
            padding: 3rem 2rem;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            text-align: center;
            margin-top: 2rem;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 1rem;
        }
        h2 {
            color: #667eea;
            text-align: center;
        }
        .stButton>button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem;
            font-size: 16px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .logout-button>button {
            background: #dc3545 !important;
        }
        .logout-button>button:hover {
            box-shadow: 0 5px 20px rgba(220, 53, 69, 0.4) !important;
        }
        div[data-testid="stFormSubmitButton"] > button {
            margin-top: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Logout function
    def logout():
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        st.rerun()

    # Main App Logic
    if not st.session_state.logged_in:
        # Show login/signup forms
        st.markdown("<h1>🔐 Welcome</h1>", unsafe_allow_html=True)
        
        # Create tabs for Sign In and Sign Up
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        
        # Sign In Tab
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("signin_form"):
                st.subheader("Sign In to Your Account")
                email = st.text_input("Email", placeholder="Enter your email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Sign In")
                
                if submit:
                    if not email or not password:
                        st.error("Please fill in all fields!")
                    else:
                        success, result = authenticate_user(email, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_name = result
                            st.session_state.user_email = email
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(result)
        
        # Sign Up Tab
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("signup_form"):
                st.subheader("Create a New Account")
                name = st.text_input("Full Name", placeholder="Enter your full name")
                email = st.text_input("Email", placeholder="Enter your email", key="signup_email")
                password = st.text_input("Password", type="password", placeholder="Create a password", key="signup_password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                submit = st.form_submit_button("Sign Up")
                
                if submit:
                    if not name or not email or not password or not confirm_password:
                        st.error("Please fill in all fields!")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long!")
                    elif password != confirm_password:
                        st.error("Passwords do not match!")
                    else:
                        success, message = create_user(name, email, password)
                        if success:
                            st.success(message + " Please sign in.")
                        else:
                            st.error(message)

    else:
        # Show dashboard for logged-in users
        st.markdown(f"""
            <div class="welcome-container">
                <h1>👋 Welcome!</h1>
                <h2>{st.session_state.user_name}</h2>
                <p style="color: #666; font-size: 16px; margin-top: 1rem;">
                    Email: {st.session_state.user_email}
                </p>
                <p style="color: #666; margin-top: 1rem;">
                    You have successfully logged in to your account.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Logout button with custom styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="logout-button">', unsafe_allow_html=True)
            if st.button("🚪 Logout", use_container_width=True):
                logout()
            st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    run_app()
