import hmac

import streamlit as st


DEFAULT_USERS = {
    "admin": {"password": "admin123", "status": "active"},
    "sheinmon": {"password": "changeme", "status": "active"},
}


def get_user_db() -> dict:
    try:
        users = st.secrets.get("passwords", {})
    except Exception:
        users = {}

    if not users:
        return DEFAULT_USERS

    return {
        username: {"password": str(password), "status": "active"}
        for username, password in users.items()
    }


def require_login() -> bool:
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    return bool(st.session_state.logged_in)


def render_login(user_db: dict) -> None:
    st.markdown(
        """
        <style>
        .block-container { max-width: 480px; padding-top: 14vh; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Member Login")
    st.caption("Teng Hui Shipping Tools")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)

    if not submitted:
        return

    user = user_db.get(username)
    password_ok = user and hmac.compare_digest(user["password"], password)
    active_ok = user and user.get("status") == "active"

    if password_ok and active_ok:
        st.session_state.logged_in = True
        st.session_state.current_user = username
        st.rerun()

    st.error("Invalid username or password.")


def logout() -> None:
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()
