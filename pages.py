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
    
	st.markdown("<h1>🔐 Welcome</h1>", unsafe_allow_html=True)
    
	# Back to landing page button
	col1, col2, col3 = st.columns([1, 2, 1])
	with col1:
		if st.button("← Back"):
			st.session_state.show_auth = False
			st.rerun()
    
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

