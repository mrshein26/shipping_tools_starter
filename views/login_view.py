import streamlit as st
from core.auth import check_credentials
from core.utils import add_log

def login_screen():
    """Login Screen မျက်နှာပြင်ပြသရုံသက်သက် View မော်ဂျူး"""
    st.markdown("""
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            overflow: hidden !important;
            height: 100vh !important;
            background-color: #f0f2f6 !important;
        }
        [data-testid="stMainBlockContainer"] {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            height: 100vh !important;
            padding: 0 !important;
        }
        [data-testid="stVerticalBlock"] {
            gap: 0px !important;
            width: 100% !important;
        }
        [data-testid="column"]:nth-of-type(2), [data-testid="stColumn"]:nth-of-type(2) {
            background-color: #ffffff !important; 
            padding: 2.5rem 2rem !important;
            border-radius: 16px !important; 
            box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.08) !important; 
            border: 1px solid #e2e8f0 !important;
            max-width: 420px !important;
            margin: 0 auto !important;
        }
        .stButton>button {
            background-color: #a6192e !important; border: none !important;
            border-radius: 6px !important; padding: 0.6rem !important; margin-top: 10px !important;
            width: 100% !important;
        }
        .stButton>button p {
            color: #ffffff !important; font-size: 16px !important;
            font-weight: bold !important;
        }
        .stButton>button:hover {
            background-color: #8a1526 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    _, col_login, _ = st.columns([1, 1.5, 1])

    with col_login:
        st.markdown("<h3 style='text-align: center; color: #a6192e;'>Shipping Portal</h3>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; color: #475569; margin-bottom: 25px; font-size: 18px;'><b>Member</b> Login</div>", unsafe_allow_html=True)
        
        with st.form(key='login_form'):
            u_name = st.text_input("Username")
            u_pass = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Sign In")

            if submit_button:
                # core/auth.py မှ Function ကို လှမ်းခေါ်စစ်ဆေးခြင်း
                if check_credentials(u_name, u_pass):
                    st.session_state.logged_in = True
                    st.session_state.current_user = u_name
                    add_log(u_name, "Logged In")    
                    st.rerun()
                else: 
                    st.error("❌ Invalid Username or Password")