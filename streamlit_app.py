import streamlit as st
import streamlit.components.v1 as components
from styles import load_custom_styles
from pages import landing_page, auth_page, doctor_dashboard_page, patient_dashboard_page, prescription_page


def sync_browser_route(route: str) -> None:
    """Reflect app state in browser path without changing server-side routing."""
    target_path = "/" if route == "root" else f"/{route}"
    components.html(
        f"""
        <script>
        (function() {{
            const parentWin = window.parent;
            if (!parentWin || !parentWin.location || !parentWin.history) return;
            const currentPath = parentWin.location.pathname || "/";
            const currentSearch = parentWin.location.search || "";
            const currentHash = parentWin.location.hash || "";
            const targetPath = "{target_path}";
            if (currentPath !== targetPath) {{
                parentWin.history.replaceState({{}}, "", targetPath + currentSearch + currentHash);
            }}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


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
    if 'show_prescription' not in st.session_state:
        st.session_state.show_prescription = False
    if 'selected_patient' not in st.session_state:
        st.session_state.selected_patient = ""
    if 'selected_patient_id' not in st.session_state:
        st.session_state.selected_patient_id = None

    # Query-param logout hook for custom HTML logout controls
    logout_param = st.query_params.get("logout")
    if logout_param == "1":
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        st.session_state.user_role = None
        st.session_state.show_auth = False
        st.session_state.show_signup = False
        st.session_state.show_prescription = False
        st.session_state.selected_patient = ""
        st.session_state.selected_patient_id = None
        st.query_params.clear()
        st.rerun()

    # Main App Logic - Route to appropriate page
    if st.session_state.logged_in:
        if st.session_state.user_role == "Doctor":
            if st.session_state.show_prescription:
                sync_browser_route("prescription")
                prescription_page()
            else:
                sync_browser_route("doctor")
                doctor_dashboard_page()
        else:
            sync_browser_route("patient")
            patient_dashboard_page()
    elif st.session_state.show_auth:
        sync_browser_route("authentication")
        auth_page()
    else:
        sync_browser_route("root")
        landing_page()


if __name__ == "__main__":
    run_app()
