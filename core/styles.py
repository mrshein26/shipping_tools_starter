# core/styles.py

def get_custom_css(is_dark_mode):
    if is_dark_mode:
        # 🌙 Dark Mode အတွက် 
        btn_prim_bg = "#F8FAFC" 
        btn_prim_hover = "#E2E8F0"
        btn_prim_text = "#0F172A" 
        
        btn_sec_bg = "#0F172A"    
        btn_sec_border = "#334155"
        btn_sec_text = "#CBD5E1"
        btn_sec_hover = "#1E293B"

        # Radio & Pills (Dark Mode) အရောင်များ
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

        # Radio & Pills (Light Mode) အရောင်များ
        box_unselected_bg = "#FFFFFF"
        box_unselected_border = "#E2E8F0"
        box_unselected_text = "#475569"
        box_hover_bg = "#F8FAFC"
        box_selected_bg = "#334155"
        box_selected_text = "#FFFFFF"

    return f"""
<style>
/* 🌟 အပေါ်က "Select..." ခေါင်းစဉ်များကို App တစ်ခုလုံးတွင် အပြီးတိုင်ဖျောက်ရန် */
div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {{
    display: none !important; 
}}

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

/* 🌟 Box အတွင်းရှိ စာသားများကို အပေါ်အောက် အလယ်တည့်တည့်ဖြစ်စေရန် ထပ်မံချိန်ညှိခြင်း */
div[data-testid="stMarkdownContainer"] > p {{
    margin-top: 0 !important; 
    margin-bottom: 0 !important;
    padding-top: 2px !important;
    padding-bottom: 4px !important;
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

/* ========================================================
   🔘 Radio Buttons (ဘောင်မပါသော အဝိုင်းဒီဇိုင်း)
   ======================================================== */
div[data-testid="stRadio"] label {{
    background-color: transparent !important; 
    border: none !important; 
    padding: 8px 16px 8px 0px !important; 
    cursor: pointer !important;
    transition: all 0.2s ease-in-out !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important; 
}}

div[data-testid="stRadio"] label p {{
    margin: 0 !important;
    padding: 0 0 0 1px !important; 
    line-height: 1 !important; 
    display: flex !important;
    align-items: center !important;
    color: {box_unselected_text} !important;
}}

div[data-testid="stRadio"] label:hover {{
    background-color: transparent !important;
    opacity: 0.7 !important;
}}

div[data-testid="stRadio"] label[data-checked="true"] p {{
    color: {box_selected_bg} !important; 
    font-weight: 600 !important;
}}

/* ========================================================
   💊 Pills Menu (st.pills) ၏ ဒီဇိုင်း (Ultimate Selectors)
   ======================================================== */
/* 🌟 Unselected (ပုံမှန်) အခြေအနေ */
div[data-testid="stPills"] button,
button[data-testid="stPill"] {{
    background-color: {box_unselected_bg} !important; 
    border: 1px solid {box_unselected_border} !important;
    border-radius: 20px !important; 
    padding: 6px 16px !important;
    margin-right: 8px !important;
    transition: all 0.2s ease-in-out !important;
}}

/* 🌟 အတွင်းရှိ စာသား (Text) များကို အတင်းအကျပ် အရောင်ပြောင်းရန် */
div[data-testid="stPills"] button *,
button[data-testid="stPill"] * {{
    color: {box_unselected_text} !important;
    font-weight: 400 !important;
    font-family: 'Inter', sans-serif !important;
}}

/* 🌟 Hover ဖြစ်ချိန် */
div[data-testid="stPills"] button:hover,
button[data-testid="stPill"]:hover {{
    background-color: {box_hover_bg} !important;
    border-color: {box_hover_bg} !important;
    opacity: 0.9 !important;
}}

/* Select မလုပ်ထားတဲ့ Pill တွေရဲ့ အဖြူရောင် Background ပေါ်မှာ စာသားမြင်ရအောင် Dark Color ပြောင်းခြင်း */
div[data-testid="stPills"] button p,
div[data-testid="stPills"] button span,
div[data-testid="stSegmented"] button p,
div[data-testid="stSegmented"] button span {{
    color: #0F172A !important; 
    font-weight: 600 !important;
}}

/* Selected (Active) ဖြစ်နေသော Pill အတွက်မူ စာသားကို အဖြူရောင် ပြန်ထားရန် */
div[data-testid="stPills"] button[aria-pressed="true"] p,
div[data-testid="stPills"] button[data-checked="true"] p,
div[data-testid="stSegmented"] button[aria-pressed="true"] p,
div[data-testid="stSegmented"] button[data-checked="true"] p {{
    color: #FFFFFF !important;
}}
</style>
"""
