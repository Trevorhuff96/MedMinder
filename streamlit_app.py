import streamlit as st
from styles import load_custom_styles
from pages import landing_page, auth_page, dashboard_page


def run_app():
    """Main Streamlit application"""
    
    # Configuration
    st.set_page_config(page_title="MedMinder", page_icon="💊", layout="wide")

    # Load and apply custom styling
    st.markdown(load_custom_styles(), unsafe_allow_html=True)

    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""
    if 'show_auth' not in st.session_state:
        st.session_state.show_auth = False

    # Main App Logic - Route to appropriate page
    if st.session_state.logged_in:
        dashboard_page()
    elif st.session_state.show_auth:
        auth_page()
    else:
        landing_page()


if __name__ == "__main__":
    run_app()
