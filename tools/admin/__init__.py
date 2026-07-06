import streamlit as st


def render_admin_tools(current_user: str) -> None:
    st.subheader("Admin Tools")

    tabs = st.tabs(
        [
            "Air Booking",
            "Remove & Combine",
            "Export Data",
            "Import Data (RO)",
            "REX Data",
            "Extract INV No",
            "License Balance",
            "Import Lists",
            "Export Summary",
        ]
    )

    for tab, title in zip(
        tabs,
        [
            "Air Booking",
            "Remove & Combine",
            "Export Data",
            "Import Data (RO)",
            "REX Data",
            "Extract INV No",
            "License Balance",
            "Import Lists",
            "Export Summary",
        ],
    ):
        with tab:
            st.info(f"{title} module frame is ready. Add old logic here after the core tools are stable.")
