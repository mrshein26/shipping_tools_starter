import streamlit as st


def render_forms_home(current_user: str) -> None:
    st.subheader("Extract Forms")
    selected_form = st.radio(
        "Select Form Type",
        [
            "Declaration of NWPM (CN)",
            "Statement of Origin (CA,DR)",
            "DMAM (JP)",
            "Org Criterion (IN)",
            "Cover Sheet",
            "Certificate of Origin (CL)",
        ],
        horizontal=True,
    )

    st.info(f"{selected_form} frame is ready. Move the matching extraction and template-fill logic into tools/forms/ one file at a time.")

    if selected_form in {"Org Criterion (IN)", "Cover Sheet"}:
        st.file_uploader("Upload Excel or CSV", type=["xlsx", "xls", "csv"])
    else:
        st.file_uploader("Upload invoice PDFs or ZIP", type=["pdf", "zip"], accept_multiple_files=True)

    st.button("Generate Forms", use_container_width=True, disabled=True)
