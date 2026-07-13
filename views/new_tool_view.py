import streamlit as st
from core.utils import add_log, extract_files

def render_new_tool_ui():
    st.subheader("🚀 My New Tool")
    st.write("Welcome to the new modular tool interface!")
    
    uploaded_files = st.file_uploader("Upload PDFs or ZIP", type=["pdf", "zip"], accept_multiple_files=True)
    
    if st.button("Process Files"):
        if uploaded_files:
            files = extract_files(uploaded_files)
            st.success(f"Successfully extracted {len(files)} files!")
            add_log(st.session_state.current_user, f"Processed {len(files)} files in New Tool")
        else:
            st.error("Please upload files first.")