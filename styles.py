"""
CSS styling for the app.
"""

def load_custom_styles():
    """Load and apply custom CSS styling"""
    styles = """
        <style>
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        div[data-testid="stForm"] {
            background: white;
            padding: 2rem;
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
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 1rem;
        }
        h2 {
            color: #667eea;
            text-align: center;
        }
        .stButton>button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem;
            font-size: 16px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .logout-button>button {
            background: #dc3545 !important;
        }
        .logout-button>button:hover {
            box-shadow: 0 5px 20px rgba(220, 53, 69, 0.4) !important;
        }
        div[data-testid="stFormSubmitButton"] > button {
            margin-top: 1rem;
        }
        </style>
    """
    return styles
