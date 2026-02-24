"""
Page components for the MedMinder app
"""

from datetime import date, timedelta

import streamlit as st
from auth import authenticate_user, create_user
from prescription import save_prescription
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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown('<div class="auth-back">', unsafe_allow_html=True)
        if st.button("← Back", key="back_button"):
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
                speciality = st.selectbox(
                    "Speciality",
                    ["Cardiologist", "Dentist", "Neurologist", "Pediatrician", "General Practitioner"],
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

def doctor_dashboard_page():
    """Display the dashboard specifically for Doctors"""
    load_custom_styles()
    saved_notice = st.session_state.pop("prescription_saved_notice", None)
    if saved_notice:
        st.markdown(
            f"<div class='prescription-toast'>{saved_notice}</div>",
            unsafe_allow_html=True,
        )

    header_col, logout_col = st.columns([6, 1.4])
    with header_col:
        st.markdown(f"<h1 class='doctor-welcome'>🩺 Welcome back, Dr. {st.session_state.user_name}!</h1>", unsafe_allow_html=True)
    with logout_col:
        st.markdown('<div class="patient-top-logout">', unsafe_allow_html=True)
        st.markdown('<a class="patient-logout-link" href="?logout=1">Logout</a>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<p class='doctor-account-role'><strong>Account:</strong> {st.session_state.user_email} | <strong>Role:</strong> {st.session_state.user_role}</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Doctor summary metrics
    metrics = [
        {
            "icon": "👥",
            "label": "Total Patients",
            "value": "142",
            "detail": "3 new this week",
            "badge": "Active",
        },
        {
            "icon": "📅",
            "label": "Today's Appointments",
            "value": "8",
            "detail": "2 follow-ups pending",
            "badge": "Today",
        },
        {
            "icon": "💊",
            "label": "Refill Requests",
            "value": "12",
            "detail": "Action required",
            "badge": "Urgent",
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
        st.info("Patient search and management table will go here.")
        
    with tab2:
        st.subheader("Today's Schedule")
        st.info("Calendar view and appointment details will go here.")
        
    with tab3:
        st.subheader("Manage Prescriptions")
        st.markdown("<p class='doctor-rx-subtitle'>Select a patient and start a prescription.</p>", unsafe_allow_html=True)
        dummy_patients = [
            {"name": "Ethan Carter", "note": "Hypertension follow-up"},
            {"name": "Sophia Bennett", "note": "Diabetes management"},
            {"name": "Liam Brooks", "note": "Post-op medication review"},
            {"name": "Olivia Hayes", "note": "Migraine treatment plan"},
            {"name": "Noah Turner", "note": "Asthma refill request"},
        ]

        for idx, patient in enumerate(dummy_patients):
            name_col, action_col = st.columns([3.6, 1.4])
            with name_col:
                st.markdown(
                    f"""
                    <div class="doctor-rx-card">
                        <p class="doctor-rx-name">{patient["name"]}</p>
                        <p class="doctor-rx-note">{patient["note"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with action_col:
                if st.button("Prescribe", key=f"prescribe_{idx}", use_container_width=True):
                    st.session_state.show_prescription = True
                    st.session_state.selected_patient = patient["name"]
                    st.rerun()


def prescription_page():
    """Display prescription page for the selected patient."""
    load_custom_styles()

    header_col, logout_col = st.columns([6, 1.4])
    with header_col:
        st.markdown("<h1 class='doctor-welcome'>💊 Create Prescription</h1>", unsafe_allow_html=True)
    with logout_col:
        st.markdown('<div class="patient-top-logout">', unsafe_allow_html=True)
        st.markdown('<a class="patient-logout-link" href="?logout=1">Logout</a>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    patient_name = st.session_state.get("selected_patient", "Unknown Patient")
    st.markdown(f"<p class='doctor-account-role'><strong>Patient:</strong> {patient_name}</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("Prescription Details")

    with st.form("prescription_form"):
        st.markdown("#### Clinical Summary")
        diagnosis = st.text_input("Diagnosis", placeholder="e.g., Type 2 Diabetes Mellitus")
        follow_up_days = st.number_input("Follow-up in (days)", min_value=1, max_value=180, value=30, step=1)
        general_notes = st.text_area("General Notes", placeholder="Add overall notes for this prescription...")

        st.markdown("#### Medicines")
        total_medicines = st.selectbox("Total Medicines", [1, 2, 3, 4, 5], index=2)

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
                    st.rerun()
                else:
                    st.error(message)

    if st.button("← Back to Doctor Dashboard", key="back_to_doctor"):
        st.session_state.show_prescription = False
        st.rerun()


def patient_dashboard_page():
    """Display the dashboard specifically for Patients"""
    load_custom_styles()

    header_col, logout_col = st.columns([6, 1.4])
    with header_col:
        st.markdown(f"<h1 class='patient-welcome'>👋 Welcome back, {st.session_state.user_name}!</h1>", unsafe_allow_html=True)
    with logout_col:
        st.markdown('<div class="patient-top-logout">', unsafe_allow_html=True)
        st.markdown('<a class="patient-logout-link" href="?logout=1">Logout</a>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<p class='patient-account-role'><strong>Account:</strong> {st.session_state.user_email} | <strong>Role:</strong> {st.session_state.user_role}</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Patient summary metrics
    metrics = [
        {
            "icon": "⏰",
            "label": "Next Dose",
            "value": "2:00 PM",
            "detail": "Lisinopril 10mg",
            "badge": "Today",
        },
        {
            "icon": "📈",
            "label": "Medication Adherence",
            "value": "94%",
            "detail": "Great job this week",
            "badge": "+2%",
        },
        {
            "icon": "🩺",
            "label": "Next Appointment",
            "value": "Oct 12",
            "detail": "Dr. Smith",
            "badge": "10:30 AM",
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
        st.info("List of current medications and refill request buttons will go here.")
        
    with tab2:
        st.subheader("Medication Schedule")
        st.info("Daily timeline of when to take medications will go here.")
        
    with tab3:
        st.subheader("Contact Doctor")
        st.info("Secure messaging interface with care providers will go here.")

    # Floating chatbot launcher for patient dashboard
    render_floating_chatbot()
