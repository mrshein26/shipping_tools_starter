import csv
from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from config import ACTIVITY_LOG, LOG_DIR


def add_log(user: str, action: str, once_key: str | None = None) -> None:
    if once_key and st.session_state.get(once_key):
        return
    if once_key:
        st.session_state[once_key] = True

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    mm_timezone = timezone(timedelta(hours=6, minutes=30))
    now = datetime.now(mm_timezone).strftime("%Y-%m-%d %H:%M:%S")
    file_exists = ACTIVITY_LOG.exists()

    with ACTIVITY_LOG.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "User", "Action"])
        writer.writerow([now, user, action])


def render_admin_log() -> None:
    with st.expander("Admin Monitor"):
        if not ACTIVITY_LOG.exists():
            st.caption("No activity recorded yet.")
            return

        logs = pd.read_csv(ACTIVITY_LOG)
        st.dataframe(logs.iloc[::-1], use_container_width=True, hide_index=True)
