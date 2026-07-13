import os
import csv
import requests
import io
import zipfile
from datetime import datetime, timedelta, timezone
import streamlit as st

def send_discord_alert(user, msg, timestamp):
    """Discord သို့ Real-time Alert ပို့ရန်"""
    try:
        # secrets.toml မှ လုံခြုံစွာ လှမ်းခေါ်ခြင်း
        webhook_url = st.secrets["discord_webhook"]
        alert_message = (
            f"🔔 **Teng Hui Shipping**\n"
            f"⏰ **Time:** `{timestamp}`\n"
            f"👤 **User:** `{str(user).upper()}`\n"
            f"✍️ **Action:** `{msg}`\n"
            f"───────────────────"
        )
        requests.post(webhook_url, json={"content": alert_message}, timeout=5)
    except Exception as e:
        print(f"Discord Alert Error: {e}")

def add_log(user, action):
    """CSV သို့ မှတ်တမ်းတင်ပြီး Discord သို့ပါ တစ်ပြိုင်နက် ပို့မည်"""
    mm_timezone = timezone(timedelta(hours=6, minutes=30))
    now = datetime.now(mm_timezone).strftime("%Y-%m-%d %H:%M:%S")
    
    file_exists = os.path.isfile("activity_logs.csv")
    try:
        with open("activity_logs.csv", mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists: writer.writerow(["Timestamp", "User", "Action"])
            writer.writerow([now, user, action])
    except Exception as e:
        print(f"Log Error: {e}")
        
    send_discord_alert(user, action, now)

def extract_files(raw_files):
    """ZIP ဖိုင်များကို ဖြည်ထုတ်၍ PDF များကို စုစည်းပေးမည့် Shared Helper Function"""
    if not raw_files:
        return []
        
    extracted_files = []
    for rf in raw_files:
        # ZIP ဖိုင်ဖြစ်လျှင်
        if rf.name.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(rf, "r") as z:
                    for item in z.infolist():
                        if item.filename.lower().endswith(".pdf") and not item.filename.startswith("__MACOSX"):
                            pdf_bytes = io.BytesIO(z.read(item.filename))
                            pdf_bytes.name = os.path.basename(item.filename)
                            extracted_files.append(pdf_bytes)
            except Exception as e:
                st.error(f"Error reading ZIP ({rf.name}): {e}")
        # သာမန် PDF ဖိုင်ဖြစ်လျှင်
        elif rf.name.lower().endswith(".pdf"):
            extracted_files.append(rf)
            
    return extracted_files