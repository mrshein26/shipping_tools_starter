import streamlit as st

from auth import get_user_db, require_login, render_login, logout
from config import APP_TITLE, TOOL_ACCESS
from services.logger import add_log, render_admin_log
from tools.pdf_stamper import render_pdf_stamper
from tools.document_combiner import render_document_combiner
from tools.forms import render_forms_home
from tools.air_docs_merge import render_air_docs_merge
from tools.admin import render_admin_tools
from ui.layout import apply_page_config, render_header


def available_tools(username: str) -> list[str]:
    tools = []
    for tool_name, allowed_roles in TOOL_ACCESS.items():
        if "all" in allowed_roles or username in allowed_roles:
            tools.append(tool_name)
    return tools


def main() -> None:
    apply_page_config()
    user_db = get_user_db()

    if not require_login():
        render_login(user_db)
        return

    current_user = st.session_state.current_user
    render_header(APP_TITLE, current_user, on_logout=logout)

    if current_user == "admin":
        render_admin_log()

    tool = st.segmented_control(
        "Select Tool",
        available_tools(current_user),
        default="PDF Stamper",
        label_visibility="collapsed",
    )

    st.divider()

    if tool == "PDF Stamper":
        render_pdf_stamper(current_user)
    elif tool == "Document Combiner":
        render_document_combiner(current_user)
    elif tool == "Extract Forms":
        render_forms_home(current_user)
    elif tool == "Air Docs Merge":
        render_air_docs_merge(current_user)
    elif tool == "Admin Tools":
        render_admin_tools(current_user)

    add_log(current_user, f"Opened tool: {tool}", once_key=f"opened_{tool}_{current_user}")


if __name__ == "__main__":
    main()
