import streamlit as st
from core.theme import inject_theme
from views.login_view import login_screen
from views.pdf_stamper_view import render_pdf_stamper_ui  
from views.pdf_compressor_view import render_pdf_compressor_ui 
from views.document_combiner_view import render_document_combiner_ui
from views.extract_forms_view import render_extract_forms_ui
from views.history_view import render_history_ui  
from core.utils import add_log

# ၁။ Page Config
st.set_page_config(page_title="Shipping Tools - V2", layout="wide")

# ၂။ Login Session State
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False
if "current_user" not in st.session_state: 
    st.session_state.current_user = None

# ၃။ 🔐 Login စစ်ဆေးခြင်း
if not st.session_state.logged_in:
    login_screen() 
    st.stop()

# ၄။ Theme စနစ်
inject_theme()

# 💡 နေရာလွတ် (Gap) များနှင့် Primary Button များကို ရေပြာရင့်ရောင်သို့ ပြောင်းလဲမည့် CSS
st.markdown("""
<style>
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 1rem !important;
}
hr {
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}
h1, h2, h3, h4 {
    padding-bottom: 0.2rem !important;
    margin-bottom: 0.2rem !important;
}
div[data-testid="stRadio"] {
    margin-bottom: -1rem !important;
}
div[data-testid="stMarkdownContainer"] > p {
    margin-bottom: 0.5rem !important;
}

/* 🎨 အဓိက ခလုတ်များ (Primary Buttons) အားလုံးကို ရေပြာရင့်ရောင် ပြောင်းခြင်း */
button[kind="primary"] {
    background-color: #1E40AF !important; 
    border: none !important;
}

/* 💡 ခလုတ်အတွင်းရှိ စာသားများကို အဖြူရောင်နှင့် အထူ (Bold) ပြောင်းပေးခြင်း */
button[kind="primary"] p {
    color: #ffffff !important;
    font-weight: bold !important;
    font-size: 16px !important;
}

button[kind="primary"]:hover {
    background-color: #1e3a8a !important;
}
</style>
""", unsafe_allow_html=True)

# ၅။ Header Layout
top_col1, top_col2 = st.columns([7, 3])
with top_col1:
    # 💡 ခေါင်းစဉ် (Header) ကို ရေပြာရင့်ရောင် ပြောင်းထားပါသည်
    st.markdown("<h1 style='color: #1E40AF; padding-bottom: 0; margin-bottom: 0;'>Shipping Tools - V2</h1>", unsafe_allow_html=True)
    st.caption(f"Active User: {st.session_state.current_user} | 🔐 Secure Access")

with top_col2:
    theme_col, logout_col = st.columns(2)
    with theme_col:
        current_theme = st.selectbox(
            "Theme", ["Light", "Dark"], 
            index=0 if st.session_state.theme == "Light" else 1,
            label_visibility="collapsed"
        )
        if current_theme != st.session_state.theme:
            st.session_state.theme = current_theme
            st.rerun()
    with logout_col:
        if st.button("⏻ Log Out", use_container_width=True):
            add_log(st.session_state.current_user, "Logged Out")
            st.session_state.logged_in = False
            st.rerun()

st.markdown("---")

# ၆။ 🛡️ Menu Bar စနစ်
available_tools = ["PDF Stamper", "PDF Compressor", "Extract Forms", "Document Combiner"]

if st.session_state.current_user == "admin":
    available_tools.append("Admin Tools") 

st.write("### 🧰 Select Tool")
tool = st.radio("Select Tool Menu", available_tools, horizontal=True, label_visibility="collapsed")

st.markdown("---")

# ၇။ 🔄 Tool Routers 
if tool == "PDF Stamper":
    render_pdf_stamper_ui()
elif tool == "PDF Compressor":
    render_pdf_compressor_ui()
elif tool == "Extract Forms":
    render_extract_forms_ui()
elif tool == "Document Combiner":
    render_document_combiner_ui()
elif tool == "Admin Tools":
    render_history_ui()