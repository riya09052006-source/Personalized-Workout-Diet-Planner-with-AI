import streamlit as st
import os
from database.db import init_db

# Initialize database tables on app start
init_db()

# Setup Streamlit page configuration
st.set_page_config(
    page_title="AI FitPlanner",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global dark mode premium CSS styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif;
        background-color: #070913 !important;
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0B0F19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    .sidebar-user {
        padding: 15px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 20px;
        text-align: center;
    }
    
    h1, h2 {
        background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 25px !important;
    }
    
    div[data-testid="stTextInput"] input {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    button[kind="secondaryFormSubmit"], button[kind="primary"] {
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%) !important;
        color: #070913 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
    }
    
    div[data-testid="stTabBar"] button {
        color: #94A3B8 !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="stTabBar"] button[aria-selected="true"] {
        color: #00F2FE !important;
        border-bottom-color: #00F2FE !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session states
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# Define pages structure
login_page = st.Page("pages/login.py", title="Sign In", icon="🔒")
dashboard_page = st.Page("pages/dashboard.py", title="Dashboard", icon="📊")
profile_page = st.Page("pages/profile.py", title="Profile Setup", icon="👤")
workout_page = st.Page("pages/workout.py", title="Workout Plan", icon="💪")
diet_page = st.Page("pages/diet.py", title="Diet Plan", icon="🥗")

# Setup routing navigation depending on authentication state
if st.session_state.user_id is None:
    pg = st.navigation([login_page], position="hidden")
else:
    pg = st.navigation({
        "Dashboard": [dashboard_page],
        "My Recommendations": [workout_page, diet_page],
        "Profile settings": [profile_page]
    })
    
    st.sidebar.markdown(f"""
        <div class="sidebar-user">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Logged in as</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #00F2FE;">{st.session_state.user_name}</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.user_name = ""
        st.success("Logged out successfully.")
        st.rerun()

pg.run()