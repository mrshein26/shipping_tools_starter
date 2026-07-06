import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build


def get_drive_service():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(creds_info)
        return build("drive", "v3", credentials=creds)
    except Exception:
        return None


def search_files_by_name_contains(service, folder_id: str, text: str) -> list[dict]:
    query = f"name contains '{text}' and '{folder_id}' in parents and trashed=false"
    result = (
        service.files()
        .list(
            q=query,
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        .execute()
    )
    return result.get("files", [])
