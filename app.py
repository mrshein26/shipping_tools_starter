import streamlit as st
from PIL import Image
from core.theme import inject_theme
from views.login_view import login_screen
from views.pdf_stamper_view import render_pdf_stamper_ui  
from views.pdf_compressor_view import render_pdf_compressor_ui 
from views.document_combiner_view import render_document_combiner_ui
from views.extract_forms_view import render_extract_forms_ui
from views.history_view import render_history_ui  
from core.utils import add_log

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

if is_dark_mode:
    # 🌙 Dark Mode အတွက် 
    btn_prim_bg = "#F8FAFC" 
    btn_prim_hover = "#E2E8F0"
    btn_prim_text = "#0F172A" 
    
    btn_sec_bg = "#0F172A"    
    btn_sec_border = "#334155"
    btn_sec_text = "#CBD5E1"
    btn_sec_hover = "#1E293B"
else:
    # ☀️ Light Mode အတွက် (အရမ်းမရင့်တော့ဘဲ မျက်စိအေးသော ခဲပြာရောင် သို့ ပြောင်းထားပါသည်)
    btn_prim_bg = "#334155"    # ပိုလင်းသော ခဲပြာရောင် (Slate 700)
    btn_prim_hover = "#475569" # Mouse တင်လျှင် ပိုလင်းသွားမည်
    btn_prim_text = "#FFFFFF" 
    
    btn_sec_bg = "#FFFFFF"
    btn_sec_border = "#E2E8F0"
    btn_sec_text = "#475569"
    btn_sec_hover = "#F8FAFC"

# 💡 Dynamic CSS (Font, ခလုတ်ဒီဇိုင်းများ နှင့် Input Boxes များ)
custom_css = f"""
<style>
/* 🚫 Streamlit Menu, Footer နှင့် အောက်ခြေ ညာဘက်ရှိ Cloud Badge များကို ဖျောက်ရန် */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
.viewerBadge_container {{display: none !important;}}
.viewerBadge_link {{display: none !important;}}
[data-testid="stDecoration"] {{display: none !important;}}

/* 🔠 App တစ်ခုလုံးရှိ စာသားများကို Inter Font သို့ ပြောင်းခြင်း */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
}}

.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 1rem !important;
}}
hr {{
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}}
h1, h2, h3, h4 {{
    padding-bottom: 0.2rem !important;
    margin-bottom: 0.2rem !important;
    font-weight: 600 !important; /* ခေါင်းစဉ်များကို ပိုမိုသပ်ရပ်စေရန် */
}}
div[data-testid="stRadio"] {{
    margin-bottom: -1rem !important;
}}
div[data-testid="stMarkdownContainer"] > p {{
    margin-bottom: 0.5rem !important;
}}

/* ========================================================
   🔲 စာရိုက်သွင်းရသော အကွက်များ (Input Boxes - Login အပါအဝင်)
   ======================================================== */
div[data-baseweb="input"] > div {{
    background-color: #F8FAFC !important; 
    border: 1px solid #E2E8F0 !important; 
    border-radius: 6px !important;
    transition: all 0.2s ease-in-out !important;
}}
div[data-baseweb="input"] > div:focus-within {{
    border-color: #0F172A !important;
    box-shadow: 0 0 0 1px #0F172A !important;
}}
div[data-baseweb="input"] input {{
    color: #0F172A !important; 
    font-weight: 500 !important;
}}
div[data-baseweb="input"] input::placeholder {{
    color: #94A3B8 !important; 
}}

/* ========================================================
   🔘 ခလုတ်များ (Buttons) ၏ ယေဘုယျပုံစံ
   ======================================================== */
div.stButton > button {{
    display: inline-flex !important;
    align-items: center !important;       
    justify-content: center !important;   
    padding: 0.5rem 1rem !important;
    min-height: 42px !important;
    border-radius: 6px !important; 
    transition: all 0.2s ease-in-out !important;
    font-family: 'Inter', sans-serif !important; 
}}

/* 🔥 Primary Buttons (Process, Extract, Sign In, etc.) */
div.stButton > button[kind="primary"] {{
    background-color: {btn_prim_bg} !important;
    border: 1px solid {btn_prim_bg} !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}}
div.stButton > button[kind="primary"] p {{
    color: {btn_prim_text} !important;
    font-weight: 500 !important; 
    margin: 0 !important;        
}}
div.stButton > button[kind="primary"]:hover {{
    background-color: {btn_prim_hover} !important; 
    border-color: {btn_prim_hover} !important;
}}

/* ⚪ Secondary Buttons (Clear Files, etc.) */
div.stButton > button[kind="secondary"] {{
    background-color: {btn_sec_bg} !important;
    border: 1px solid {btn_sec_border} !important;
}}
div.stButton > button[kind="secondary"] p {{
    color: {btn_sec_text} !important;
    font-weight: 500 !important; 
    margin: 0 !important;        
}}
div.stButton > button[kind="secondary"]:hover {{
    background-color: {btn_sec_hover} !important; 
}}
</style>
"""
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
