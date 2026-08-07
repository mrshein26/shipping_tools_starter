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

if is_dark_mode:
    # 🌙 Dark Mode အတွက် 
    btn_prim_bg = "#F8FAFC" 
    btn_prim_hover = "#E2E8F0"
    btn_prim_text = "#0F172A" 
    
    btn_sec_bg = "#0F172A"    
    btn_sec_border = "#334155"
    btn_sec_text = "#CBD5E1"
    btn_sec_hover = "#1E293B"

    # 🌟 ဒီအောက်က Radio Box (Dark Mode) အရောင်များ ကျန်ခဲ့တာပါ 🌟
    box_unselected_bg = "#1E293B"      
    box_unselected_border = "#334155"  
    box_unselected_text = "#E2E8F0"    
    box_hover_bg = "#334155"           
    box_selected_bg = "#3B82F6"        
    box_selected_text = "#FFFFFF"      
else:
    # ☀️ Light Mode အတွက် 
    btn_prim_bg = "#334155"    
    btn_prim_hover = "#475569" 
    btn_prim_text = "#FFFFFF" 
    
    btn_sec_bg = "#FFFFFF"
    btn_sec_border = "#E2E8F0"
    btn_sec_text = "#475569"
    btn_sec_hover = "#F8FAFC"

    # 🌟 ဒီအောက်က Radio Box (Light Mode) အရောင်များ ကျန်ခဲ့တာပါ 🌟
    box_unselected_bg = "#FFFFFF"
    box_unselected_border = "#E2E8F0"
    box_unselected_text = "#475569"
    box_hover_bg = "#F8FAFC"
    box_selected_bg = "#334155"
    box_selected_text = "#FFFFFF"

# 💡 Dynamic CSS (Font, ခလုတ်ဒီဇိုင်းများ နှင့် Input Boxes များ)
custom_css = f"""
<style>
/* 🔠 Google Fonts မှ Inter ကို လှမ်းခေါ်ခြင်း */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

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
    font-weight: 600 !important; 
}}
div[data-testid="stRadio"] {{
    margin-bottom: -1rem !important;
}}

/* 🌟 ဒီနေရာက မူလကုဒ်မှာ စာသားကို အပေါ်တွန်းတင်နေတဲ့ တရားခံပါ (0.5rem မှ 0 သို့ ပြင်ထားသည်) */
div[data-testid="stMarkdownContainer"] > p {{
    margin-bottom: 0 !important;
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

/* 🔥 Primary Buttons */
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

/* ⚪ Secondary Buttons */
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

/* ========================================================
   🎯 Radio Buttons (Perfect Center & Pill Shape)
   ======================================================== */
/* 🌟 အပေါ်က "Select..." အကွက်အရှည်ကြီးများကို အပြီးတိုင်ဖျောက်ရန် (Updated) */
div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {{
    display: none !important; 
}}

div[data-testid="stRadio"] > div {{
    gap: 12px !important;
    flex-wrap: wrap !important;
}}

div[data-testid="stRadio"] label {{
    background-color: {box_unselected_bg} !important;
    border: 1px solid {box_unselected_border} !important;
    border-radius: 50px !important; 
    padding: 10px 24px !important; 
    cursor: pointer !important;
    transition: all 0.2s ease-in-out !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important; 
    min-height: 44px !important; /* 🌟 Box အရွယ်အစားကို အတိအကျ ထိန်းထားခြင်း */
}}

div[data-testid="stRadio"] label div[data-baseweb="radio"] {{
    display: none !important; 
    width: 0 !important;
    margin: 0 !important;
}}
div[data-testid="stRadio"] label span[data-baseweb="radio"] {{
    display: none !important; 
}}

div[data-testid="stRadio"] label > div {{
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important; 
    height: 100% !important; 
    color: {box_unselected_text} !important; 
}}

/* 🌟 စာသားကို အပေါ်အောက် အလယ်တည့်တည့်ကျစေရန် သေချာချုပ်ထားခြင်း */
div[data-testid="stRadio"] label p {{
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important; 
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

div[data-testid="stRadio"] label[data-checked="true"] {{
    background-color: {box_selected_bg} !important;
    border-color: {box_selected_bg} !important;
}}
div[data-testid="stRadio"] label[data-checked="true"] > div {{
    color: {box_selected_text} !important;
    font-weight: 600 !important;
}}

div[data-testid="stRadio"] label:hover {{
    background-color: {box_hover_bg} !important;
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
tool = st.pills("Select Tool Menu", available_tools, label_visibility="collapsed")

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
