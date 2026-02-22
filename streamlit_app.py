import streamlit as st
from styles import load_custom_styles
from pages import landing_page, auth_page, doctor_dashboard_page, patient_dashboard_page


def run_app():
    """Main Streamlit application"""
    
    # Configuration
    st.set_page_config(page_title="MedMinder", page_icon="💊", layout="wide")

    # Load and apply custom styling
    st.markdown(load_custom_styles(), unsafe_allow_html=True)

    # Initialize session state (Added user_role!)
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'show_auth' not in st.session_state:
        st.session_state.show_auth = False
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False

    # Main App Logic - Route to appropriate page
    if st.session_state.logged_in:
        if st.session_state.user_role == "Doctor":
            doctor_dashboard_page()
        else:
            patient_dashboard_page()
    elif st.session_state.show_auth:
        auth_page()
    else:
        landing_page()


if __name__ == "__main__":
    run_app()