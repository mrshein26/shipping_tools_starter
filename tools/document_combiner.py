import re

import pandas as pd
import streamlit as st

from config import GOOGLE_DRIVE_FOLDERS
from services.file_handler import extract_pdf_files
from services.google_drive import get_drive_service, search_files_by_name_contains
from services.logger import add_log


TARGET_CARE_LABEL_SKUS = {"CN", "OB", "RU", "OR", "MX", "LD", "TW", "CO", "EC", "JP", "OJ"}


def render_document_combiner(current_user: str) -> None:
    st.subheader("Document Combiner")
    st.caption("Version 1 frame: upload, check missing files, then merge logic can be expanded step by step.")

    left, right = st.columns(2)
    with left:
        invoice_files = st.file_uploader(
            "Upload INV PDFs or ZIP files",
            type=["pdf", "zip"],
            accept_multiple_files=True,
            key="combiner_invoice_upload",
        )
    with right:
        packing_files = st.file_uploader(
            "Upload PKL PDFs or ZIP files",
            type=["pdf", "zip"],
            accept_multiple_files=True,
            key="combiner_packing_upload",
        )

    excel_files = st.file_uploader(
        "Upload PO list Excel or CSV files",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        key="combiner_po_list_upload",
    )

    check_col, merge_col = st.columns(2)

    if check_col.button("Check Missing SKC and Care Labels", use_container_width=True, type="primary"):
        report = check_missing_drive_files(invoice_files, excel_files)
        st.session_state.combiner_missing_report = report
        add_log(current_user, "Checked missing SKC and Care Labels")

    if merge_col.button("Merge Documents", use_container_width=True):
        st.info("Merge engine placeholder: move the old matching logic into this module after the checker is stable.")

    report = st.session_state.get("combiner_missing_report")
    if report:
        _render_missing_report(report)

    if invoice_files and packing_files:
        inv_count = len(extract_pdf_files(invoice_files))
        pkl_count = len(extract_pdf_files(packing_files))
        st.caption(f"Ready files: {inv_count} invoice(s), {pkl_count} packing list(s).")


def check_missing_drive_files(invoice_files, excel_files) -> dict:
    required_pos = _extract_po_numbers_from_invoice_names(invoice_files)
    care_label_pos = set()

    excel_pos, excel_care_pos = _extract_po_numbers_from_excel_files(excel_files)
    required_pos.update(excel_pos)
    care_label_pos.update(excel_care_pos)

    if not required_pos:
        return {"missing_skc": [], "missing_care_labels": [], "errors": ["No PO numbers found."]}

    service = get_drive_service()
    if service is None:
        return {
            "missing_skc": [],
            "missing_care_labels": [],
            "errors": ["Google Drive credentials are not configured."],
        }

    skc_folder = GOOGLE_DRIVE_FOLDERS["SKC"]
    care_folder = GOOGLE_DRIVE_FOLDERS["Carelabels"]
    if not skc_folder or not care_folder:
        return {
            "missing_skc": [],
            "missing_care_labels": [],
            "errors": ["Google Drive folder IDs are not configured in config.py."],
        }

    missing_skc = []
    missing_care_labels = []

    for po_no in sorted(required_pos):
        if not search_files_by_name_contains(service, skc_folder, po_no):
            missing_skc.append(po_no)
        if po_no in care_label_pos and not search_files_by_name_contains(service, care_folder, po_no):
            missing_care_labels.append(po_no)

    return {"missing_skc": missing_skc, "missing_care_labels": missing_care_labels, "errors": []}


def _extract_po_numbers_from_invoice_names(invoice_files) -> set[str]:
    po_numbers = set()
    for uploaded_file in extract_pdf_files(invoice_files):
        match = re.search(r"\b(\d{6})\b", uploaded_file.name)
        if match:
            po_numbers.add(match.group(1))
    return po_numbers


def _extract_po_numbers_from_excel_files(excel_files) -> tuple[set[str], set[str]]:
    po_numbers = set()
    care_label_pos = set()
    if not excel_files:
        return po_numbers, care_label_pos

    for excel_file in excel_files:
        try:
            if excel_file.name.lower().endswith(".csv"):
                dataframe = pd.read_csv(excel_file, header=None, on_bad_lines="skip")
            else:
                dataframe = pd.read_excel(excel_file, header=None)

            for _, row in dataframe.iterrows():
                row_text = " ".join(str(value) for value in row.values).upper()
                matches = re.findall(r"\b(\d{6})\b", row_text)
                for po_no in matches:
                    po_numbers.add(po_no)
                    if any(sku in row_text.split() for sku in TARGET_CARE_LABEL_SKUS):
                        care_label_pos.add(po_no)
        except Exception:
            continue

    return po_numbers, care_label_pos


def _render_missing_report(report: dict) -> None:
    if report["errors"]:
        for error in report["errors"]:
            st.warning(error)
        return

    tab_skc, tab_care = st.tabs(["Missing SKC", "Missing Care Labels"])
    with tab_skc:
        _render_po_table(report["missing_skc"], "SKC")
    with tab_care:
        _render_po_table(report["missing_care_labels"], "Care Label")


def _render_po_table(po_numbers: list[str], doc_type: str) -> None:
    if not po_numbers:
        st.success(f"All {doc_type} files are available.")
        return

    dataframe = pd.DataFrame(
        {
            "Sr No.": range(1, len(po_numbers) + 1),
            "PO Number": po_numbers,
            "Document Type": doc_type,
            "Status": "Missing",
            "Remarks": "",
        }
    )
    st.dataframe(dataframe, use_container_width=True, hide_index=True)
