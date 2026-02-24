"""
CSS styling for the app.
"""

def get_chatbot_component_css():
    """Return chatbot component CSS for the floating iframe UI."""
    return """
        html, body {
            margin: 0;
            padding: 0;
            background: transparent;
            overflow: visible;
            font-family: 'Inter', 'Arial', sans-serif;
        }

        .mm-chatbot-wrap {
            position: fixed;
            right: 24px;
            bottom: 24px;
            z-index: 1000;
        }

        .mm-chatbot-toggle {
            display: none;
        }

        .mm-chatbot-btn {
            width: 60px;
            height: 60px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.65rem;
            cursor: pointer;
            background: linear-gradient(140deg, #00bfa5 0%, #1a237e 100%);
            color: #ffffff;
            box-shadow: 0 12px 28px rgba(8, 29, 83, 0.35);
            border: 2px solid rgba(255, 255, 255, 0.3);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }

        .mm-chatbot-btn:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 16px 32px rgba(8, 29, 83, 0.4);
        }

        .mm-chatbot-panel {
            position: absolute;
            right: 0;
            bottom: 78px;
            width: min(340px, calc(100vw - 32px));
            border-radius: 16px;
            overflow: hidden;
            background: #ffffff;
            border: 1px solid rgba(26, 35, 126, 0.18);
            box-shadow: 0 20px 46px rgba(8, 29, 83, 0.35);
            opacity: 0;
            transform: translateY(8px) scale(0.98);
            pointer-events: none;
            transition: opacity 0.18s ease, transform 0.18s ease;
        }

        .mm-chatbot-toggle:checked ~ .mm-chatbot-panel {
            opacity: 1;
            transform: translateY(0) scale(1);
            pointer-events: auto;
        }

        .mm-chatbot-header {
            padding: 0.8rem 0.95rem;
            color: #ffffff;
            font-weight: 700;
            background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
            font-size: 0.92rem;
            letter-spacing: 0.02em;
        }

        .mm-chatbot-body {
            padding: 0.9rem;
            background: #f5f8ff;
        }

        .mm-chatbot-message {
            margin: 0;
            width: fit-content;
            max-width: 100%;
            color: #0f1b55;
            background: #eaf0ff;
            border: 1px solid #d5e2ff;
            border-radius: 12px 12px 12px 2px;
            padding: 0.55rem 0.7rem;
            font-size: 0.9rem;
            line-height: 1.35;
        }

        .mm-chatbot-message.user {
            margin-left: auto;
            border-radius: 12px 12px 2px 12px;
            background: #d9f8f3;
            border-color: #bdeee6;
            color: #06463d;
        }

        .mm-chatbot-thread {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            margin-bottom: 0.8rem;
            max-height: 180px;
            overflow-y: auto;
            padding-right: 0.2rem;
        }

        .mm-chatbot-composer {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding-top: 0.2rem;
        }

        .mm-chatbot-input {
            flex: 1;
            border: 1px solid #cfdcff;
            background: #ffffff;
            color: #1a237e;
            border-radius: 999px;
            padding: 0.5rem 0.8rem;
            font-size: 0.86rem;
            outline: none;
        }

        .mm-chatbot-input:focus {
            border-color: #00bfa5;
            box-shadow: 0 0 0 2px rgba(0, 191, 165, 0.18);
        }

        .mm-chatbot-send {
            border: none;
            border-radius: 999px;
            background: linear-gradient(140deg, #00bfa5 0%, #1a237e 100%);
            color: #ffffff;
            font-weight: 700;
            font-size: 0.78rem;
            padding: 0.48rem 0.78rem;
            cursor: pointer;
            white-space: nowrap;
        }

        @media (max-width: 640px) {
            .mm-chatbot-wrap {
                right: 14px;
                bottom: 14px;
            }

            .mm-chatbot-btn {
                width: 56px;
                height: 56px;
            }

            .mm-chatbot-panel {
                bottom: 72px;
                width: min(320px, calc(100vw - 24px));
            }
        }
    """

def load_custom_styles():
    """Load and apply custom CSS styling"""
    styles = """
        <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            border: none !important;
            font-family: 'Inter', 'Arial', sans-serif;
        }
        
        html, body, .stApp, .main {
            height: 100%;
            min-height: 100vh;
        }
        
        .main {
            background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%);
            color: #fff;
            border: none !important;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%);
            border: none !important;
        }
        
        /* Top Info Bar */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.25rem 2rem;
            background: linear-gradient(90deg, #e8f0ff 0%, #b3d1ff 100%);
            box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
        }
        
        .top-bar-left {
            display: flex;
            align-items: center;
        }
        
        .top-bar-logo {
            font-size: 1.15rem;
            font-weight: 800;
            color: white;
            letter-spacing: 1.2px;
            background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
            padding: 0.45rem 1.0rem;
            border-radius: 20px;
            box-shadow: 0 3px 8px rgba(26, 35, 126, 0.18);
        }
        
        .top-bar-right {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .info-block {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.85rem;
            color: #333;
        }
        
        .info-icon {
            font-size: 1.2rem;
        }
        
        .info-text {
            font-weight: 500;
        }
        
        /* Hide Streamlit decorations */
        #MainMenu {
            visibility: hidden;
        }
        
        footer {
            visibility: hidden;
        }
        
        header {
            visibility: hidden;
        }
        
        /* Hero Section */
        .hero-container {
            padding: 2rem 2rem 1.5rem 2rem;
            min-height: auto;
            display: flex;
            align-items: center;
            margin-top: 1.25rem; /* extra gap below navbar */
        }

        
        .hero-left {
            padding-right: 2rem;
        }
        
        .tagline {
            color: #00BFA5;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: white;
            margin-bottom: 1rem;
            line-height: 1.2;
        }
        
        .hero-subtitle {
            font-size: 1rem;
            color: rgba(255, 255, 255, 0.85);
            margin-bottom: 1.5rem;
            line-height: 1.5;
            max-width: 500px;
        }
        
        
        /* Card */
        .hero-card {
            background: white;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .heart-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        
        .card-title {
            color: #1a237e;
            font-weight: 700;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .card-text {
            color: #666;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }
        
        .social-links {
            display: flex;
            justify-content: center;
            gap: 1rem;
        }
        
        .social-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #2196F3 0%, #1565C0 100%);
            color: white;
            border-radius: 50%;
            text-decoration: none;
            transition: all 0.3s ease;
            font-size: 1.2rem;
        }
        
        .social-link:hover {
            background: #1a9a8f;
            transform: translateY(-3px);
        }

        /* Auth Page */
        .auth-container {
            max-width: 980px;
            margin: 0.85rem auto 1.0rem auto;
            padding: 0.85rem 2rem 1.2rem 2rem;
            background: transparent;
            border-radius: 18px;
            box-shadow: none;
            backdrop-filter: none;
        }

        .auth-title {
            text-align: center;
            color: #ffffff;
            font-size: 2.0rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            letter-spacing: 0.5px;
        }

        .auth-section-title {
            color: #ffffff;
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
        }

        .auth-subtitle {
            color: #e0f2f1;
            font-size: 1.05rem;
            font-weight: 600;
            margin: 1rem 0 0.5rem 0;
        }

        .auth-role-title {
            color: #0d47a1;
            background: linear-gradient(135deg, #e8f0ff 0%, #b3d1ff 100%);
            text-align: center;
            padding: 0.75rem 1rem;
            border-radius: 10px;
            font-weight: 700;
            margin-bottom: 1rem;
        }

        div[data-testid="stTabs"] {
            max-width: 720px;
            margin: 0 auto;
            background: #ffffff;
            padding: 0.75rem 1rem 1rem 1rem;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        div[data-testid="stTabs"] div[data-testid="stTabContent"] {
            padding: 0.5rem 0 0 0;
            background: transparent;
        }

        div[data-testid="stTabs"] div[data-baseweb="tab-list"] {
            background: #e8f0ff;
            border-radius: 10px;
            padding: 0.35rem;
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            width: 100%;
            margin: 0;
        }

        div[data-testid="stTabs"] button[role="tab"] {
            flex: 1 1 0;
            color: #1a237e;
            background: #e8f0ff;
            font-size: 1.15rem;
            padding: 0.75rem 1.8rem;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #c7d8ff;
            text-decoration: none;
            box-shadow: none;
            outline: none;
        }

        div[data-testid="stTabs"] button[role="tab"]:focus,
        div[data-testid="stTabs"] button[role="tab"]:focus-visible {
            outline: none;
            box-shadow: none;
        }

        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            background: #1a237e;
            color: #ffffff;
        }

        div[data-testid="stTabs"] h1,
        div[data-testid="stTabs"] h2,
        div[data-testid="stTabs"] h3,
        div[data-testid="stTabs"] h4 {
            color: #1a237e !important;
            text-align: center;
        }

        div[data-testid="stTabs"] button[role="tab"]::after,
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"]::after {
            background: transparent !important;
            height: 0 !important;
        }

        div[data-testid="stTabs"] div[data-baseweb="tab"],
        div[data-testid="stTabs"] div[data-baseweb="tab"]::after,
        div[data-testid="stTabs"] div[data-baseweb="tab"]::before {
            border-bottom: 0 !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        div[data-testid="stTabs"] div[data-baseweb="tab"][aria-selected="true"] {
            border-bottom: 3px solid #00BFA5 !important;
            box-shadow: inset 0 -3px 0 #00BFA5 !important;
        }

        div[data-testid="stTabs"] div[data-testid="stForm"] {
            background: transparent;
            box-shadow: none;
            padding: 0.75rem 0 0 0;
            margin: 0;
            max-width: 100%;
        }

        .auth-back .stButton>button {
            width: auto !important;
            min-width: 48px;
            padding: 0.2rem 0.45rem !important;
            background: #0d47a1 !important;
            color: rgba(255, 255, 255, 0.9) !important;
            font-size: 0.68rem;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            box-shadow: none !important;
            line-height: 1;
        }

        .auth-back .stButton>button:hover {
            background: #0b3b86 !important;
            transform: none !important;
            box-shadow: none !important;
        }

        .patient-welcome,
        .patient-account-role,
        .doctor-welcome,
        .doctor-account-role {
            color: #ffffff !important;
        }

        .patient-metric-card {
            background: linear-gradient(160deg, rgba(255, 255, 255, 0.2) 0%, rgba(19, 62, 151, 0.38) 100%);
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 16px;
            padding: 1rem 1rem 0.95rem 1rem;
            min-height: 176px;
            box-shadow: 0 14px 30px rgba(8, 29, 83, 0.28);
            backdrop-filter: blur(8px);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .patient-metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 18px 34px rgba(8, 29, 83, 0.34);
        }

        .patient-metric-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }

        .patient-metric-icon {
            width: 34px;
            height: 34px;
            border-radius: 10px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.05rem;
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.28) !important;
        }

        .patient-metric-badge {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #e6f2ff;
            background: rgba(0, 191, 165, 0.22);
            border: 1px solid rgba(0, 191, 165, 0.5) !important;
            border-radius: 999px;
            padding: 0.2rem 0.55rem;
        }

        .patient-metric-label {
            color: rgba(255, 255, 255, 0.78);
            font-size: 0.84rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            margin-bottom: 0.35rem;
        }

        .patient-metric-value {
            color: #ffffff;
            font-size: 1.55rem;
            font-weight: 800;
            line-height: 1.15;
            margin-bottom: 0.3rem;
        }

        .patient-metric-detail {
            color: rgba(232, 244, 255, 0.92);
            font-size: 0.9rem;
            margin-bottom: 0;
        }

        .doctor-rx-subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 0.93rem;
            margin-bottom: 0.55rem;
        }

        .doctor-rx-card {
            background: #f7faff;
            border: 1px solid #d9e6ff !important;
            border-radius: 12px;
            padding: 0.62rem 0.8rem;
            margin-bottom: 0.55rem;
            box-shadow: 0 6px 16px rgba(26, 35, 126, 0.12);
        }

        .doctor-rx-name {
            color: #1a237e;
            font-size: 0.95rem;
            font-weight: 700;
            margin-bottom: 0.12rem;
        }

        .doctor-rx-note {
            color: #4f5b7a;
            font-size: 0.82rem;
            margin-bottom: 0;
        }

        div[data-testid="stButton"] > button[id*="prescribe_"] {
            background: linear-gradient(135deg, #42a5f5 0%, #1e88e5 55%, #1565c0 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.24) !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            letter-spacing: 0.01em;
            min-width: 132px !important;
            padding: 0.62rem 0.95rem !important;
            font-size: 0.9rem !important;
            box-shadow: 0 8px 20px rgba(21, 101, 192, 0.32) !important;
        }

        div[data-testid="stButton"] > button[id*="prescribe_"]:hover {
            transform: translateY(-1px);
            filter: brightness(1.04);
            background: linear-gradient(135deg, #64b5f6 0%, #2196f3 55%, #1976d2 100%) !important;
            box-shadow: 0 12px 24px rgba(21, 101, 192, 0.38) !important;
        }

        div[data-testid="stButton"] > button[id*="prescribe_"]:focus,
        div[data-testid="stButton"] > button[id*="prescribe_"]:focus-visible {
            outline: none !important;
            box-shadow: 0 0 0 3px rgba(66, 165, 245, 0.22), 0 8px 20px rgba(21, 101, 192, 0.32) !important;
        }
        
        /* Form Styling */
        div[data-testid="stForm"] {
            background: #ffffff;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            max-width: 720px;
            margin: 0 auto;
        }

        /* Form text contrast on white backgrounds */
        div[data-testid="stForm"] {
            color: #1a237e !important;
        }

        div[data-testid="stForm"] h1,
        div[data-testid="stForm"] h2,
        div[data-testid="stForm"] h3,
        div[data-testid="stForm"] h4,
        div[data-testid="stForm"] h5,
        div[data-testid="stForm"] h6,
        div[data-testid="stForm"] label,
        div[data-testid="stForm"] p {
            color: #1a237e !important;
        }

        div[data-testid="stForm"] .stMarkdown {
            color: #1a237e !important;
        }

        div[data-testid="stForm"] input,
        div[data-testid="stForm"] textarea,
        div[data-testid="stForm"] select {
            color: #111111 !important;
            -webkit-text-fill-color: #111111 !important;
        }

        div[data-testid="stForm"] input::placeholder,
        div[data-testid="stForm"] textarea::placeholder {
            color: #6b7280 !important;
            -webkit-text-fill-color: #6b7280 !important;
        }
        
        
        .stTextInput>div[data-baseweb="input"]>input {
            color: #333 !important;
            background-color: white !important;
        }
        
        .stButton>button {
            width: 100%;
            background: #00BFA5 !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem !important;
            font-size: 16px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stForm"] .stButton>button {
            width: auto !important;
            min-width: 130px;
            padding: 0.45rem 1.3rem !important;
            margin: 0.75rem 0 0 0;
            display: block;
            background: #1a237e !important;
            color: #ffffff !important;
        }

        div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] {
            display: flex;
            justify-content: center;
            align-items: center;
        }

        div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button *,
        div[data-testid="stForm"] .stButton>button * {
            color: #ffffff !important;
        }

        div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button:hover,
        div[data-testid="stForm"] .stButton>button:hover {
            background: #00BFA5 !important;
            color: #ffffff !important;
        }
        
        .stButton>button:hover {
            background: #1a9a8f !important;
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(32, 178, 170, 0.4) !important;
        }

        .stButton>button[aria-label="← Back"],
        .stButton>button[aria-label="Back"],
        .stButton>button[aria-label*="Back"],
        div[data-testid="stButton"] > button[aria-label*="Back"],
        button[title*="Back"],
        button[aria-label*="Back"] {
            width: auto !important;
            min-width: 48px !important;
            padding: 0.2rem 0.45rem !important;
            background: #0d47a1 !important;
            color: rgba(255, 255, 255, 0.9) !important;
            font-size: 0.68rem !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            box-shadow: none !important;
            line-height: 1 !important;
        }

        .stButton>button[aria-label="← Back"]:hover,
        .stButton>button[aria-label="Back"]:hover,
        .stButton>button[aria-label*="Back"]:hover,
        div[data-testid="stButton"] > button[aria-label*="Back"]:hover,
        button[title*="Back"]:hover,
        button[aria-label*="Back"]:hover {
            background: #0b3b86 !important;
            transform: none !important;
            box-shadow: none !important;
        }
        
        .patient-top-logout {
            display: flex;
            justify-content: flex-end;
            align-items: flex-start;
            padding-top: 0.15rem;
        }

        .patient-logout-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.35rem;
            min-width: 138px;
            padding: 0.62rem 1.05rem;
            border-radius: 14px;
            text-decoration: none !important;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            font-size: 0.9rem;
            font-weight: 800;
            background: linear-gradient(135deg, #ff8a65 0%, #ef5350 55%, #d84315 100%);
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.28);
            box-shadow: 0 10px 24px rgba(200, 72, 27, 0.35);
            transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease, background 0.18s ease;
        }

        .patient-logout-link:hover {
            transform: translateY(-1px);
            filter: brightness(1.04);
            background: linear-gradient(135deg, #ff9f7d 0%, #f0625a 55%, #e64a19 100%);
            box-shadow: 0 14px 28px rgba(200, 72, 27, 0.42);
            color: #ffffff !important;
            text-decoration: none !important;
        }

        .patient-logout-link:focus,
        .patient-logout-link:focus-visible {
            outline: none;
            box-shadow: 0 0 0 3px rgba(255, 138, 101, 0.24), 0 10px 24px rgba(200, 72, 27, 0.35);
            text-decoration: none !important;
        }

        button[id*="pat_logout"],
        button[id*="doc_logout"] {
            background: linear-gradient(135deg, #ff8a65 0%, #ef5350 55%, #d84315 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.28) !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            box-shadow: 0 10px 24px rgba(200, 72, 27, 0.35) !important;
            transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease, background 0.18s ease !important;
        }
        
        button[id*="pat_logout"]:hover,
        button[id*="doc_logout"]:hover {
            transform: translateY(-1px);
            filter: brightness(1.04);
            background: linear-gradient(135deg, #ff9f7d 0%, #f0625a 55%, #e64a19 100%) !important;
            box-shadow: 0 14px 28px rgba(200, 72, 27, 0.42) !important;
        }

        button[id*="pat_logout"]:focus,
        button[id*="pat_logout"]:focus-visible,
        button[id*="doc_logout"]:focus,
        button[id*="doc_logout"]:focus-visible {
            outline: none !important;
            box-shadow: 0 0 0 3px rgba(255, 138, 101, 0.24), 0 10px 24px rgba(200, 72, 27, 0.35) !important;
        }

        
        /* Reduce default Streamlit bottom padding */
        .block-container {
            padding-top: 2.5rem !important;
            padding-bottom: 1.25rem !important;
            margin-bottom: 0 !important;
        }
        </style>
    """
    return styles
