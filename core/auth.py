import streamlit as st

# ဝန်ထမ်းစာရင်း (Database)
# st.secrets မဆောက်ရသေးပါက Error မတက်စေရန် Default Password များ ထည့်ပေးထားပါသည်
USER_DB = {
    "admin": {"password": st.secrets.get("passwords", {}).get("admin", "admin2026@"), "status": "active"},
    "sheinmon": {"password": st.secrets.get("passwords", {}).get("sheinmon", "pass123"), "status": "active"},
    "sulae": {"password": st.secrets.get("passwords", {}).get("sulae", "Sl12365"), "status": "active"},
    "thaesumon": {"password": st.secrets.get("passwords", {}).get("thaesumon", "Tsm7890"), "status": "active"},
    "thetaunghtay": {"password": st.secrets.get("passwords", {}).get("thetaunghtay", "Tah1111"), "status": "active"},
    "zayarphyohtut": {"password": st.secrets.get("passwords", {}).get("zayarphyohtut", "Zyph1122"), "status": "active"}
}

def check_credentials(username, password):
    """Username နှင့် Password မှန်ကန်မှု ရှိမရှိ စစ်ဆေးပေးသော Function"""
    if username in USER_DB and USER_DB[username]["password"] == password:
        return True
    return False
