import streamlit as st


def render_air_docs_merge(current_user: str) -> None:
    st.subheader("Air Docs Merge")
    st.warning("OCR workflow frame is ready. Move the old ASM/INV/LIC/HAWB matching logic here after PDF Stamper and Document Combiner are stable.")

    left, right = st.columns(2)
    with left:
        st.file_uploader("Upload ASM PDFs or ZIP", type=["pdf", "zip"], accept_multiple_files=True)
        st.file_uploader("Upload INV PDFs or ZIP", type=["pdf", "zip"], accept_multiple_files=True)
    with right:
        st.file_uploader("Upload LIC PDFs or ZIP", type=["pdf", "zip"], accept_multiple_files=True)
        st.file_uploader("Upload scanned HAWB PDFs or ZIP", type=["pdf", "zip"], accept_multiple_files=True)

    st.button("Process Air Docs Merge", use_container_width=True, disabled=True)
