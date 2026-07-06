import io
import os
import re
from collections import Counter

import fitz
import streamlit as st

from config import STAMP_FILES
from services.file_handler import build_zip, extract_pdf_files
from services.logger import add_log
from ui.components import render_result_download


def render_pdf_stamper(current_user: str) -> None:
    st.subheader("PDF Auto Stamper")

    tab_invoice, tab_packing = st.tabs(["Invoices", "Packing Lists"])

    with tab_invoice:
        uploaded_files = st.file_uploader(
            "Upload invoice PDFs or ZIP files",
            type=["pdf", "zip"],
            accept_multiple_files=True,
            key="invoice_stamper_upload",
        )
        _render_stamp_action(uploaded_files, "Invoice", current_user)

    with tab_packing:
        uploaded_files = st.file_uploader(
            "Upload packing list PDFs or ZIP files",
            type=["pdf", "zip"],
            accept_multiple_files=True,
            key="packing_stamper_upload",
        )
        _render_stamp_action(uploaded_files, "Packing List", current_user)


def _render_stamp_action(uploaded_files, doc_type: str, current_user: str) -> None:
    left, right = st.columns(2)

    if right.button("Clear", use_container_width=True, key=f"clear_{doc_type}"):
        result_key = _result_key(doc_type)
        st.session_state[result_key] = None
        st.rerun()

    if left.button("Stamp", use_container_width=True, type="primary", key=f"stamp_{doc_type}"):
        if not uploaded_files:
            st.error("Please upload PDF or ZIP files first.")
            return

        with st.spinner("Stamping PDF files..."):
            result = stamp_pdfs(uploaded_files, doc_type)
            st.session_state[_result_key(doc_type)] = result
            add_log(current_user, f"Stamped {result['count']} {doc_type} file(s)")

    result = st.session_state.get(_result_key(doc_type))
    if result and result["count"]:
        render_result_download(
            "Download ZIP",
            result["data"],
            f"stamped_{doc_type.lower().replace(' ', '_')}.zip",
            "application/zip",
        )
    elif result and result["errors"]:
        st.warning("No files were stamped.")
        st.dataframe(result["errors"], use_container_width=True, hide_index=True)


def stamp_pdfs(uploaded_files, doc_type: str) -> dict:
    stamp_path = STAMP_FILES[doc_type]
    if not stamp_path.exists():
        return {
            "count": 0,
            "data": b"",
            "errors": [{"File Name": str(stamp_path), "Reason": "Stamp image not found"}],
        }

    stamp_bytes = stamp_path.read_bytes()
    extracted_files = extract_pdf_files(uploaded_files)
    output_files: list[tuple[str, bytes]] = []
    errors: list[dict] = []
    base_names: list[str] = []

    for uploaded_file in extracted_files:
        try:
            stamped_name, stamped_pdf = _stamp_one_pdf(uploaded_file.name, uploaded_file.data, stamp_bytes, doc_type)
            output_files.append((stamped_name, stamped_pdf))
            base_names.append(os.path.splitext(stamped_name)[0])
        except Exception as exc:
            errors.append({"File Name": uploaded_file.name, "Reason": str(exc)})

    output_files = _dedupe_file_names(output_files)

    return {
        "count": len(output_files),
        "data": build_zip(output_files) if output_files else b"",
        "errors": errors,
    }


def _stamp_one_pdf(file_name: str, raw_pdf: bytes, stamp_bytes: bytes, doc_type: str) -> tuple[str, bytes]:
    doc = fitz.open(stream=raw_pdf, filetype="pdf")
    text = " ".join(page.get_text() for page in doc)
    base_name = _build_output_base_name(file_name, text)

    if doc_type == "Invoice":
        _stamp_invoice(doc, stamp_bytes)
    else:
        _stamp_packing_list(doc, stamp_bytes)

    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return f"{base_name}.pdf", output.getvalue()


def _build_output_base_name(file_name: str, text: str) -> str:
    order_match = re.search(r"H&M Order No:\s*(\d{6})", text)
    dest_match = re.search(r"Final Destination:.*?\b([A-Z]{2})\b", text, re.DOTALL)

    order_no = order_match.group(1) if order_match else ""
    destination = dest_match.group(1) if dest_match else ""

    if order_no and destination:
        return f"{order_no} {destination}"

    return os.path.splitext(file_name)[0].replace("_PL", "").replace(" PL", "")


def _stamp_invoice(doc, stamp_bytes: bytes) -> None:
    for page in doc:
        matches = page.search_for("Signature:")
        if matches:
            rect = fitz.Rect(matches[0].x1 + 30, matches[0].y0 - 3, matches[0].x1 + 140, matches[0].y0 + 42)
            page.insert_image(rect, stream=stamp_bytes)
            return

    doc[-1].insert_image(fitz.Rect(450, 700, 560, 745), stream=stamp_bytes)


def _stamp_packing_list(doc, stamp_bytes: bytes) -> None:
    page = doc[0]
    matches = page.search_for("Product weight")
    rect = fitz.Rect(380, matches[0].y0 + 30, 520, matches[0].y0 + 100) if matches else fitz.Rect(400, 620, 540, 690)
    page.insert_image(rect, stream=stamp_bytes)


def _dedupe_file_names(files: list[tuple[str, bytes]]) -> list[tuple[str, bytes]]:
    total = Counter(name for name, _ in files)
    seen = Counter()
    deduped = []

    for name, data in files:
        seen[name] += 1
        if total[name] == 1 or seen[name] == 1:
            deduped.append((name, data))
            continue

        root, ext = os.path.splitext(name)
        deduped.append((f"{root}-{seen[name] - 1}{ext}", data))

    return deduped


def _result_key(doc_type: str) -> str:
    return f"pdf_stamper_{doc_type.lower().replace(' ', '_')}_result"
