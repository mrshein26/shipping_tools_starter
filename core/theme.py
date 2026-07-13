import streamlit as st

def inject_theme():
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"

    if st.session_state.theme == "Dark":
        dark_css = """
        <style>
        /* ၁။ အခြေခံ နောက်ခံနှင့် စာသား */
        .stApp { background-color: #0F172A !important; }
        h1, h2, h3, p, label, span { color: #F8FAFC !important; }
        [data-testid="stHeader"] { background-color: transparent !important; }
        
        /* ၂။ Menu (Segmented Control) ၏ ခေါင်းမာသော အဖြူရောင်နောက်ခံအားလုံးကို ရှင်းလင်းခြင်း */
        div[data-testid="stSegmentedControl"] {
            background-color: #1E293B !important;
            border: 1px solid #475569 !important;
            border-radius: 8px !important;
            padding: 4px !important;
        }
        
        /* ရွေးချယ်မထားသော အစိတ်အပိုင်းအားလုံးကို အတင်းအကျပ် အကြည်ရောင် ပြောင်းပစ်ခြင်း */
        div[data-testid="stSegmentedControl"] *:not([aria-checked="true"]):not([data-selected="true"]) {
            background: transparent !important;
            background-color: transparent !important;
        }
        
        /* စာသားအားလုံးကို ပုံမှန်အချိန်တွင် မီးခိုးဖျော့ရောင် ထားရှိခြင်း */
        div[data-testid="stSegmentedControl"] p,
        div[data-testid="stSegmentedControl"] span {
            color: #94A3B8 !important;
        }
        
        /* ရွေးချယ်ထားသော (Active) ဘက်ကိုသာ သီးသန့် အပြာ/မီးခိုးရင့်ရောင် နောက်ခံပေးခြင်း */
        div[data-testid="stSegmentedControl"] [aria-checked="true"],
        div[data-testid="stSegmentedControl"] [data-selected="true"] {
            background-color: #334155 !important;
            background: #334155 !important;
            border-radius: 6px !important;
        }
        
        /* ရွေးချယ်ထားသော ဘက်မှ စာသားကို အဖြူရောင် ထင်ထင်ရှားရှား ပြသခြင်း */
        div[data-testid="stSegmentedControl"] [aria-checked="true"] p,
        div[data-testid="stSegmentedControl"] [aria-checked="true"] span,
        div[data-testid="stSegmentedControl"] [data-selected="true"] p,
        div[data-testid="stSegmentedControl"] [data-selected="true"] span {
            color: #FFFFFF !important;
            font-weight: bold !important;
        }

        /* ၃။ Upload Button တွင် အဖြူရောင် ဝင်နေမှုကို ဖြေရှင်းခြင်း */
        [data-testid="stFileUploaderDropzone"] {
            background-color: #1E293B !important;
            border: 2px dashed #475569 !important;
        }
        [data-testid="stFileUploaderDropzone"] button,
        [data-testid="stFileUploaderDropzone"] button:hover {
            background-color: #334155 !important;
            color: #FFFFFF !important;
            border: 1px solid #475569 !important;
        }
        
        /* ၄။ ပုံမှန် Button များ */
        .stButton > button {
            background-color: #1E293B !important;
            color: #FFFFFF !important;
            border: 1px solid #475569 !important;
        }
        .stButton > button:hover {
            background-color: #334155 !important;
            color: #FFFFFF !important;
        }

        /* ၅။ Dropdown / Selectbox */
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] > div:hover,
        div[data-baseweb="select"] > div:focus {
            background-color: #1E293B !important;
            color: #FFFFFF !important;
            border: 1px solid #475569 !important;
        }
        </style>
        """
        st.markdown(dark_css, unsafe_allow_html=True)
    else:
        light_css = """
        <style>
        .stApp { background-color: #FFFFFF !important; }
        h1, h2, h3, p, label, span { color: #0F172A !important; }
        [data-testid="stHeader"] { background-color: transparent !important; }
        </style>
        """
        st.markdown(light_css, unsafe_allow_html=True)