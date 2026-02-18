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
        
        /* Main Navigation Bar */
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 3rem;
            background: linear-gradient(135deg, #0d47a1 0%, #00796b 100%);
        }
        
        .navbar-left {
            display: flex;
            gap: 2rem;
        }
        
        .nav-link {
            color: white;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            transition: color 0.3s ease;
            cursor: pointer;
        }
        
        .nav-link:hover {
            color: #20B2AA;
        }
        
        .navbar-right {
            display: flex;
            align-items: center;
        }
        
        .nav-button {
            background: linear-gradient(135deg, #20B2AA 0%, #1a9a8f 100%);
            color: white;
            border: none;
            padding: 0.7rem 1.5rem;
            border-radius: 25px;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(32, 178, 170, 0.3);
        }
        
        .nav-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(32, 178, 170, 0.4);
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

        .navbar {
            margin-bottom: 0.9rem; /* space between navbar and content */
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
        
        .button-group {
            display: flex;
            gap: 1.5rem;
            margin-bottom: 3rem;
        }
        
        .btn-primary {
            background: #20B2AA;
            color: white;
            border: none;
            padding: 0.85rem 2rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover {
            background: #1a9a8f;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(32, 178, 170, 0.4);
        }
        
        .btn-secondary {
            background: transparent;
            color: white;
            border: 2px solid white;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
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
        
        /* Form Styling */
        div[data-testid="stForm"] {
            background: white;
            padding: 1.25rem;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }
        
        .welcome-container {
            background: white;
            padding: 3rem 2rem;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            text-align: center;
            margin-top: 2rem;
            color: #333;
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
        
        .stButton>button:hover {
            background: #1a9a8f !important;
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(32, 178, 170, 0.4) !important;
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
