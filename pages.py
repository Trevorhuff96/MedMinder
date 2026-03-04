"""
Page components for the MedMinder app
"""

from datetime import date, datetime, timedelta
from html import escape

import streamlit as st
from streamlit_calendar import calendar
from auth import (
    authenticate_user,
    create_user,
    get_all_patients,
    get_all_doctors,
    get_patient_count_for_doctor,
    get_patients_for_doctor,
    get_specialities,
    get_user_profile,
    update_user_profile,
)
from prescription import save_prescription, get_prescriptions_for_patient
from appointments import (
    save_appointment,
    cancel_appointment,
    get_appointments_for_patient,
    get_appointments_for_doctor,
    get_care_team_for_patient,
    get_booked_slots_for_doctor,
)
from styles import load_custom_styles
from ui_components import render_floating_chatbot

US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia",
    "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
    "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola",
    "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria",
    "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus",
    "Belgium", "Belize", "Benin", "Bhutan", "Bolivia",
    "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria",
    "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon",
    "Canada", "Central African Republic", "Chad", "Chile", "China",
    "Colombia", "Comoros", "Congo", "Costa Rica", "Cote d'Ivoire",
    "Croatia", "Cuba", "Cyprus", "Czech Republic", "Democratic Republic of the Congo",
    "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador",
    "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia",
    "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon",
    "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada",
    "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras",
    "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland",
    "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya",
    "Kiribati", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon",
    "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
    "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta",
    "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia",
    "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique",
    "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand",
    "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway",
    "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay",
    "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia",
    "Rwanda", "Saint Kitts and Nevis", "Saint Lucia",
    "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe",
    "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore",
    "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa",
    "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname",
    "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania",
    "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia",
    "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine",
    "United Arab Emirates", "United Kingdom", "United States", "Uruguay",
    "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen",
    "Zambia", "Zimbabwe"
]

DOB_MAX_DATE = date.today()
DOB_MIN_DATE = DOB_MAX_DATE - timedelta(days=365 * 100)

def validate_signup_fields(first_name, last_name, dob, line1, city, state, zip_code, 
                           country, phone, email, password, speciality="__SKIP__"):
    """
    Validate signup form fields for both Doctor and Patient roles.
    
    Args:
        Common fields for both roles, plus optional speciality for doctors
        speciality: Use "__SKIP__" as default to skip validation (for patients)
    
    Returns:
        dict: Dictionary of field errors {field_name: error_message}
    """
    errors = {}
    
    # Common validations
    if not first_name:
        errors["first_name"] = "First Name is required."
    if not last_name:
        errors["last_name"] = "Last Name is required."
    if dob is None:
        errors["dob"] = "Date of Birth is required."
    elif dob > DOB_MAX_DATE or dob < DOB_MIN_DATE:
        errors["dob"] = "Date of Birth must be between 100 years ago and today."
    if not line1:
        errors["line1"] = "Address Line 1 is required."
    if not city:
        errors["city"] = "City is required."
    if state is None:
        errors["state"] = "State is required."
    if not zip_code:
        errors["zip_code"] = "Zip Code is required."
    if country is None:
        errors["country"] = "Country is required."
    if not phone:
        errors["phone"] = "Phone is required."
    if not email:
        errors["email"] = "Email is required."
    if not password:
        errors["password"] = "Password is required."
    elif len(password) < 6:
        errors["password"] = "Password must be at least 6 characters."
    
    # Doctor-specific validation (only validate if speciality was passed)
    if speciality != "__SKIP__" and speciality is None:
        errors["speciality"] = "Speciality is required."
    
    return errors

def landing_page():
    """Display the modern landing page with hero section"""
    
    # Top Info Bar
    st.markdown("""
    <div class="top-bar">
        <div class="top-bar-left">
            <span class="top-bar-logo">MEDMINDER</span>
        </div>
        <div class="top-bar-right">
            <div class="info-block">
                <span class="info-icon">📞</span>
                <span class="info-text">EMERGENCY: (+123) 456 7890</span>
            </div>
            <div class="info-block">
                <span class="info-icon">🕐</span>
                <span class="info-text">WORK HOUR: 09:00 - 20:00 Everyday</span>
            </div>
            <div class="info-block">
                <span class="info-icon">📍</span>
                <span class="info-text">LOCATION: 0123 UNCC</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.8, 1.2])
    
    # Left Column - Text and Buttons
    with col1:
        st.markdown("""
        <div class="hero-left">
            <p class="tagline">- Stay on Track. Stay In Mind.</p>
            <h1 class="hero-title">Smarter Health Management Starts Here.</h1>
            <p class="hero-subtitle">
                Supporting patients and providers through every step of care.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Buttons - Side by side
        st.markdown('<div class="hero-cta">', unsafe_allow_html=True)
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
        
        with btn_col1:
            if st.button("Sign In", use_container_width=True, key="signin_hero"):
                st.session_state.show_auth = True
                st.session_state.show_signup = False
                st.rerun()
        
        with btn_col2:
            if st.button("Sign Up", use_container_width=True, key="signup_hero"):
                st.session_state.show_auth = True
                st.session_state.show_signup = True 
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    
    # Right Column - Card with Icon
    with col2:
        st.markdown("""
        <div class="hero-card">
            <div class="heart-icon">❤️</div>
            <div class="card-title">Safe & Secure</div>
            <p class="card-text">Enterprise-grade security for your health data.</p>
            <div class="social-links">
                <a href="#" class="social-link">f</a>
                <a href="#" class="social-link">t</a>
                <a href="#" class="social-link">in</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def auth_page():
    """Display the authentication page with Sign In and Sign Up tabs"""

    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown("<h1 class='auth-title'>🔐 Welcome to MedMinder</h1>", unsafe_allow_html=True)

    # Back to landing page button
    back_left, back_center, back_right = st.columns([1, 6, 1])
    with back_center:
        st.markdown('<div class="auth-back">', unsafe_allow_html=True)
        if st.button("< Back", key="back_button"):
            st.session_state.show_auth = False
            st.session_state.show_signup = False
            if "role" in st.session_state:
                del st.session_state.role
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ------------------ ONBOARDING FORMS ------------------
    # If a role has been selected, hide the tabs and show the full form
    if "role" in st.session_state:
        
        if st.session_state.role == "Doctor":
            with st.form("doctor_onboarding_form"):
                st.markdown("<h3 class='auth-section-title'>Doctor Onboarding</h3>", unsafe_allow_html=True)
                first_name = st.text_input("First Name", placeholder="Enter your first name")
                first_name_error = st.empty()
                last_name = st.text_input("Last Name", placeholder="Enter your last name")
                last_name_error = st.empty()
                dob = st.date_input(
                    "Date of Birth",
                    min_value=DOB_MIN_DATE,
                    max_value=DOB_MAX_DATE,
                    format="DD/MM/YYYY",
                    help="DD/MM/YYYY",
                )
                dob_error = st.empty()
                gender = st.radio("Gender", ["Male", "Female", "Other"])

                st.markdown("<h4 class='auth-subtitle'>Office Location</h4>", unsafe_allow_html=True)
                line1 = st.text_input("Address Line 1", placeholder="Enter address line 1")
                line1_error = st.empty()
                line2 = st.text_input("Address Line 2 (optional)", placeholder="Enter address line 2")
                city = st.text_input("City", placeholder="Enter city")
                city_error = st.empty()
                state = st.selectbox("State", US_STATES, index=None, placeholder="Select your state")
                state_error = st.empty()
                zip_code = st.text_input("Zip Code", placeholder="Enter zip code")
                zip_code_error = st.empty()
                country = st.selectbox("Country", COUNTRIES, index=None, placeholder="Select your country")
                country_error = st.empty()

                st.markdown("<h4 class='auth-subtitle'>Professional Details</h4>", unsafe_allow_html=True)
                phone = st.text_input("Phone", placeholder="Enter phone number")
                phone_error = st.empty()
                speciality_options = get_specialities()
                speciality = st.selectbox(
                    "Speciality",
                    speciality_options,
                    index=None,
                    placeholder="Select your specialty",
                )
                speciality_error = st.empty()
                off_day = st.radio("Off Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
                office_hours = st.radio("Office Hours", ["8:00 AM to 5:00 PM", "9:00 AM to 6:00 PM"])

                st.markdown("<h4 class='auth-subtitle'>Account Details</h4>", unsafe_allow_html=True)
                email = st.text_input("Email", placeholder="Enter your email")
                email_error = st.empty()
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                password_error = st.empty()
                submit = st.form_submit_button("Sign Up")

                if submit:
                    error_slots = {
                        "first_name": first_name_error,
                        "last_name": last_name_error,
                        "dob": dob_error,
                        "line1": line1_error,
                        "city": city_error,
                        "state": state_error,
                        "zip_code": zip_code_error,
                        "country": country_error,
                        "phone": phone_error,
                        "speciality": speciality_error,
                        "email": email_error,
                        "password": password_error,
                    }
                    
                    # Validate all fields using helper function
                    errors = validate_signup_fields(
                        first_name, last_name, dob, line1, city, state, zip_code,
                        country, phone, email, password, speciality=speciality
                    )

                    if errors:
                        if len(errors) == 1:
                            st.error(next(iter(errors.values())))
                        else:
                            st.error("There are missing required fields.")
                            for key, message in errors.items():
                                slot = error_slots.get(key)
                                if slot is not None:
                                    slot.error(message)
                        return

                    address_str = f"{line1}{', ' + line2 if line2 else ''}, {city}, {state} {zip_code}, {country}"
                    profile_data = {
                        "dob": str(dob), 
                        "gender": gender,
                        "phone": phone,
                        "address": address_str,
                        "speciality": speciality,
                        "office_hours": office_hours
                    }
                    
                    success, message = create_user(f"{first_name} {last_name}", email, password, "Doctor", profile_data)
                    
                    if success:
                        st.success(message + " Please sign in.")
                        # Delete the role state to return the user to the Sign In tabs
                        del st.session_state.role
                        st.rerun()
                    else:
                        st.error(message)

        elif st.session_state.role == "Patient":
            with st.form("patient_onboarding_form"):
                st.markdown("<h3 class='auth-section-title'>Patient Onboarding</h3>", unsafe_allow_html=True)
                first_name = st.text_input("First Name", placeholder="Enter your first name")
                first_name_error = st.empty()
                last_name = st.text_input("Last Name", placeholder="Enter your last name")
                last_name_error = st.empty()
                dob = st.date_input(
                    "Date of Birth",
                    min_value=DOB_MIN_DATE,
                    max_value=DOB_MAX_DATE,
                    format="DD/MM/YYYY",
                    help="DD/MM/YYYY",
                )
                dob_error = st.empty()
                gender = st.radio("Gender", ["Male", "Female", "Other"])

                st.markdown("<h4 class='auth-subtitle'>Address</h4>", unsafe_allow_html=True)
                line1 = st.text_input("Address Line 1", placeholder="Enter address line 1")
                line1_error = st.empty()
                line2 = st.text_input("Address Line 2 (optional)", placeholder="Enter address line 2")
                city = st.text_input("City", placeholder="Enter city")
                city_error = st.empty()
                state = st.selectbox("State", US_STATES, index=None, placeholder="Select your state")
                state_error = st.empty()
                zip_code = st.text_input("Zip Code", placeholder="Enter zip code")
                zip_code_error = st.empty()
                country = st.selectbox("Country", COUNTRIES, index=None, placeholder="Select your country")
                country_error = st.empty()
                phone = st.text_input("Phone", placeholder="Enter phone number")
                phone_error = st.empty()

                st.markdown("<h4 class='auth-subtitle'>Account Details</h4>", unsafe_allow_html=True)
                email = st.text_input("Email", placeholder="Enter your email")
                email_error = st.empty()
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                password_error = st.empty()
                submit = st.form_submit_button("Sign Up")

                if submit:
                    error_slots = {
                        "first_name": first_name_error,
                        "last_name": last_name_error,
                        "dob": dob_error,
                        "line1": line1_error,
                        "city": city_error,
                        "state": state_error,
                        "zip_code": zip_code_error,
                        "country": country_error,
                        "phone": phone_error,
                        "email": email_error,
                        "password": password_error,
                    }
                    
                    # Validate all fields using helper function
                    errors = validate_signup_fields(
                        first_name, last_name, dob, line1, city, state, zip_code,
                        country, phone, email, password
                    )

                    if errors:
                        if len(errors) == 1:
                            st.error(next(iter(errors.values())))
                        else:
                            st.error("There are missing required fields.")
                            for key, message in errors.items():
                                slot = error_slots.get(key)
                                if slot is not None:
                                    slot.error(message)
                        return

                    address_str = f"{line1}{', ' + line2 if line2 else ''}, {city}, {state} {zip_code}, {country}"
                    profile_data = {
                        "dob": str(dob), 
                        "gender": gender,
                        "phone": phone,
                        "address": address_str
                    }
                    
                    success, message = create_user(f"{first_name} {last_name}", email, password, "Patient", profile_data)
                    
                    if success:
                        st.success(message + " Please sign in.")
                        # Delete the role state to return the user to the Sign In tabs
                        del st.session_state.role
                        st.rerun()
                    else:
                        st.error(message)

    # ------------------ SIGN IN & SIGN UP TABS ------------------
    # If no role is selected, show the standard tabs
    else:
        tabs = ["Sign In", "Sign Up"]
        if st.session_state.get("show_signup"):
            tabs = ["Sign Up", "Sign In"]

        tab1, tab2 = st.tabs(tabs)

        def render_signin():
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
                            st.session_state.user_name = result["name"]
                            st.session_state.user_role = result["role"]
                            st.session_state.user_email = email
                            st.session_state.show_signup = False
                            st.success(f"Login successful! Welcome, {result['name']}.")
                            st.rerun()
                        else:
                            st.error(result)

        def render_signup():
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Select Your Role")
            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Doctor", key="doctor_button", use_container_width=True):
                    st.session_state.role = "Doctor"
                    st.rerun()
            with col2:
                if st.button("Patient", key="patient_button", use_container_width=True):
                    st.session_state.role = "Patient"
                    st.rerun()

        if st.session_state.get("show_signup"):
            with tab1:
                render_signup()
            with tab2:
                render_signin()
        else:
            with tab1:
                render_signin()
            with tab2:
                render_signup()


    st.markdown('</div>', unsafe_allow_html=True)



def init_menu_state():
    """Initialize menu state in session"""
    if "menu_open" not in st.session_state:
        st.session_state.menu_open = False
    if "show_appointments" not in st.session_state:
        st.session_state.show_appointments = False


def render_side_drawer():
    """Render a side drawer menu with Profile, Appointments, and Logout"""
    menu_open = st.session_state.get("menu_open", False)
    
    if menu_open:
        # Create a container that will be positioned as drawer
        st.markdown("""
        <style>
        .menu-overlay-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 9998;
            pointer-events: none;
        }
        /* Target the container holding our drawer */
        div[data-testid="stVerticalBlock"]:has(.side-menu-container) {
            position: fixed !important;
            top: 0 !important;
            right: 0 !important;
            width: 300px !important;
            height: 100vh !important;
            background: linear-gradient(135deg, #0B2F5B 0%, #0d3a78 100%) !important;
            box-shadow: -4px 0 24px rgba(0, 0, 0, 0.3) !important;
            z-index: 9999 !important;
            padding: 24px !important;
            overflow-y: auto !important;
        }
        .side-menu-container {
            width: 100%;
        }
        .side-menu-title {
            color: #ffffff;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 24px;
            text-align: center;
        }
        div[data-testid="stVerticalBlock"]:has(.side-menu-container) button {
            margin-bottom: 12px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        div[data-testid="stVerticalBlock"]:has(.side-menu-container) button:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Dark overlay background
        st.markdown('<div class="menu-overlay-bg"></div>', unsafe_allow_html=True)
        
        # Create container for menu
        with st.container():
            st.markdown('<div class="side-menu-container">', unsafe_allow_html=True)
            st.markdown('<div class="side-menu-title">Menu</div>', unsafe_allow_html=True)
            
            if st.button("✕ Close", key="drawer_close_btn", use_container_width=True):
                st.session_state.menu_open = False
                st.rerun()

            if st.button("🏠 Dashboard", key="drawer_dashboard_btn", use_container_width=True):
                st.session_state.show_profile_edit = False
                st.session_state.show_appointments = False
                st.session_state.show_prescription = False
                st.session_state.menu_open = False
                st.rerun()

            if st.button("⚙️ Profile", key="drawer_profile_btn", use_container_width=True):
                st.session_state.show_profile_edit = True
                st.session_state.show_appointments = False
                st.session_state.menu_open = False
                st.rerun()

            if st.button("📅 Appointment", key="drawer_appointment_btn", use_container_width=True):
                st.session_state.show_appointments = True
                st.session_state.show_profile_edit = False
                st.session_state.menu_open = False
                st.rerun()

            if st.button("🚪 Log out", key="drawer_logout_btn", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_name = ""
                st.session_state.user_email = ""
                st.session_state.user_role = None
                st.session_state.show_auth = False
                st.session_state.show_signup = False
                st.session_state.show_prescription = False
                st.session_state.show_profile_edit = False
                st.session_state.show_appointments = False
                st.session_state.selected_patient = ""
                st.session_state.selected_patient_id = None
                st.session_state.menu_open = False
                st.query_params.clear()
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)


def appointments_page():
    """Display appointments page for both doctors and patients."""
    load_custom_styles()
    init_menu_state()
    render_side_drawer()

    role = st.session_state.get("user_role", "")
    user_email = st.session_state.get("user_email", "")
    title = "📅 Appointments"
    
    header_col1, header_col2 = st.columns([5.5, 0.5])
    
    with header_col1:
        st.markdown(f"<h1 class='patient-welcome'>{title}</h1>", unsafe_allow_html=True)

    with header_col2:
        if st.button("☰", key="toggle_menu_appointments", help="Open menu"):
            st.session_state.menu_open = not st.session_state.menu_open
            st.rerun()
    
    st.markdown(
        f"<p class='patient-account-role'><strong>Account:</strong> {user_email} | "
        f"<strong>Role:</strong> {role}</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if role == "Doctor":
        st.subheader("Daily Schedule")
        
        # Get doctor's appointments
        doctor_appointments = get_appointments_for_doctor(user_email)
        
        if not doctor_appointments:
            st.info("No upcoming patient appointments.")
        else:
            st.markdown(f"**Total Appointments:** {len(doctor_appointments)}")
            st.markdown("---")
            
            for appt in doctor_appointments:
                with st.container():
                    display_date = appt["date"]
                    try:
                        date_obj = datetime.strptime(appt["date"], "%Y-%m-%d")
                        display_date = date_obj.strftime("%b %d, %Y")
                    except (ValueError, TypeError):
                        pass

                    display_time = appt["time"]
                    try:
                        time_obj = datetime.strptime(appt["time"], "%H:%M")
                        display_time = time_obj.strftime("%I:%M %p")
                    except (ValueError, TypeError):
                        pass

                    status_label = (appt.get("status") or "unknown").upper()
                    patient_name = escape(appt.get("patient_name") or "Unknown Patient")
                    patient_email = escape(appt.get("patient_email") or "")
                    
                    st.markdown(
                        f"""
                        <div class="doctor-rx-card" style="margin-bottom: 12px; padding: 14px 16px;">
                            <div class="patient-rx-head" style="margin-bottom: 8px;">
                                <div class="doctor-rx-name">👤 {patient_name}</div>
                                <span class="patient-rx-date">{status_label}</span>
                            </div>
                            <p class="doctor-rx-note" style="margin-bottom: 6px;">📧 {patient_email}</p>
                            <p class="doctor-rx-note" style="margin-bottom: 0;">📅 {display_date} &nbsp;&nbsp;🕐 {display_time}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    if appt.get('notes'):
                        st.markdown(f"**Notes:** {appt['notes']}")
                    
                    st.markdown("---")
        return

    # Patient view - show existing appointments first
    st.subheader("My Appointments")
    patient_appointments = get_appointments_for_patient(user_email)
    
    if patient_appointments:
        st.markdown(f"**Total Appointments:** {len(patient_appointments)}")
        st.markdown("---")
        
        for appt in patient_appointments:
            with st.container():
                card_col, action_col = st.columns([6, 1])

                display_date = appt["date"]
                try:
                    date_obj = datetime.strptime(appt["date"], "%Y-%m-%d")
                    display_date = date_obj.strftime("%b %d, %Y")
                except (ValueError, TypeError):
                    pass

                display_time = appt["time"]
                try:
                    time_obj = datetime.strptime(appt["time"], "%H:%M")
                    display_time = time_obj.strftime("%I:%M %p")
                except (ValueError, TypeError):
                    pass

                status_label = (appt.get("status") or "unknown").upper()
                doctor_name = escape(appt.get("doctor_name") or "Unknown Doctor")
                speciality = escape(appt.get("speciality") or "General")

                with card_col:
                    st.markdown(
                        f"""
                        <div class="doctor-rx-card" style="margin-bottom: 12px; padding: 14px 16px;">
                            <div class="patient-rx-head" style="margin-bottom: 8px;">
                                <div class="doctor-rx-name">👨‍⚕️ Dr. {doctor_name}</div>
                                <span class="patient-rx-date">{status_label}</span>
                            </div>
                            <p class="doctor-rx-note" style="margin-bottom: 6px;">🩺 {speciality}</p>
                            <p class="doctor-rx-note" style="margin-bottom: 0;">📅 {display_date} &nbsp;&nbsp;🕐 {display_time}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with action_col:
                    if appt['status'] != 'cancelled':
                        if st.button("Cancel", key=f"cancel_patient_{appt['appointment_id']}"):
                            success, message = cancel_appointment(appt['appointment_id'], user_email)
                            if success:
                                st.success("✅ Appointment cancelled. Doctor will be removed from your care team if you have no other appointments with them.")
                                st.rerun()
                            else:
                                st.error(message)
                
                if appt.get('notes'):
                    st.markdown(f"**Notes:** {appt['notes']}")
                
                st.markdown("---")
    else:
        st.info("You have no appointments yet. Book one below!")
    
    st.markdown("---")
    st.header("📅 Book New Appointment")
    st.markdown("---")

    doctors = get_all_doctors()
    if not doctors:
        st.info("No doctors are available for booking yet.")
        return

    preselected_email = (
        st.session_state.get("appointment_doctor_email", "")
        or st.query_params.get("doctor_email", "")
        or ""
    ).strip().lower()

    selected_index = 0
    if preselected_email:
        selected_index = next(
            (i for i, doc in enumerate(doctors) if (doc.get("email") or "").strip().lower() == preselected_email),
            0,
        )

    doc_options = [
        f"{doc.get('name', 'Unknown doctor')} ({doc.get('speciality') or 'General'})"
        for doc in doctors
    ]

    st.markdown("#### Select Provider")
    chosen_label = st.selectbox(
        "Switch between available doctors:",
        options=doc_options,
        index=selected_index,
    )
    viewed_doc = doctors[doc_options.index(chosen_label)]

    st.session_state.appointment_doctor_email = (viewed_doc.get("email") or "").strip()

    st.info(
        f"Viewing calendar for **{viewed_doc.get('name', 'Unknown doctor')}** "
        f"({viewed_doc.get('speciality') or 'General Practitioner'})."
    )

    today = date.today()

    # Generate appointment slots from doctor's office hours
    def generate_appointment_slots(doctor_office_hours, start_date, num_days=14):
        """Generate appointment slots based on office hours."""
        slots = []
        
        # Parse office hours (e.g., "9:00 AM to 6:00 PM")
        office_hours_str = doctor_office_hours or "9:00 AM to 5:00 PM"
        try:
            parts = office_hours_str.lower().replace("to", "-").split("-")
            if len(parts) == 2:
                start_time_str = parts[0].strip()
                end_time_str = parts[1].strip()
                
                # Parse start time
                start_hour = datetime.strptime(start_time_str, "%I:%M %p").hour
                # Parse end time
                end_hour = datetime.strptime(end_time_str, "%I:%M %p").hour
            else:
                # Default hours
                start_hour = 9
                end_hour = 17
        except (ValueError, AttributeError):
            # Default hours if parsing fails
            start_hour = 9
            end_hour = 17
        
        # Generate slots for each day
        for day_offset in range(1, num_days + 1):  # Start from tomorrow
            slot_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends
            if slot_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                continue
            
            # Generate 30-minute slots throughout the day
            current_hour = start_hour
            while current_hour < end_hour:
                for minutes in [0, 30]:
                    if current_hour == end_hour - 1 and minutes == 30:
                        break  # Don't create slot 30 min before closing
                    
                    slot_time = datetime(
                        slot_date.year, slot_date.month, slot_date.day,
                        current_hour, minutes
                    )
                    
                    # Skip lunch hour (12:00-13:00)
                    if current_hour == 12:
                        continue
                    
                    slots.append({
                        "title": "Available - Click to Book",
                        "start": slot_time.isoformat(),
                        "end": (slot_time + timedelta(minutes=30)).isoformat(),
                        "backgroundColor": "#28a745",
                        "borderColor": "#28a745",
                    })
                
                current_hour += 1
        
        return slots
    
    calendar_events = generate_appointment_slots(
        viewed_doc.get("office_hours"),
        today,
        num_days=14
    )

    booked_slots = get_booked_slots_for_doctor(viewed_doc.get("email"))
    available_events = []
    for event in calendar_events:
        event_start = event.get("start", "")
        try:
            start_obj = datetime.fromisoformat(event_start.replace("Z", "+00:00"))
            slot_key = (start_obj.strftime("%Y-%m-%d"), start_obj.strftime("%H:%M"))
            if slot_key not in booked_slots:
                available_events.append(event)
        except ValueError:
            available_events.append(event)

    calendar_options = {
        "editable": False,
        "selectable": True,
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridDay,listWeek",
        },
        "initialView": "dayGridMonth",
        "buttonText": {
            "today": "Today",
            "dayGridMonth": "Month",
            "timeGridDay": "Day",
            "listWeek": "List",
        },
        "slotMinTime": "08:00:00",
        "slotMaxTime": "18:00:00",
        "dayMaxEvents": True,
        "height": 650,
        "validRange": {
            "start": str(today),
            "end": str(today + timedelta(days=30)),
        },
    }

    st.markdown("**Use Month, Day, or List view. Click an available green slot to book.**")

    # Build quick-book options from currently available calendar events
    quick_slots = []
    for event in available_events:
        start_value = event.get("start", "")
        try:
            slot_dt = datetime.fromisoformat(start_value.replace("Z", "+00:00"))
            quick_slots.append(
                {
                    "event_start": start_value,
                    "date_key": slot_dt.strftime("%Y-%m-%d"),
                    "date_label": slot_dt.strftime("%b %d, %Y"),
                    "time_label": slot_dt.strftime("%I:%M %p"),
                }
            )
        except ValueError:
            continue

    quick_slots.sort(key=lambda item: item["event_start"])

    def process_appointment_booking(event_start):
        # Create unique key for this appointment booking to prevent duplicates
        appt_key = f"{user_email}_{viewed_doc.get('email')}_{event_start}"

        # Check if this appointment was just booked in this session
        if "booked_appointments" not in st.session_state:
            st.session_state.booked_appointments = set()

        if appt_key in st.session_state.booked_appointments:
            st.info("✅ This appointment slot has already been booked!")
            return

        try:
            date_obj = datetime.fromisoformat(event_start.replace("Z", "+00:00"))
            formatted_date = date_obj.strftime("%B %d, %Y at %I:%M %p")

            # Save appointment to database
            success, message, appt_id = save_appointment(
                patient_email=user_email,
                doctor_email=viewed_doc.get("email"),
                appointment_datetime=event_start,
                notes=""
            )

            if success:
                # Mark this appointment as booked in session
                st.session_state.booked_appointments.add(appt_key)

                st.success(
                    f"✅ Awesome! Your appointment is confirmed with Dr. {viewed_doc.get('name', 'your doctor')} on **{formatted_date}**."
                )
                st.balloons()
                st.info(f"🩺 Dr. {viewed_doc.get('name')} has been added to your care team!")
                st.rerun()
            else:
                st.error(f"Failed to save appointment: {message}")
        except ValueError:
            st.error("Invalid appointment time format. Please try again.")

    st.markdown("#### Quick Book")
    if quick_slots:
        unique_dates = []
        seen_dates = set()
        for slot in quick_slots:
            date_key = slot["date_key"]
            if date_key not in seen_dates:
                seen_dates.add(date_key)
                unique_dates.append((date_key, slot["date_label"]))

        selected_date_key = st.selectbox(
            "Pick a date:",
            options=[item[0] for item in unique_dates],
            format_func=lambda key: next((label for value, label in unique_dates if value == key), key),
            key=f"quick_book_date_{viewed_doc.get('email', 'doctor')}",
        )

        day_slots = [slot for slot in quick_slots if slot["date_key"] == selected_date_key]
        selected_event_start = st.selectbox(
            "Pick a time:",
            options=[slot["event_start"] for slot in day_slots],
            format_func=lambda value: next((slot["time_label"] for slot in day_slots if slot["event_start"] == value), value),
            key=f"quick_book_time_{viewed_doc.get('email', 'doctor')}",
        )

        if st.button("Book Selected Time", type="primary", key=f"quick_book_btn_{viewed_doc.get('email', 'doctor')}"):
            process_appointment_booking(selected_event_start)
    else:
        st.info("No available times for this provider right now.")

    cal_result = calendar(
        events=available_events,
        options=calendar_options,
        key=f"calendar_{viewed_doc.get('doctor_id', viewed_doc.get('email', 'doc'))}",
    )

    st.markdown("---")

    if cal_result and cal_result.get("callback") == "eventClick":
        event_start = cal_result.get("eventClick", {}).get("event", {}).get("start", "")
        if event_start:
            process_appointment_booking(event_start)


def doctor_dashboard_page():
    """Display the dashboard specifically for Doctors"""
    load_custom_styles()
    init_menu_state()
    render_side_drawer()
    
    saved_notice = st.session_state.pop("prescription_saved_notice", None)
    if saved_notice:
        st.markdown(
            f"<div class='prescription-toast'>{saved_notice}</div>",
            unsafe_allow_html=True,
        )

    header_col1, header_col2 = st.columns([5.5, 0.5])
    
    with header_col1:
        st.markdown(f"<h1 class='doctor-welcome'>🩺 Welcome back, Dr. {st.session_state.user_name}!</h1>", unsafe_allow_html=True)

    with header_col2:
        if st.button("☰", key="toggle_menu", help="Open menu"):
            st.session_state.menu_open = not st.session_state.menu_open
            st.rerun()

    st.markdown(f"<p class='doctor-account-role'><strong>Account:</strong> {st.session_state.user_email} | <strong>Role:</strong> {st.session_state.user_role}</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get patient count for this doctor
    total_patients = get_patient_count_for_doctor(st.session_state.user_email)
    
    # Get appointment data for metrics
    all_appointments = get_appointments_for_doctor(st.session_state.user_email)
    total_appointments = len(all_appointments)
    
    today_str = date.today().strftime("%Y-%m-%d")
    today_appointments = [appt for appt in all_appointments if appt.get('date') == today_str]
    today_count = len(today_appointments)
    
    # Doctor summary metrics
    metrics = [
        {
            "icon": "👥",
            "label": "Total Patients",
            "value": str(total_patients),
            "detail": "Under your care",
            "badge": "Active",
        },
        {
            "icon": "📅",
            "label": "Total Appointments",
            "value": str(total_appointments),
            "detail": f"{today_count} scheduled today",
            "badge": "Upcoming",
        },
        {
            "icon": "📋",
            "label": "Today's Schedule",
            "value": str(today_count),
            "detail": "appointments today",
            "badge": "Today",
        },
    ]

    cols = st.columns(3)
    for col, metric in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="patient-metric-card">
                    <div class="patient-metric-head">
                        <span class="patient-metric-icon">{metric["icon"]}</span>
                        <span class="patient-metric-badge">{metric["badge"]}</span>
                    </div>
                    <p class="patient-metric-label">{metric["label"]}</p>
                    <h3 class="patient-metric-value">{metric["value"]}</h3>
                    <p class="patient-metric-detail">{metric["detail"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Doctor Specific Tabs
    tab1, tab2, tab3 = st.tabs(["👥 My Patients", "📅 Daily Schedule", "💊 Prescriptions"])
    
    with tab1:
        st.subheader("Patient Roster")
        
        # Get patients for this doctor
        my_patients = get_patients_for_doctor(st.session_state.user_email)
        
        if not my_patients:
            st.info("No patients found. Patients will appear here once you create a prescription for them.")
        else:
            st.markdown(
                f"<p style='color: #2e3d63; font-size: 16px; font-weight: 600; margin-bottom: 20px;'>Total Patients: {len(my_patients)}</p>",
                unsafe_allow_html=True
            )
            
            # Display patients in styled cards
            for idx, patient in enumerate(my_patients):
                patient_card_html = f"""
                <div class="doctor-rx-card" style="margin-bottom: 20px; padding: 20px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #4a90e2;">
                    <div style="display: grid; grid-template-columns: 2fr 2fr 1fr; gap: 20px;">
                        <div>
                            <p style="color: #2e3d63; font-size: 16px; font-weight: 600; margin-bottom: 8px;">👤 {patient['name']}</p>
                            <p style="color: #5a6c7d; font-size: 14px; margin-bottom: 4px;">📧 {patient['email']}</p>
                            {f"<p style='color: #5a6c7d; font-size: 14px; margin-bottom: 4px;'>📞 {patient['phone']}</p>" if patient['phone'] else ""}
                        </div>
                        <div>
                            {f"<p style='color: #5a6c7d; font-size: 14px; margin-bottom: 4px;'><strong>DOB:</strong> {patient['dob']}</p>" if patient['dob'] else ""}
                            {f"<p style='color: #5a6c7d; font-size: 14px; margin-bottom: 4px;'><strong>Gender:</strong> {patient['gender']}</p>" if patient['gender'] else ""}
                            {f"<p style='color: #5a6c7d; font-size: 14px; margin-bottom: 4px;'><strong>Address:</strong> {patient['address']}</p>" if patient['address'] else ""}
                        </div>
                        <div style="text-align: center;">
                            <p style="color: #2e3d63; font-size: 14px; font-weight: 600; margin-bottom: 4px;">Prescriptions</p>
                            <p style="color: #4a90e2; font-size: 24px; font-weight: 700;">{patient['prescription_count']}</p>
                        </div>
                    </div>
                </div>
                """
                st.markdown(patient_card_html, unsafe_allow_html=True)
        
    with tab2:
        st.subheader("Daily Schedule")
        
        # Get doctor's appointments for today only
        all_doctor_appointments = get_appointments_for_doctor(st.session_state.user_email)
        today_str = date.today().strftime("%Y-%m-%d")
        today_appointments = [appt for appt in all_doctor_appointments if appt.get('date') == today_str]
        
        if not today_appointments:
            st.info("No appointments today.")
        else:
            st.markdown(f"<p style='color: #2e3d63; font-size: 16px; font-weight: 600; margin-bottom: 10px;'>Today's Appointments: {len(today_appointments)}</p>", unsafe_allow_html=True)
            st.markdown("---")
            
            for appt in today_appointments:
                with st.container():
                    display_date = appt["date"]
                    try:
                        date_obj = datetime.strptime(appt["date"], "%Y-%m-%d")
                        display_date = date_obj.strftime("%b %d, %Y")
                    except (ValueError, TypeError):
                        pass

                    display_time = appt["time"]
                    try:
                        time_obj = datetime.strptime(appt["time"], "%H:%M")
                        display_time = time_obj.strftime("%I:%M %p")
                    except (ValueError, TypeError):
                        pass

                    status_label = (appt.get("status") or "unknown").upper()
                    patient_name = escape(appt.get("patient_name") or "Unknown Patient")
                    patient_email = escape(appt.get("patient_email") or "")
                    
                    st.markdown(
                        f"""
                        <div class="doctor-rx-card" style="margin-bottom: 12px; padding: 14px 16px;">
                            <div class="patient-rx-head" style="margin-bottom: 8px;">
                                <div class="doctor-rx-name">👤 {patient_name}</div>
                                <span class="patient-rx-date">{status_label}</span>
                            </div>
                            <p class="doctor-rx-note" style="margin-bottom: 6px;">📧 {patient_email}</p>
                            <p class="doctor-rx-note" style="margin-bottom: 0;">📅 {display_date} &nbsp;&nbsp;🕐 {display_time}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    if appt.get('notes'):
                        st.markdown(f"**Notes:** {appt['notes']}")
                    
                    st.markdown("---")
        
    with tab3:
        st.subheader("Manage Prescriptions")
        st.markdown("<p class='doctor-rx-subtitle' style='color: #2e3d63;'>Select a patient and start a prescription.</p>", unsafe_allow_html=True)
        
        # Show only doctor's existing patients
        my_patients = get_patients_for_doctor(st.session_state.user_email)
        
        if not my_patients:
            st.info("No patients linked to you yet.")
        else:
            for idx, patient in enumerate(my_patients):
                name_col, action_col = st.columns([3.6, 1.4])
                with name_col:
                    st.markdown(
                        f"""
                        <div class="doctor-rx-card">
                            <p class="doctor-rx-name">{patient["name"]}</p>
                            <p class="doctor-rx-note">{patient["email"]}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with action_col:
                    if st.button("Prescribe", key=f"prescribe_{idx}", use_container_width=True):
                        st.session_state.show_prescription = True
                        st.session_state.selected_patient = patient["name"]
                        st.session_state.selected_patient_id = patient["patient_id"]
                        st.rerun()




def prescription_page():
    """Display prescription page for the selected patient."""
    load_custom_styles()
    init_menu_state()
    render_side_drawer()

    header_col1, header_col2 = st.columns([5.5, 0.5])
    
    with header_col1:
        st.markdown("<h1 class='doctor-welcome'>💊 Create Prescription</h1>", unsafe_allow_html=True)

    with header_col2:
        if st.button("☰", key="toggle_menu_prescription", help="Open menu"):
            st.session_state.menu_open = not st.session_state.menu_open
            st.rerun()

    patient_name = st.session_state.get("selected_patient", "Unknown Patient")
    st.markdown(f"<p class='doctor-account-role'><strong>Patient:</strong> {patient_name}</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("<h2 class='rx-title'>Prescription Details</h2>", unsafe_allow_html=True)
    rx_left, rx_center, rx_right = st.columns([2, 4, 2])
    with rx_center:
        total_medicines = st.selectbox("Total Medicines", [1, 2, 3, 4, 5], index=2, key="rx_total_medicines")

    with st.form("prescription_form"):
        st.markdown("#### Clinical Summary")
        diagnosis = st.text_input("Diagnosis", placeholder="e.g., Type 2 Diabetes Mellitus")
        follow_up_days = st.number_input("Follow-up in (days)", min_value=1, max_value=180, value=30, step=1)
        general_notes = st.text_area("General Notes", placeholder="Add overall notes for this prescription...")

        st.markdown("#### Medicines")

        medicine_entries = []
        for idx in range(1, total_medicines + 1):
            st.markdown(f"##### Medicine {idx}")
            med_col1, med_col2 = st.columns(2)
            with med_col1:
                med_name = st.text_input(
                    f"Medicine Name {idx}",
                    key=f"rx_med_name_{idx}",
                    placeholder="e.g., Metformin",
                )
                dosage = st.text_input(
                    f"Dosage {idx}",
                    key=f"rx_dosage_{idx}",
                    placeholder="e.g., 500 mg",
                )
                frequency = st.selectbox(
                    f"Frequency {idx}",
                    [
                        "Once daily",
                        "Twice daily",
                        "Three times daily",
                        "Every 6 hours",
                        "Every 8 hours",
                        "As needed (PRN)",
                    ],
                    key=f"rx_frequency_{idx}",
                )
            with med_col2:
                days_to_take = st.number_input(
                    f"Days to Take {idx}",
                    min_value=1,
                    max_value=180,
                    value=7,
                    step=1,
                    key=f"rx_days_{idx}",
                )
                route = st.selectbox(
                    f"Route {idx}",
                    ["Oral", "Topical", "Injection", "Inhalation", "Other"],
                    key=f"rx_route_{idx}",
                )
                timing = st.text_input(
                    f"Timing {idx}",
                    key=f"rx_timing_{idx}",
                    placeholder="e.g., After meals",
                )

            directions = st.text_area(
                f"Directions {idx}",
                key=f"rx_directions_{idx}",
                placeholder="e.g., Take one tablet after breakfast and dinner with water.",
            )
            st.divider()

            medicine_entries.append(
                {
                    "name": med_name,
                    "dosage": dosage,
                    "frequency": frequency,
                    "days": days_to_take,
                    "route": route,
                    "timing": timing,
                    "directions": directions,
                }
            )

        submit_rx = st.form_submit_button("Save Prescription")

        if submit_rx:
            valid_medicines = [m for m in medicine_entries if m["name"].strip()]
            if not valid_medicines:
                st.error("Please add at least one medicine name before saving.")
            else:
                success, message, prescription_id = save_prescription(
                    patient_name=patient_name,
                    patient_id=st.session_state.get("selected_patient_id"),
                    doctor_email=st.session_state.get("user_email", ""),
                    diagnosis=diagnosis,
                    follow_up_days=follow_up_days,
                    general_notes=general_notes,
                    medicines=medicine_entries,
                )

                if success:
                    st.session_state.prescription_saved_notice = (
                        f"Prescription saved for {patient_name}."
                    )
                    st.session_state.show_prescription = False
                    st.session_state.selected_patient_id = None
                    st.rerun()
                else:
                    st.error(message)

def build_medication_schedule(prescriptions):
    """
    Build a daily medication schedule from prescriptions.
    
    Args:
        prescriptions: List of prescription dicts with medicines array
        
    Returns:
        dict: Keyed by time slot with list of medications for that time
    """
    # Extended time slots to accommodate various intervals
    schedule = {
        "8 AM": [],
        "12 PM": [],
        "2 PM": [],
        "4 PM": [],
        "6 PM": [],
        "8 PM": [],
        "10 PM": [],
    }
    
    TIME_MAPPINGS = {
        "Once daily": ["8 AM"],
        "Twice daily": ["8 AM", "8 PM"],
        "Three times daily": ["8 AM", "2 PM", "8 PM"],
        "Four times daily": ["8 AM", "12 PM", "4 PM", "8 PM"],
        "Before meals": ["8 AM", "12 PM", "6 PM"],
        "After meals": ["8 AM", "12 PM", "6 PM"],
        "At bedtime": ["10 PM"],
        "With breakfast": ["8 AM"],
        "With lunch": ["12 PM"],
        "With dinner": ["6 PM"],
    }
    
    for rx in prescriptions:
        medicines = rx.get("medicines", [])
        doctor_name = (rx.get("doctor_name") or rx.get("doctor_email") or "Unknown doctor").strip()
        
        for med in medicines:
            med_name = (med.get("name") or "").strip()
            if not med_name:
                continue
            
            frequency = (med.get("frequency") or "Once daily").strip()
            dosage = (med.get("dosage") or "-").strip()
            directions = (med.get("directions") or "").strip()
            
            # Determine which time slots this medicine should appear
            times = TIME_MAPPINGS.get(frequency)
            
            # If not found, try to parse "Every X hours" pattern
            if not times and "every" in frequency.lower():
                import re
                match = re.search(r'every\s+(\d+)\s+hours?', frequency, re.IGNORECASE)
                if match:
                    hours = int(match.group(1))
                    # Calculate times starting from 8 AM
                    times = []
                    current_hour = 8
                    while current_hour < 24:
                        if current_hour < 12:
                            times.append(f"{current_hour} AM")
                        elif current_hour == 12:
                            times.append("12 PM")
                        else:
                            times.append(f"{current_hour - 12} PM")
                        current_hour += hours
                    # Filter to only valid slots
                    times = [t for t in times if t in schedule]
            
            # Default to morning only if still not found
            if not times:
                times = ["8 AM"]
            
            med_display = {
                "name": med_name,
                "dosage": dosage,
                "frequency": frequency,
                "directions": directions,
                "doctor": doctor_name,
            }
            
            for time_slot in times:
                if time_slot in schedule:
                    schedule[time_slot].append(med_display)
    
    return schedule

def get_next_medication_dose(prescriptions):
    """
    Calculate the next medication dose based on current time and prescription schedule.
    
    Args:
        prescriptions: List of prescription dicts
        
    Returns:
        dict: {"time": "2 PM", "medication": "Lisinopril 10mg", "badge": "In 30 min"} or None
    """
    from datetime import datetime, timedelta
    
    if not prescriptions:
        return None
    
    # Build the schedule
    schedule = build_medication_schedule(prescriptions)
    
    # Map time slots to hour values for comparison
    time_slot_hours = {
        "8 AM": 8,
        "12 PM": 12,
        "2 PM": 14,
        "4 PM": 16,
        "6 PM": 18,
        "8 PM": 20,
        "10 PM": 22,
    }
    
    # Get current time
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    current_time_decimal = current_hour + current_minute / 60.0
    
    # Find the next scheduled medication
    next_time = None
    next_medications = []
    
    for time_slot in ["8 AM", "12 PM", "2 PM", "4 PM", "6 PM", "8 PM", "10 PM"]:
        slot_hour = time_slot_hours[time_slot]
        medications = schedule.get(time_slot, [])
        
        if medications and slot_hour >= current_time_decimal:
            next_time = time_slot
            next_medications = medications
            break
    
    # If no medication found today, wrap to tomorrow's first dose
    if not next_time:
        for time_slot in ["8 AM", "12 PM", "2 PM", "4 PM", "6 PM", "8 PM", "10 PM"]:
            medications = schedule.get(time_slot, [])
            if medications:
                next_time = time_slot
                next_medications = medications
                break
    
    if not next_medications:
        return None
    
    # Pick the first medication for display
    first_med = next_medications[0]
    med_name = first_med["name"]
    med_dosage = first_med["dosage"]
    
    # Calculate time difference for badge
    slot_hour = time_slot_hours.get(next_time, 8)
    time_diff_hours = slot_hour - current_time_decimal
    
    if time_diff_hours < 0:
        # Tomorrow
        time_diff_hours += 24
        badge = "Tomorrow"
    elif time_diff_hours < 1:
        minutes = int(time_diff_hours * 60)
        badge = f"In {minutes} min" if minutes > 0 else "Now"
    elif time_diff_hours < 2:
        badge = "In 1 hour"
    elif time_diff_hours < 24:
        hours = int(time_diff_hours)
        badge = f"In {hours} hours"
    else:
        badge = "Tomorrow"
    
    return {
        "time": next_time,
        "medication": f"{med_name} {med_dosage}",
        "badge": badge,
    }

def calculate_medication_adherence(prescriptions):
    """
    Calculate medication adherence percentage based on tracked doses.
    
    Args:
        prescriptions: List of prescription dicts
        
    Returns:
        dict: {"adherence_percent": 85, "taken": 17, "total": 20, "trend": "+2%"}
    """
    if not prescriptions:
        return {"adherence_percent": 0, "taken": 0, "total": 0, "trend": ""}
    
    # Initialize adherence tracking in session state if needed
    if "medication_doses_taken" not in st.session_state:
        st.session_state.medication_doses_taken = {}
    
    # Build schedule to count total doses
    schedule = build_medication_schedule(prescriptions)
    
    total_daily_doses = 0
    for time_slot, medications in schedule.items():
        total_daily_doses += len(medications)
    
    # Count taken doses from session state
    taken_doses = len([v for v in st.session_state.medication_doses_taken.values() if v])
    
    # Calculate adherence (simplistic: based on today's doses)
    if total_daily_doses > 0:
        adherence_percent = int((taken_doses / total_daily_doses) * 100)
    else:
        adherence_percent = 0
    
    # Trend (simplified - based on session)
    trend = "+2%" if adherence_percent >= 80 else "-2%"
    
    return {
        "adherence_percent": adherence_percent,
        "taken": taken_doses,
        "total": total_daily_doses,
        "trend": trend,
    }

def patient_dashboard_page():
    """Display the dashboard specifically for Patients"""
    load_custom_styles()
    init_menu_state()
    render_side_drawer()
    
    # Initialize medication adherence tracking
    if "medication_doses_taken" not in st.session_state:
        st.session_state.medication_doses_taken = {}

    header_col1, header_col2 = st.columns([5.5, 0.5])
    
    with header_col1:
        st.markdown(f"<h1 class='patient-welcome'>👋 Welcome back, {st.session_state.user_name}!</h1>", unsafe_allow_html=True)

    with header_col2:
        if st.button("☰", key="toggle_menu_patient", help="Open menu"):
            st.session_state.menu_open = not st.session_state.menu_open
            st.rerun()

    st.markdown(f"<p class='patient-account-role'><strong>Account:</strong> {st.session_state.user_email} | <strong>Role:</strong> {st.session_state.user_role}</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get prescriptions for calculations
    patient_prescriptions = get_prescriptions_for_patient(st.session_state.get("user_email", ""))
    
    # Get appointments for next appointment metric
    patient_appointments = get_appointments_for_patient(st.session_state.get("user_email", ""))
    
    # Calculate next dose dynamically
    next_dose_info = get_next_medication_dose(patient_prescriptions)
    
    if next_dose_info:
        next_dose_time = next_dose_info["time"]
        next_dose_med = next_dose_info["medication"]
        next_dose_badge = next_dose_info["badge"]
    else:
        next_dose_time = "—"
        next_dose_med = "No medications scheduled"
        next_dose_badge = ""
    
    # Calculate adherence dynamically
    adherence_info = calculate_medication_adherence(patient_prescriptions)
    adherence_percent = adherence_info["adherence_percent"]
    adherence_trend = adherence_info["trend"]
    adherence_detail = f"Taken {adherence_info['taken']}/{adherence_info['total']} today"
    
    # Get next appointment info
    if patient_appointments:
        # Find the next upcoming appointment (future dates)
        from datetime import datetime as dt
        today = dt.now()
        future_appointments = [
            appt for appt in patient_appointments
            if appt.get('date') and appt['date'] >= today.strftime("%Y-%m-%d")
        ]
        if future_appointments:
            next_appt = future_appointments[0]
            try:
                appt_date = dt.strptime(next_appt['date'], "%Y-%m-%d").strftime("%b %d")
                next_appt_value = appt_date
                next_appt_detail = f"Dr. {next_appt.get('doctor_name', 'Unknown')}"
                next_appt_badge = next_appt.get('time', '')
            except:
                next_appt_value = "—"
                next_appt_detail = "Invalid date"
                next_appt_badge = ""
        else:
            next_appt_value = "—"
            next_appt_detail = "No upcoming appointments"
            next_appt_badge = ""
    else:
        next_appt_value = "—"
        next_appt_detail = "No appointments scheduled"
        next_appt_badge = ""
    
    # Patient summary metrics
    metrics = [
        {
            "icon": "⏰",
            "label": "Next Dose",
            "value": next_dose_time,
            "detail": next_dose_med,
            "badge": next_dose_badge,
        },
        {
            "icon": "📈",
            "label": "Medication Adherence",
            "value": f"{adherence_percent}%",
            "detail": adherence_detail,
            "badge": adherence_trend,
        },
        {
            "icon": "🩺",
            "label": "Next Appointment",
            "value": next_appt_value,
            "detail": next_appt_detail,
            "badge": next_appt_badge,
        },
    ]

    cols = st.columns(3)
    for col, metric in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="patient-metric-card">
                    <div class="patient-metric-head">
                        <span class="patient-metric-icon">{metric["icon"]}</span>
                        <span class="patient-metric-badge">{metric["badge"]}</span>
                    </div>
                    <p class="patient-metric-label">{metric["label"]}</p>
                    <h3 class="patient-metric-value">{metric["value"]}</h3>
                    <p class="patient-metric-detail">{metric["detail"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Patient Specific Tabs
    tab1, tab2, tab3 = st.tabs(["💊 My Medications", "🔔 Reminders", "🩺 Care Team"])
    
    with tab1:
        st.subheader("Active Prescriptions")

        if not patient_prescriptions:
            st.info("No prescriptions found yet.")
        else:
            diagnosis_options = sorted(
                {
                    (rx.get("diagnosis") or "Not specified").strip() or "Not specified"
                    for rx in patient_prescriptions
                }
            )
            medicine_options = sorted(
                {
                    (med.get("name") or "").strip()
                    for rx in patient_prescriptions
                    for med in rx.get("medicines", [])
                    if (med.get("name") or "").strip()
                }
            )
            doctor_options = sorted(
                {
                    (rx.get("doctor_name") or rx.get("doctor_email") or "Unknown doctor").strip()
                    for rx in patient_prescriptions
                }
            )

            st.markdown(
                "<h4 class='patient-filter-title'>Filter Medications</h4>",
                unsafe_allow_html=True,
            )
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            with filter_col1:
                st.markdown("<p class='patient-filter-label'>Diagnosis</p>", unsafe_allow_html=True)
                selected_diagnosis = st.selectbox(
                    "Diagnosis",
                    ["All"] + diagnosis_options,
                    key="patient_filter_diagnosis",
                    label_visibility="collapsed",
                )
            with filter_col2:
                st.markdown("<p class='patient-filter-label'>Medicine Name</p>", unsafe_allow_html=True)
                selected_medicine = st.selectbox(
                    "Medicine Name",
                    ["All"] + medicine_options,
                    key="patient_filter_medicine",
                    label_visibility="collapsed",
                )
            with filter_col3:
                st.markdown("<p class='patient-filter-label'>Doctor</p>", unsafe_allow_html=True)
                selected_doctor = st.selectbox(
                    "Doctor",
                    ["All"] + doctor_options,
                    key="patient_filter_doctor",
                    label_visibility="collapsed",
                )

            filtered_prescriptions = []
            for rx in patient_prescriptions:
                diagnosis_value = (rx.get("diagnosis") or "Not specified").strip() or "Not specified"
                doctor_value = (rx.get("doctor_name") or rx.get("doctor_email") or "Unknown doctor").strip()
                medicine_names = {
                    (med.get("name") or "").strip()
                    for med in rx.get("medicines", [])
                    if (med.get("name") or "").strip()
                }

                if selected_diagnosis != "All" and diagnosis_value != selected_diagnosis:
                    continue
                if selected_doctor != "All" and doctor_value != selected_doctor:
                    continue
                if selected_medicine != "All" and selected_medicine not in medicine_names:
                    continue

                filtered_prescriptions.append(rx)

            if not filtered_prescriptions:
                st.info("No prescriptions match the selected filters.")

            for idx, rx in enumerate(filtered_prescriptions, start=1):
                diagnosis = escape(rx.get("diagnosis") or "Not specified")
                created_at = escape((rx.get("created_at") or "")[:10])
                follow_up = rx.get("follow_up_days") or "-"
                doctor_name = escape((rx.get("doctor_name") or rx.get("doctor_email") or "Unknown doctor"))
                medicines = rx.get("medicines", [])
                if medicines:
                    med_lines = []
                    for med in medicines:
                        med_name = escape((med.get("name") or "").strip())
                        if not med_name:
                            continue
                        dosage = escape(str(med.get("dosage") or "-"))
                        frequency = escape(str(med.get("frequency") or "-"))
                        days = escape(str(med.get("days") or "-"))
                        directions = escape(str(med.get("directions") or "-"))
                        med_lines.append(
                            f"<li><span class='patient-med-name'>{med_name}</span>"
                            f"<span class='patient-med-meta'>Dosage: {dosage}, Frequency: {frequency}, Days: {days}</span>"
                            f"<span class='patient-med-dir'>Directions: {directions}</span></li>"
                        )
                else:
                    med_lines = ["<li><span class='patient-med-dir'>No medicine entries available.</span></li>"]

                st.markdown(
                    f"""
                    <div class="patient-rx-card">
                        <div class="patient-rx-head">
                            <span class="patient-rx-title">Prescription {idx}</span>
                            <span class="patient-rx-date">{created_at or "-"}</span>
                        </div>
                        <p class="patient-rx-doctor"><strong>Doctor:</strong> {doctor_name}</p>
                        <p class="patient-rx-diagnosis"><strong>Diagnosis:</strong> {diagnosis}</p>
                        <p class="patient-rx-followup"><strong>Follow-up:</strong> {follow_up} days</p>
                        <ul class="patient-med-list">
                            {''.join(med_lines)}
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        
    with tab2:
        st.subheader("Medication Schedule & Tracking")
        if not patient_prescriptions:
            st.info("No prescriptions found. Your medication schedule will appear here once you receive prescriptions.")
        else:
            medication_schedule = build_medication_schedule(patient_prescriptions)
            
            st.markdown("""
            <style>
            .med-schedule-card {
                background: #f8f9fa;
                border-left: 4px solid #26c485;
                padding: 16px;
                margin: 12px 0;
                border-radius: 4px;
            }
            .med-schedule-time {
                font-size: 16px;
                font-weight: 600;
                color: #0d47a1;
                margin-bottom: 12px;
            }
            .med-item {
                background: white;
                padding: 10px 12px;
                margin: 6px 0;
                border-radius: 4px;
                border-left: 3px solid #e0e0e0;
                font-size: 14px;
            }
            .med-name {
                font-weight: 600;
                color: #1a1a1a;
                display: block;
                margin-bottom: 4px;
            }
            .med-detail {
                color: #666;
                font-size: 13px;
                margin: 4px 0;
                display: block;
                line-height: 1.5;
            }
            .med-doctor {
                color: #888;
                font-size: 12px;
                font-style: italic;
                margin-top: 6px;
                display: block;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Display timeline
            has_medications = False
            for time_slot, medications in medication_schedule.items():
                if medications:
                    has_medications = True
                    
                    st.markdown(f"""<div style="background: #f8f9fa; border-left: 4px solid #26c485; padding: 16px; margin: 12px 0; border-radius: 4px;">
                        <div style="font-size: 16px; font-weight: 600; color: #0d47a1; margin-bottom: 12px;">{time_slot}</div>
                    </div>""", unsafe_allow_html=True)
                    
                    for idx, med in enumerate(medications):
                        med_name = escape(med["name"])
                        med_dosage = escape(med["dosage"])
                        med_frequency = escape(med["frequency"])
                        med_directions = escape(med["directions"]) if med["directions"] else ""
                        med_doctor = escape(med.get("doctor", "Unknown doctor"))
                        
                        # Create unique key for this medication dose
                        dose_key = f"{time_slot}_{med_name}_{idx}"
                        
                        # Create columns for checkbox and med info
                        cb_col, info_col = st.columns([0.5, 9.5])
                        
                        with cb_col:
                            # Checkbox to mark dose as taken
                            is_taken = st.checkbox(
                                "✓",
                                value=st.session_state.medication_doses_taken.get(dose_key, False),
                                key=dose_key,
                                label_visibility="collapsed"
                            )
                            # Update session state
                            st.session_state.medication_doses_taken[dose_key] = is_taken
                        
                        with info_col:
                            # Display medication info
                            st.markdown(f"""
                            <div style="background: white; padding: 10px 12px; margin: 6px 0; border-radius: 4px; border-left: 3px solid #e0e0e0; font-size: 14px;">
                                <span style="font-weight: 600; color: #1a1a1a; display: block; margin-bottom: 4px;">{med_name}</span>
                                <span style="color: #666; font-size: 13px; margin: 4px 0; display: block;"><strong>Dosage:</strong> {med_dosage}</span>
                                <span style="color: #666; font-size: 13px; margin: 4px 0; display: block;"><strong>Frequency:</strong> {med_frequency}</span>
                                {f'<span style="color: #666; font-size: 13px; margin: 4px 0; display: block;"><strong>Directions:</strong> {med_directions}</span>' if med_directions else ''}
                                <span style="color: #888; font-size: 12px; font-style: italic; margin-top: 6px; display: block;">Prescribed by: {med_doctor}</span>
                            </div>
                            """, unsafe_allow_html=True)
            
            if not has_medications:
                st.info("No active medications to display in schedule.")
        
    with tab3:
        st.subheader("Care Team")
        
        # Get care team from database (includes doctors from appointments and prescriptions)
        care_team = get_care_team_for_patient(st.session_state.get("user_email", ""))
        
        if not care_team:
            st.info("No doctors in your care team yet. Book an appointment or receive a prescription to add a doctor to your team!")
        else:
            st.markdown(
                f"<p style='color: #2e3d63; font-size: 16px; font-weight: 600; margin-bottom: 20px;'>Total Doctors: {len(care_team)}</p>",
                unsafe_allow_html=True
            )
            
            for doctor in care_team:
                doctor_name = escape(doctor['name'])
                speciality = escape(doctor['speciality'])
                email = escape(doctor['email'])
                office_hours = escape(doctor.get('office_hours') or 'Not specified')
                linked_date = doctor.get('linked_at', '')[:10] if doctor.get('linked_at') else 'N/A'
                
                care_team_card = f"""
                <div class="doctor-rx-card" style="margin-bottom: 20px; padding: 20px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #4a90e2;">
                    <div style="display: grid; grid-template-columns: 3fr 2fr; gap: 20px;">
                        <div>
                            <p style="color: #2e3d63; font-size: 16px; font-weight: 600; margin-bottom: 8px;">👨‍⚕️ Dr. {doctor_name}</p>
                            <p style="color: #5a6c7d; font-size: 14px; margin-bottom: 4px;">🩺 <strong>Specialty:</strong> {speciality}</p>
                            <p style="color: #5a6c7d; font-size: 14px; margin-bottom: 4px;">📧 {email}</p>
                        </div>
                        <div>
                            <p style="color: #5a6c7d; font-size: 14px; margin-bottom: 4px;"><strong>🕐 Office Hours:</strong></p>
                            <p style="color: #5a6c7d; font-size: 14px; margin-bottom: 8px;">{office_hours}</p>
                            <p style="color: #5a6c7d; font-size: 14px;"><strong>Added:</strong> {linked_date}</p>
                        </div>
                    </div>
                </div>
                """
                st.markdown(care_team_card, unsafe_allow_html=True)

    # Floating chatbot launcher for patient dashboard
    # Keep it hidden while the side menu is open so it does not block menu clicks.
    if not st.session_state.get("menu_open", False):
        render_floating_chatbot(
            st.session_state.get("user_name", ""),
            st.session_state.get("user_email", ""),
        )




def profile_edit_page():
    """Display profile details page, with optional edit mode."""
    load_custom_styles()
    init_menu_state()
    render_side_drawer()

    if "profile_edit_mode" not in st.session_state:
        st.session_state.profile_edit_mode = False

    def display_value(value):
        return value if value not in (None, "", "None") else "Not provided"

    header_col1, header_col2, header_col3 = st.columns([4.5, 1, 0.5])
    
    with header_col1:
        st.markdown("<h1 class='patient-welcome'>👤 My Profile</h1>", unsafe_allow_html=True)

    with header_col2:
        if not st.session_state.profile_edit_mode:
            if st.button("✏️ Edit Profile", key="open_profile_edit"):
                st.session_state.profile_edit_mode = True
                st.rerun()
        else:
            if st.button("❌ Cancel", key="cancel_profile_edit"):
                st.session_state.profile_edit_mode = False
                st.rerun()

    with header_col3:
        if st.button("☰", key="toggle_menu_profile", help="Open menu"):
            st.session_state.menu_open = not st.session_state.menu_open
            st.rerun()

    current_email = st.session_state.get("user_email", "")
    if not current_email:
        st.error("No user email found in session. Please log in again.")
        if st.button("< Back"):
            st.session_state.show_profile_edit = False
            st.rerun()
        return

    user_profile = get_user_profile(current_email)
    if not user_profile:
        st.error(f"Could not load profile information for {current_email}. Please try again.")
        if st.button("< Back"):
            st.session_state.show_profile_edit = False
            st.rerun()
        return

    st.markdown(
        f"<p class='patient-account-role'><strong>Account:</strong> {current_email} | "
        f"<strong>Role:</strong> {user_profile['role']}</p>",
        unsafe_allow_html=True,
    )
    
    # Add subtle fade-in animation
    st.markdown("""
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .profile-section-header, .profile-card {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # Profile information cards with better styling
    if not st.session_state.profile_edit_mode:
        st.markdown("""
        <style>
        .profile-section-header {
            background: linear-gradient(135deg, #0B2F5B 0%, #1a4d8f 100%);
            border-radius: 12px 12px 0 0;
            padding: 16px 24px;
            margin-bottom: 0;
        }
        .profile-section-header h3 {
            color: white;
            font-size: 1.1rem;
            font-weight: 600;
            margin: 0;
            display: flex;
            align-items: center;
        }
        .profile-card {
            background: white;
            border-radius: 0 0 12px 12px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 24px;
            border: 1px solid #e8e8e8;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .profile-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.12);
        }
        .profile-field {
            display: flex;
            padding: 14px 16px;
            margin-bottom: 8px;
            background: #f8f9fa;
            border-radius: 8px;
            transition: background 0.2s;
        }
        .profile-field:hover {
            background: #e9ecef;
        }
        .profile-field:last-child {
            margin-bottom: 0;
        }
        .profile-field-label {
            color: #495057;
            font-weight: 600;
            min-width: 140px;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
        }
        .profile-field-label::before {
            content: "•";
            color: #0B2F5B;
            font-weight: bold;
            font-size: 1.2rem;
            margin-right: 8px;
        }
        .profile-field-value {
            color: #212529;
            font-weight: 400;
            font-size: 0.9rem;
            flex: 1;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="profile-section-header">
                <h3>👤 Personal Information</h3>
            </div>
            <div class="profile-card">
                <div class="profile-field">
                    <div class="profile-field-label">Full Name</div>
                    <div class="profile-field-value">{}</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Email</div>
                    <div class="profile-field-value">{}</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Role</div>
                    <div class="profile-field-value">{}</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Date of Birth</div>
                    <div class="profile-field-value">{}</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Gender</div>
                    <div class="profile-field-value">{}</div>
                </div>
            </div>
            """.format(
                display_value(user_profile.get('name')),
                display_value(user_profile.get('email')),
                display_value(user_profile.get('role')),
                display_value(user_profile.get('dob')),
                display_value(user_profile.get('gender'))
            ), unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="profile-section-header">
                <h3>📞 Contact Information</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Build contact information HTML
            contact_fields = """
            <div class="profile-card">
                <div class="profile-field">
                    <div class="profile-field-label">Phone</div>
                    <div class="profile-field-value">{}</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Address</div>
                    <div class="profile-field-value">{}</div>
                </div>""".format(
                display_value(user_profile.get('phone')),
                display_value(user_profile.get('address'))
            )
            
            # Add doctor-specific fields if applicable
            if user_profile.get("role") == "Doctor":
                contact_fields += """
                <div class="profile-field">
                    <div class="profile-field-label">Speciality</div>
                    <div class="profile-field-value">{}</div>
                </div>
                <div class="profile-field">
                    <div class="profile-field-label">Office Hours</div>
                    <div class="profile-field-value">{}</div>
                </div>""".format(
                    display_value(user_profile.get('speciality')),
                    display_value(user_profile.get('office_hours'))
                )
            
            contact_fields += """
            </div>"""
            
            st.markdown(contact_fields, unsafe_allow_html=True)

    if st.session_state.profile_edit_mode:
        st.markdown("---")
        
        # Center the edit form
        form_left, form_center, form_right = st.columns([1, 3, 1])
        
        with form_center:
            st.markdown("<h3 style='text-align: center;'>✏️ Edit Profile Information</h3>", unsafe_allow_html=True)
            
            with st.form("profile_edit_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Personal Details")
                    new_name = st.text_input(
                        "Full Name",
                        value=user_profile.get("name", ""),
                        placeholder="Enter your full name",
                    )
                    new_email = st.text_input(
                        "Email",
                        value=user_profile.get("email", ""),
                        placeholder="Enter your email",
                    )
                
                with col2:
                    st.markdown("#### Contact Details")
                    new_address = st.text_area(
                        "Address",
                        value=user_profile.get("address", ""),
                        placeholder="Enter your complete address",
                        height=137,
                    )

                submit = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")

                if submit:
                    if not new_name or not new_name.strip():
                        st.error("Name cannot be empty.")
                        return
                    if not new_email or not new_email.strip():
                        st.error("Email cannot be empty.")
                        return

                    email_changed = new_email != current_email
                    name_changed = new_name != user_profile.get("name", "")
                    success, message = update_user_profile(
                        current_email,
                        name=new_name,
                        new_email=new_email if email_changed else None,
                        address=new_address,
                    )

                    if success:
                        if name_changed:
                            st.session_state.user_name = new_name
                        if email_changed:
                            st.session_state.user_email = new_email

                        st.session_state.profile_edit_mode = False
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
