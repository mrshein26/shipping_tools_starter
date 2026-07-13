import streamlit as st
import io
import os
import re
import zipfile
import pandas as pd
from collections import Counter
from openpyxl.styles import PatternFill, Font, Alignment

# Google Drive API Imports
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2 import service_account

# PDFplumber & pypdf Imports
import pdfplumber
from pypdf import PdfWriter

from core.utils import add_log
from views.pdf_stamper_view import extract_files  # တူညီသော extract_files အား ပြန်လည်အသုံးပြုခြင်း

# =========================================================
# TOOL 2: DOCUMENT COMBINER
# =========================================================
def render_document_combiner_ui():
    st.subheader("🗂️ Document Combiner")
    st.write("Google Drive နှင့် ချိတ်ဆက်၍ Sketch/Care Labels များ စစ်ဆေးခြင်းနှင့် စာရွက်စာတမ်းများ ပေါင်းစပ်ခြင်း စနစ်")

    # Session States များ စတင်သတ်မှတ်ခြင်း
    if "up_key" not in st.session_state: st.session_state.up_key = 0
    if "combiner_res" not in st.session_state: st.session_state.combiner_res = None

    def authenticate_gdrive():
        try:
            creds_info = st.secrets["gcp_service_account"]
            creds = service_account.Credentials.from_service_account_info(creds_info)
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            return None
            
    def clear_files():
        st.session_state.up_key += 1
        st.session_state.combiner_res = None
        st.rerun()

    SKC_FOLDER_ID = "1G79u-7bMJIoaKJJ7Nytir6Gmw2JsA9hW"
    
    SKU_FOLDERS = {
        "Carelabels": "1yC8jPbMHbAG422yNQzaWS9SLPvpXd7_1",
        "Declaration of NWPM (CN)": "12z376dGIo6JQjykJ0Yg5LFQv3vReUyd3",
        "DMAM (JP)": "1RBKMBil1FDK0fvmb1G-zmm-sJLjO-nLi",
        "Org Criterion (IN)": "1KkwS3nwD09lzZeooTxbKJgV-wY0Za4gi",
        "Statement of Origin (CA)": "133YC0_osh0GMHCENaPj04-utodtlxzkF",
        "Cover Sheets": "1xKLBZ6BEET3ZD4_9qmu9dGWMjzN8MVav",
        "CERTIFICADO DE ORIGEN (CL)": "1gGgzOlMjR4zVCVC9iglOzhEDam-ysFAF"
    }

    def get_wh(pdf_f):
        try:
            pdf_f.seek(0)
            with pdfplumber.open(pdf_f) as p:
                for page in p.pages:
                    text = page.extract_text() or ""
                    if "INVOICE" in text.upper():
                        m = re.search(r"\b([A-Z]{3}\d{3})\b", text)
                        if m:
                            return m.group(1)
            return None
        except: 
            return None

    # Variables များကို ကြိုတင်ကြေညာခြင်း
    u_i, u_p, u_e = None, None, None

    col1, col2 = st.columns(2)
    with col1:
        u_i = st.file_uploader("Upload INV (PDFs or ZIP)", type=["pdf", "zip"], accept_multiple_files=True, key=f"c_i_{st.session_state.up_key}")
    with col2:
        u_p = st.file_uploader("Upload PKL (PDFs or ZIP)", type=["pdf", "zip"], accept_multiple_files=True, key=f"c_p_{st.session_state.up_key}")
    
    u_e = st.file_uploader("📊 Upload Excel/CSV (PO List) for Checking", type=["xlsx", "xls", "csv"], accept_multiple_files=True, key=f"c_e_{st.session_state.up_key}")
    
    # -------------------------------------------------------------------------
    # 🔍 SKC & Care Labels Checker Section
    # -------------------------------------------------------------------------
    if st.button("🔍 Check Missing Sketch & Care Label in Drive", use_container_width=True, type="primary"):
        if not u_i and not u_e:
            st.error("⚠️ လိုအပ်သော PO နံပါတ်များ သိရှိရန် INV ဖိုင်များ (သို့မဟုတ်) Excel ဖိုင်ကို အရင် Upload လုပ်ပေးပါ။")
        else:
            with st.spinner("Google Drive တွင် Sketch နှင့် Care Label များ စစ်ဆေးနေပါသည်..."):
                drive_service = authenticate_gdrive()
                if drive_service:
                    req_pos = set()
                    excel_care_label_pos = set()
                    target_skus = ["CN", "OB", "RU", "OR", "MX", "LD", "TW", "CO", "EC", "JP", "OJ"]
                    
                    if u_i:
                        u_i_copied = extract_files(u_i)
                        for inv in u_i_copied:
                            po_m = re.search(r"(\d{6})", inv.name)
                            if po_m: req_pos.add(po_m.group(1))
                    
                    if u_e:
                        target_sku_pattern = r"\b(" + "|".join(target_skus) + r")\b"
                        for excel_file in u_e:
                            try:
                                if excel_file.name.endswith('.csv'):
                                    df = pd.read_csv(excel_file, on_bad_lines='skip', header=None)
                                else:
                                    df = pd.read_excel(excel_file, header=None)
                                
                                for index, row in df.iterrows():
                                    row_str = " ".join([str(val) for val in row.values]).upper()
                                    po_matches = re.findall(r"\b(\d{6})\b", row_str)
                                    for po in po_matches:
                                        req_pos.add(po)
                                        if re.search(target_sku_pattern, row_str):
                                            excel_care_label_pos.add(po)
                            except Exception as e:
                                st.error(f"❌ '{excel_file.name}' ဖိုင်ဖတ်ရာတွင် အမှားအယွင်းရှိပါသည်: {e}")
                    
                    if not req_pos:
                        st.warning("⚠️ Upload လုပ်ထားသော ဖိုင်များထဲတွင် PO နံပါတ် (ဂဏန်း ၆ လုံး) ရှာမတွေ့ပါ။")
                    else:
                        missing_skcs = set()
                        missing_carelabels = set()
                        CARELABEL_FOLDER_ID = "1yC8jPbMHbAG422yNQzaWS9SLPvpXd7_1"
                        
                        for po in req_pos:
                            skc_query = f"name contains '{po}' and '{SKC_FOLDER_ID}' in parents and trashed=false"
                            try:
                                skc_items = drive_service.files().list(q=skc_query, fields="files(id, name)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute().get('files', [])
                                if not skc_items: missing_skcs.add(po)
                            except: missing_skcs.add(po)
                                
                            has_care_label_sku = False
                            if u_i:
                                for inv in u_i_copied:
                                    if po in inv.name and any(sku in inv.name.upper() for sku in target_skus):
                                        has_care_label_sku = True
                                        break
                            if po in excel_care_label_pos:
                                has_care_label_sku = True
                                
                            if has_care_label_sku:
                                cl_query = f"name contains '{po}' and '{CARELABEL_FOLDER_ID}' in parents and trashed=false"
                                try:
                                    cl_items = drive_service.files().list(q=cl_query, fields="files(id, name)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute().get('files', [])
                                    if not cl_items: missing_carelabels.add(po)
                                except: missing_carelabels.add(po)

                        tab_skc, tab_cl = st.tabs(["🖼️ Missing Sketch", "🏷️ Missing Care Labels"])
                        skc_list = sorted(list(missing_skcs))
                        df_skc = pd.DataFrame({
                            "Sr No.": range(1, len(skc_list) + 1),
                            "PO Number": skc_list,
                            "Document Type": ["SKC (Sketch)"] * len(skc_list),
                            "Status": ["Missing"] * len(skc_list),
                            "Remarks": [""] * len(skc_list)
                        }) if skc_list else pd.DataFrame(columns=["Sr No.", "PO Number", "Document Type", "Status", "Remarks"])

                        cl_list = sorted(list(missing_carelabels))
                        df_cl = pd.DataFrame({
                            "Sr No.": range(1, len(cl_list) + 1),
                            "PO Number": cl_list,
                            "Document Type": ["Care Label"] * len(cl_list),
                            "Status": ["Missing"] * len(cl_list),
                            "Remarks": [""] * len(cl_list)
                        }) if cl_list else pd.DataFrame(columns=["Sr No.", "PO Number", "Document Type", "Status", "Remarks"])
                        
                        with tab_skc:
                            if missing_skcs:
                                st.warning(f"⚠️ Drive တွင် မရှိသေးသော Sketch များ စစုပေါင်း: **{len(missing_skcs)}** ခု")
                                st.dataframe(df_skc, use_container_width=True, hide_index=True)
                            else:
                                st.success("✅ လိုအပ်သော Sketch ဖိုင်များအားလုံး Drive တွင် ရှိပြီးဖြစ်ပါသည်။")
                                
                        with tab_cl:
                            if missing_carelabels:
                                st.warning(f"⚠️ Drive တွင် မရှိသေးသော Care Labels များ စုစုပေါင်း: **{len(missing_carelabels)}** ခု")
                                st.dataframe(df_cl, use_container_width=True, hide_index=True)
                            else:
                                st.success("✅ လိုအပ်သော Care Label ဖိုင်များအားလုံး Drive တွင် ရှိပြီးဖြစ်ပါသည်။")
                        
                        if missing_skcs or missing_carelabels:
                            towrite = io.BytesIO()
                            with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
                                if skc_list: df_skc.to_excel(writer, index=False, sheet_name='Missing_SKCs')
                                if cl_list: df_cl.to_excel(writer, index=False, sheet_name='Missing_CareLabels')
                                
                                for sheet_name in writer.sheets:
                                    worksheet = writer.sheets[sheet_name]
                                    worksheet.freeze_panes = 'A2'
                                    worksheet.auto_filter.ref = worksheet.dimensions
                                    header_fill = PatternFill(start_color="E6F0FA", end_color="E6F0FA", fill_type="solid")
                                    header_font = Font(bold=True)
                                    header_alignment = Alignment(horizontal="center", vertical="center")
                                    
                                    for cell in worksheet[1]:
                                        cell.font = header_font
                                        cell.fill = header_fill
                                        cell.alignment = header_alignment

                                    for col in worksheet.columns:
                                        max_length = 0
                                        column = col[0].column_letter
                                        for cell in col:
                                            try:
                                                if col[0].value != "Remarks" and cell.row > 1:
                                                    cell.alignment = Alignment(horizontal="center", vertical="center")
                                                if col[0].value == "PO Number" and cell.row > 1:
                                                    cell.number_format = '@'
                                                if len(str(cell.value)) > max_length:
                                                    max_length = len(str(cell.value))
                                            except: pass
                                        adjusted_width = (max_length + 3) if worksheet[column+'1'].value != "Remarks" else 30
                                        worksheet.column_dimensions[column].width = adjusted_width
                            
                            st.divider()
                            st.download_button(
                                label="📥 Download Standard Missing Report (Excel)",
                                data=towrite.getvalue(),
                                file_name="Missing_SKC_and_CareLabels_Report.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                            log_msg = f"Checked Missing: Found {len(missing_skcs)} SKCs, {len(missing_carelabels)} CareLabels"
                            add_log(st.session_state.get('current_user', 'Unknown'), log_msg)
                else:
                    st.error("❌ Google Drive သို့ ချိတ်ဆက်၍ မရပါ။ (Secrets.toml ရှိ gcp_service_account ကို စစ်ဆေးပါ)")

    # -------------------------------------------------------------------------
    # 🔗 Merge Documents & Clear Files ခလုတ်များ အပိုင်း
    # -------------------------------------------------------------------------
    cb_col1, cb_col2 = st.columns(2)
        
    if cb_col1.button("🔗 Merge Documents", use_container_width=True, key="m_all", type="secondary"):
        if not u_i or not u_p: 
            st.error("⚠️ INV နှင့် PKL ဖိုင် နှစ်ခုလုံးကို အရင် Upload လုပ်ပေးပါ။")
        else:
            with st.spinner('Merging Documents & Checking SKU Folders...'):
                pkl_map = {}; ex_map = {}
                ext_u_p = extract_files(u_p)
                ext_u_i = extract_files(u_i)
                ext_u_o = []
                ext_u_s = []

                drive_service = authenticate_gdrive()
                if drive_service:
                    req_pos = set()
                    for inv in ext_u_i:
                        po_m = re.search(r"(\d{6})", inv.name)
                        if po_m: req_pos.add(po_m.group(1))

                    up_skcs = {}
                    for po in req_pos:
                        try:
                            query = f"name contains '{po}' and '{SKC_FOLDER_ID}' in parents and trashed=false"
                            res = drive_service.files().list(q=query, fields="files(id, name)").execute()
                            items = res.get('files', [])

                            if items:
                                request = drive_service.files().get_media(fileId=items[0]['id'])
                                fh = io.BytesIO()
                                downloader = MediaIoBaseDownload(fh, request)
                                done = False
                                while done is False: _, done = downloader.next_chunk()
                                fh.seek(0)
                                fh.name = items[0]['name'] 
                                ext_u_s.append(fh)
                        except: pass 

                    ext_u_o_s = ext_u_o + ext_u_s
                    skc_pos = set()
                    for s in ext_u_s:
                        m = re.search(r"(\d{6})", s.name)
                        if m: skc_pos.add(m.group(1))
                    
                    for p in ext_u_p:
                        m = re.search(r"(\d{6})(?:\s+|-)?([A-Za-z]{2}).*?([A-Z]{3}\d{3})", p.name, re.IGNORECASE)
                        if m: 
                            pkl_map[(m.group(1), m.group(2).upper(), m.group(3).upper())] = p
                    
                    for e in ext_u_o_s:
                        m = re.search(r"(\d{6})", e.name)
                        if m:
                            po_num = m.group(1)
                            if po_num not in ex_map: ex_map[po_num] = []
                            ex_map[po_num].append(e)
                    
                    zip_b = io.BytesIO(); count = 0
                    error_logs = []; used_pkls = set()

                    with zipfile.ZipFile(zip_b, "w", zipfile.ZIP_DEFLATED) as zf:
                        for inv in ext_u_i:
                            po_m = re.search(r"(\d{6})(?:\s+|-)?([A-Z]{2,})?", inv.name, re.IGNORECASE)
                            if po_m:
                                po = po_m.group(1)
                                sku = po_m.group(2).upper() if po_m.group(2) else "" 
                                wh = get_wh(inv)
                                
                                if not sku and wh:
                                    matched_keys = [k for k in pkl_map.keys() if k[0] == po and k[2] == wh]
                                    if matched_keys: sku = matched_keys[0][1]

                                if sku and wh and (po, sku, wh) in pkl_map:
                                    merger = PdfWriter()
                                    inv.seek(0)
                                    merger.append(inv)
                                    
                                    pkl_file = pkl_map[(po, sku, wh)]
                                    pkl_file.seek(0)
                                    merger.append(pkl_file) 
                                    
                                    for ex in ex_map.get(po, []): 
                                        ex.seek(0)
                                        merger.append(ex)
                                    
                                    if sku and drive_service:
                                        target_folders = set()
                                        if sku in ["GB", "OG", "ID", "ME", "OD", "IX", "PA"] or (sku == "OL" and wh == "IDW262"):
                                            target_folders.add(SKU_FOLDERS["Cover Sheets"])
                                        if sku in ["CN", "OB", "RU", "OR", "MX", "LD", "TW", "CO", "EC", "JP", "OJ"]:
                                            target_folders.add(SKU_FOLDERS["Carelabels"])
                                        if sku in ["CN", "OB"]:
                                            target_folders.add(SKU_FOLDERS["Declaration of NWPM (CN)"])
                                        if sku in ["JP", "OJ"]:
                                            target_folders.add(SKU_FOLDERS["DMAM (JP)"])
                                        if sku in ["IN", "OI"]:
                                            target_folders.add(SKU_FOLDERS["Org Criterion (IN)"])
                                        if sku in ["CA", "DR"]:
                                            target_folders.add(SKU_FOLDERS["Statement of Origin (CA)"])
                                        if sku == "CL":
                                            target_folders.add(SKU_FOLDERS["CERTIFICADO DE ORIGEN (CL)"])
                                            
                                        for folder_id in target_folders:
                                            sku_query = f"name contains '{po}' and '{folder_id}' in parents and trashed=false"
                                            try:
                                                sku_res = drive_service.files().list(q=sku_query, fields="files(id, name)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
                                                sku_items = sku_res.get('files', [])
                                                
                                                if sku_items:
                                                    sku_request = drive_service.files().get_media(fileId=sku_items[0]['id'])
                                                    sku_fh = io.BytesIO()
                                                    sku_downloader = MediaIoBaseDownload(sku_fh, sku_request)
                                                    sku_done = False
                                                    while sku_done is False: _, sku_done = sku_downloader.next_chunk()
                                                    sku_fh.seek(0)
                                                    
                                                    if folder_id == SKU_FOLDERS["Cover Sheets"]:
                                                        merger.merge(0, sku_fh)
                                                    else:
                                                        merger.append(sku_fh)
                                            except: pass

                                    out = io.BytesIO(); merger.write(out); doc_bytes = out.getvalue()
                                    final_filename = f"{po} {sku}-{wh}.pdf" if sku else f"{po}-{wh}.pdf"
                                    zf.writestr(final_filename, doc_bytes)
                                    count += 1; used_pkls.add((po, sku, wh)) 
                                    
                                    if po not in skc_pos:
                                        error_logs.append({"Type": "Sketch", "File Name": f"PO: {po}", "Status": "Warning", "Reason": "Missing Sketch file in Drive"})
                                else:
                                    reason = "Matching PKL not found" if wh else "Warehouse ID not found in Invoice"
                                    error_logs.append({"File Name": inv.name, "Status": "Failed", "Reason": reason, "Type": "Invoice"})
                            else:
                                error_logs.append({"File Name": inv.name, "Status": "Skipped", "Reason": "PO Number missing in name", "Type": "Invoice"})
                        
                        for (p_po, p_sku, p_wh), p_file in pkl_map.items(): 
                            if (p_po, p_sku, p_wh) not in used_pkls:
                                error_logs.append({"File Name": p_file.name, "Status": "Failed", "Reason": "Matching Invoice not found", "Type": "Packing List"})
                                    
                    if count > 0:
                        add_log(st.session_state.current_user, f"Merged {count} docs")
                    st.session_state.combiner_res = {"count": count, "zip_data": zip_b.getvalue() if count > 0 else None, "error_logs": error_logs}
                    st.rerun()

    if cb_col2.button("🗑️ Clear All Files", key="clr_merge_all", use_container_width=True): 
        clear_files()

    # ਰလဒ်များအား ခလုတ်အပြင်ဘက်တွင် သန့်ရှင်းစွာ ပြသခြင်း
    if st.session_state.get('combiner_res'):
        res = st.session_state.combiner_res
        if res["count"] > 0:
            st.success(f"🎉 Merged {res['count']} files successfully!")
            st.download_button("📥 Download Merged ZIP", res["zip_data"], "merged_documents.zip", use_container_width=True)
        else: 
            st.warning("⚠️ No matching INV and PKL found to merge.")
            
        if res["error_logs"]:
            st.markdown("---")
            st.subheader("⚠️ Missing Documents Report")
            df_errors = pd.DataFrame(res["error_logs"])
            df_errors.insert(0, 'Sr No', [str(i) for i in range(1, 1 + len(df_errors))])
            df_errors = df_errors[["Sr No", "Type", "File Name", "Status", "Reason"]]
            
            def highlight_alt_rows(x): return ['background-color: rgba(59, 130, 246, 0.05)' if i % 2 == 0 else '' for i in range(len(x))]
            st.dataframe(df_errors.style.apply(highlight_alt_rows, axis=0), use_container_width=True, hide_index=True)
            
            csv_data = df_errors.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Download Error Report (CSV)", data=csv_data, file_name=f"Missing_Docs_Report.csv", mime="text/csv", use_container_width=True)