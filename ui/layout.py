import streamlit as st

from config import APP_TITLE, IMAGES_DIR


def apply_page_config() -> None:
    icon_path = IMAGES_DIR / "TH Logo.png"
    page_icon = str(icon_path) if icon_path.exists() else "📄"

    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=page_icon,
        layout="wide",
    )

    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        header, footer, #MainMenu { visibility: hidden; }
        div[data-testid="stFileUploaderDropzone"] {
            border: 1px solid #D8E1EA;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, current_user: str, on_logout) -> None:
    left, right = st.columns([8, 2])
    with left:
        st.title(title)
        st.caption(f"Active user: {current_user}")
    with right:
        st.write("")
        if st.button("Log Out", use_container_width=True):
            on_logout()
