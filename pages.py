"""
Page components for the MedMinder app
"""

import streamlit as st


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
		btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
        
		with btn_col1:
			if st.button("Sign In", use_container_width=True, key="signin_hero"):
				st.session_state.show_auth = True
				st.rerun()
        
		with btn_col2:
			if st.button("Sign Up", use_container_width=True, key="signup_hero"):
				st.session_state.show_auth = True
				st.session_state.show_signup = True 
				st.rerun()
    
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
    from auth import authenticate_user, create_user

    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🔐 Welcome to MedMinder</h1>", unsafe_allow_html=True)

    # Back to landing page button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Back", key="back_button", use_container_width=True):
            st.session_state.show_auth = False
            if "role" in st.session_state:
                del st.session_state.role
            if "show_signup" in st.session_state:
                del st.session_state.show_signup
            st.rerun()

    # Set the default active tab to Sign Up if show_signup is True
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False

    # Show only the Sign Up tab if show_signup is True
    if st.session_state.show_signup:
        tab2 = st.container()
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)

            if "role" not in st.session_state:
                st.markdown("<h3 style='color: #4CAF50; text-align: center; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>Select Your Role</h3>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)  

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Doctor", key="doctor_button", use_container_width=True):
                        st.session_state.role = "Doctor"
                        st.session_state.show_signup = True
                        st.rerun()
                with col2:
                    if st.button("Patient", key="patient_button", use_container_width=True):
                        st.session_state.role = "Patient"
                        st.session_state.show_signup = True
                        st.rerun()

            if "role" in st.session_state:
                if st.session_state.role == "Doctor":
                    with st.form("doctor_onboarding_form"):
                        st.markdown("<h3 style='color: #4CAF50;'>Doctor Onboarding</h3>", unsafe_allow_html=True)
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            first_name = st.text_input("First Name", placeholder="Enter your first name")
                        with col2:
                            last_name = st.text_input("Last Name", placeholder="Enter your last name")
                        dob = st.date_input("Date of Birth")
                        gender = st.radio("Gender", ["Male", "Female", "Other"], horizontal=True)

                        st.markdown("<h4 style='color: #4CAF50;'>Office Location</h4>", unsafe_allow_html=True)
                        line1 = st.text_input("Address Line 1", placeholder="Enter address line 1")
                        line2 = st.text_input("Address Line 2", placeholder="Enter address line 2")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            city = st.text_input("City", placeholder="Enter city")
                            state = st.selectbox("State", ["State 1", "State 2", "State 3"], index=0)
                        with col2:
                            zip_code = st.text_input("Zip Code", placeholder="Enter zip code")
                            country = st.selectbox("Country", ["Country 1", "Country 2", "Country 3"], index=0)

                        st.markdown("<h4 style='color: #4CAF50;'>Professional Details</h4>", unsafe_allow_html=True)
                        phone = st.text_input("Phone", placeholder="Enter phone number")
                        speciality = st.selectbox("Speciality", ["Cardiologist", "Dentist", "Neurologist", "Pediatrician", "General Practitioner"], index=0)
                        off_day = st.radio("Off Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], horizontal=True)
                        office_hours = st.radio("Office Hours", ["8:00 AM to 5:00 PM", "9:00 AM to 6:00 PM"], horizontal=True)

                        st.markdown("<h4 style='color: #4CAF50;'>Account Details</h4>", unsafe_allow_html=True)
                        email = st.text_input("Email", placeholder="Enter your email")
                        password = st.text_input("Password", type="password", placeholder="Enter your password")
                        submit = st.form_submit_button("Sign Up", use_container_width=True)

                        if submit:
                            success, message = create_user(f"{first_name} {last_name}", email, password)
                            if success:
                                st.success(message + " Please sign in.")
                                st.rerun()
                            else:
                                st.error(message)

                elif st.session_state.role == "Patient":
                    with st.form("patient_onboarding_form"):
                        st.markdown("<h3 style='color: #4CAF50;'>Patient Onboarding</h3>", unsafe_allow_html=True)
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            first_name = st.text_input("First Name", placeholder="Enter your first name")
                        with col2:
                            last_name = st.text_input("Last Name", placeholder="Enter your last name")
                        dob = st.date_input("Date of Birth")
                        gender = st.radio("Gender", ["Male", "Female", "Other"], horizontal=True)

                        st.markdown("<h4 style='color: #4CAF50;'>Address</h4>", unsafe_allow_html=True)
                        line1 = st.text_input("Address Line 1", placeholder="Enter address line 1")
                        line2 = st.text_input("Address Line 2", placeholder="Enter address line 2")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            city = st.text_input("City", placeholder="Enter city")
                            state = st.selectbox("State", ["State 1", "State 2", "State 3"], index=0)
                        with col2:
                            zip_code = st.text_input("Zip Code", placeholder="Enter zip code")
                            country = st.selectbox("Country", ["Country 1", "Country 2", "Country 3"], index=0)
                        phone = st.text_input("Phone", placeholder="Enter phone number")

                        st.markdown("<h4 style='color: #4CAF50;'>Account Details</h4>", unsafe_allow_html=True)
                        email = st.text_input("Email", placeholder="Enter your email")
                        password = st.text_input("Password", type="password", placeholder="Enter your password")
                        submit = st.form_submit_button("Sign Up", use_container_width=True)

                        if submit:
                            success, message = create_user(f"{first_name} {last_name}", email, password)
                            if success:
                                st.success(message + " Please sign in.")
                                st.rerun()
                            else:
                                st.error(message)

    else:
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

        # Sign In Tab
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("signin_form"):
                st.subheader("Sign In to Your Account")
                email = st.text_input("Email", placeholder="Enter your email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Sign In", use_container_width=True)

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
            st.session_state.show_signup = True
            st.markdown("<br>", unsafe_allow_html=True)

            if "role" not in st.session_state:
                st.markdown("<h3 style='color: #4CAF50; text-align: center; background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>Select Your Role</h3>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)  

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Doctor", key="doctor_button", use_container_width=True):
                        st.session_state.role = "Doctor"
                        st.session_state.show_signup = True
                        st.rerun()
                with col2:
                    if st.button("Patient", key="patient_button", use_container_width=True):
                        st.session_state.role = "Patient"
                        st.session_state.show_signup = True
                        st.rerun()

            if "role" in st.session_state:
                if st.session_state.role == "Doctor":
                    with st.form("doctor_onboarding_form"):
                        st.markdown("<h3 style='color: #4CAF50;'>Doctor Onboarding</h3>", unsafe_allow_html=True)
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            first_name = st.text_input("First Name", placeholder="Enter your first name")
                        with col2:
                            last_name = st.text_input("Last Name", placeholder="Enter your last name")
                        dob = st.date_input("Date of Birth")
                        gender = st.radio("Gender", ["Male", "Female", "Other"], horizontal=True)

                        st.markdown("<h4 style='color: #4CAF50;'>Office Location</h4>", unsafe_allow_html=True)
                        line1 = st.text_input("Address Line 1", placeholder="Enter address line 1")
                        line2 = st.text_input("Address Line 2", placeholder="Enter address line 2")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            city = st.text_input("City", placeholder="Enter city")
                            state = st.selectbox("State", ["State 1", "State 2", "State 3"], index=0)
                        with col2:
                            zip_code = st.text_input("Zip Code", placeholder="Enter zip code")
                            country = st.selectbox("Country", ["Country 1", "Country 2", "Country 3"], index=0)

                        st.markdown("<h4 style='color: #4CAF50;'>Professional Details</h4>", unsafe_allow_html=True)
                        phone = st.text_input("Phone", placeholder="Enter phone number")
                        speciality = st.selectbox("Speciality", ["Cardiologist", "Dentist", "Neurologist", "Pediatrician", "General Practitioner"], index=0)
                        off_day = st.radio("Off Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], horizontal=True)
                        office_hours = st.radio("Office Hours", ["8:00 AM to 5:00 PM", "9:00 AM to 6:00 PM"], horizontal=True)

                        st.markdown("<h4 style='color: #4CAF50;'>Account Details</h4>", unsafe_allow_html=True)
                        email = st.text_input("Email", placeholder="Enter your email")
                        password = st.text_input("Password", type="password", placeholder="Enter your password")
                        submit = st.form_submit_button("Sign Up", use_container_width=True)

                        if submit:
                            success, message = create_user(f"{first_name} {last_name}", email, password)
                            if success:
                                st.success(message + " Please sign in.")
                                st.rerun()
                            else:
                                st.error(message)

                elif st.session_state.role == "Patient":
                    with st.form("patient_onboarding_form"):
                        st.markdown("<h3 style='color: #4CAF50;'>Patient Onboarding</h3>", unsafe_allow_html=True)
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            first_name = st.text_input("First Name", placeholder="Enter your first name")
                        with col2:
                            last_name = st.text_input("Last Name", placeholder="Enter your last name")
                        dob = st.date_input("Date of Birth")
                        gender = st.radio("Gender", ["Male", "Female", "Other"], horizontal=True)

                        st.markdown("<h4 style='color: #4CAF50;'>Address</h4>", unsafe_allow_html=True)
                        line1 = st.text_input("Address Line 1", placeholder="Enter address line 1")
                        line2 = st.text_input("Address Line 2", placeholder="Enter address line 2")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            city = st.text_input("City", placeholder="Enter city")
                            state = st.selectbox("State", ["State 1", "State 2", "State 3"], index=0)
                        with col2:
                            zip_code = st.text_input("Zip Code", placeholder="Enter zip code")
                            country = st.selectbox("Country", ["Country 1", "Country 2", "Country 3"], index=0)
                        phone = st.text_input("Phone", placeholder="Enter phone number")

                        st.markdown("<h4 style='color: #4CAF50;'>Account Details</h4>", unsafe_allow_html=True)
                        email = st.text_input("Email", placeholder="Enter your email")
                        password = st.text_input("Password", type="password", placeholder="Enter your password")
                        submit = st.form_submit_button("Sign Up", use_container_width=True)

                        if submit:
                            success, message = create_user(f"{first_name} {last_name}", email, password)
                            if success:
                                st.success(message + " Please sign in.")
                                st.rerun()
                            else:
                                st.error(message)


def dashboard_page():
	"""Display the dashboard for logged-in users"""
	st.markdown(f"# 👋 Welcome, {st.session_state.user_name}!")
	st.markdown(f"**Email:** {st.session_state.user_email}")
	st.markdown("You have successfully logged in to your account.")
    
	st.markdown("---")
    
	col1, col2, col3 = st.columns([1, 1, 1])
	with col2:
		if st.button("🚪 Logout", use_container_width=True):
			st.session_state.logged_in = False
			st.session_state.user_name = ""
			st.session_state.user_email = ""
			st.session_state.show_auth = False
			st.rerun()

