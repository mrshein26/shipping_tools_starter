# main.py

import streamlit as st
from PIL import Image
from core.theme import inject_theme
from core.styles import get_custom_css  # 👈 CSS module အသစ်ကို လှမ်းခေါ်ခြင်း
from views.login_view import login_screen
from views.pdf_stamper_view import render_pdf_stamper_ui  
from views.pdf_compressor_view import render_pdf_compressor_ui 
from views.document_combiner_view import render_document_combiner_ui
from views.extract_forms_view import render_extract_forms_ui
from views.history_view import render_history_ui  
from core.utils import add_log
from views.booking_forms_view import render_booking_forms_ui
from views.document_checker_view import render_document_checker_ui

# ၁။ Page Config
# 💡 ဤနေရာတွင် ဖိုင်နာမည်ကို "TH Logo.png" ဟု အတိအကျ ပြင်ဆင်ထားပါသည်
logo_img = Image.open("assets/images/TH Logo.png") 
st.set_page_config(page_title="Shipping Tools - V2", page_icon=logo_img, layout="wide")

# ၂။ Login Session State
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False
if "current_user" not in st.session_state: 
    st.session_state.current_user = None

# 💡 Theme ကို App ဖွင့်ဖွင့်ချင်း Light အဖြစ် ပုံသေသတ်မှတ်ခြင်း (Error မတက်စေရန်)
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# ၃။ 🔐 Login စစ်ဆေးခြင်း
if not st.session_state.logged_in:
    login_screen() 
    st.stop()

# ၄။ Theme စနစ်
inject_theme()

# ==========================================
# 🖋️ Option 3: Elegant Minimalist (Slate) + 🔠 Inter Font
# ==========================================
is_dark_mode = st.session_state.get("theme", "Light") == "Dark"

# 💡 Dynamic CSS ကို Styles module မှ လှမ်းခေါ်ပြီး အသုံးပြုခြင်း
custom_css = get_custom_css(is_dark_mode)
st.markdown(custom_css, unsafe_allow_html=True)

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
        if st.button("⏻ Log Out", width="stretch"):
            add_log(st.session_state.current_user, "Logged Out")
            st.session_state.logged_in = False
            st.rerun()

st.markdown("---")

# ၆။ 🛡️ Menu Bar စနစ်
available_tools = ["PDF Stamper", "PDF Compressor", "Extract Forms", "Document Combiner", "Document Checker", "Booking Forms"]

if st.session_state.current_user == "admin":
    available_tools.append("Admin Tools") 

st.write("### 🧰 Select Tool")
# Radio အစား pills ကို သုံးပါမည်
tool = st.segmented_control("Select Tool Menu", available_tools, label_visibility="collapsed")

# Pills က နှိပ်ပြီးသားကို ထပ်နှိပ်ရင် Unselect ဖြစ်သွားတတ်လို့ Default ပြန်ထားပေးဖို့ လိုပါတယ်
if not tool:
    tool = available_tools[0]

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
elif tool == "Document Checker":
    render_document_checker_ui()    
elif tool == "Booking Forms":
    render_booking_forms_ui()    
elif tool == "Admin Tools":
    render_history_ui()
