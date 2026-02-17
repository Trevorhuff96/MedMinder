import streamlit as st
from auth import authenticate_user, create_user
from styles import load_custom_styles


def run_app():
    """Main Streamlit application"""
    
    # Configuration
    st.set_page_config(page_title="Login Page", page_icon="🔐", layout="centered")

    # Load and apply custom styling
    st.markdown(load_custom_styles(), unsafe_allow_html=True)

    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""

    # Logout function
    def logout():
        """Clear session state and logout user"""
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
