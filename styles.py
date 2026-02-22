"""
CSS styling for the app.
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
            color: #ffffff !important;
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
        
        .logout-button>button {
            background: #dc3545 !important;
        }
        
        .logout-button>button:hover {
            box-shadow: 0 5px 20px rgba(220, 53, 69, 0.4) !important;
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
