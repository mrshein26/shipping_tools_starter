import requests
import streamlit as st


def send_discord_alert(user: str, action: str, timestamp: str) -> None:
    webhook_url = st.secrets.get("DISCORD_WEBHOOK_URL", "")
    if not webhook_url:
        return

    payload = {
        "content": (
            "**Teng Hui Shipping**\n"
            f"Time: `{timestamp}`\n"
            f"User: `{user}`\n"
            f"Action: `{action}`"
        )
    }
    requests.post(webhook_url, json=payload, timeout=5)
