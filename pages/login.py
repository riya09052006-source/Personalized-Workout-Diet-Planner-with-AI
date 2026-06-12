import streamlit as st
from database.db import authenticate_user, register_user

st.markdown("""
    <style>
    .auth-title {
        text-align: center;
        color: #ffffff;
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 5px;
        background: linear-gradient(135deg, #00F2FE, #4FACFE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .auth-subtitle {
        text-align: center;
        color: #94A3B8;
        font-family: 'Outfit', sans-serif;
        font-size: 1rem;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

def show_login_page():
    st.markdown('<div class="auth-title">AI FitPlanner</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-subtitle">Your personalized AI-driven workout and diet assistant</div>', unsafe_allow_html=True)
    
    _, col, _ = st.columns([1, 2, 1])
    
    with col:
        tab_login, tab_signup = st.tabs(["🔒 Access Account", "✨ Create Account"])
        
        with tab_login:
            st.write(" ")
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="name@domain.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit_btn = st.form_submit_button("Log In", use_container_width=True)
                
                if submit_btn:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        user = authenticate_user(email.strip(), password)
                        if user:
                            st.session_state.user_id = user.id
                            st.session_state.user_name = user.name
                            st.success(f"Welcome back, {user.name}!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")
                            
        with tab_signup:
            st.write(" ")
            with st.form("signup_form", clear_on_submit=False):
                new_name = st.text_input("Full Name", placeholder="John Doe")
                new_email = st.text_input("Email Address", placeholder="name@domain.com")
                new_password = st.text_input("Password", type="password", placeholder="At least 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                signup_btn = st.form_submit_button("Register", use_container_width=True)
                
                if signup_btn:
                    if not new_name or not new_email or not new_password:
                        st.error("All fields are required.")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        user = register_user(new_name.strip(), new_email.strip(), new_password)
                        if user:
                            st.success("Account created successfully! Please log in above.")
                        else:
                            st.error("An account with this email already exists.")

if __name__ == "__main__":
    show_login_page()