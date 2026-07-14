import streamlit as st
import fitz  # PyMuPDF
import io
import os
import re
import zipfile
import subprocess
import tempfile
import shutil
import pandas as pd
import pdfplumber
from pypdf import PdfWriter
from collections import Counter
from core.utils import add_log, extract_files

# Google Drive API Imports
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def compress_pdf_bytes(pdf_bytes, gs_setting="/ebook"):
    """Ghostscript အသုံးပြု၍ PDF Bytes များကို Compress လုပ်ပေးသော Helper Function"""
    if not shutil.which("gs"):
        return pdf_bytes 
        
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.pdf")
        output_path = os.path.join(temp_dir, "output.pdf")
        
        with open(input_path, "wb") as f:
            f.write(pdf_bytes)
            
        gs_cmd = [
            "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={gs_setting}", "-dNOPAUSE", "-dQUIET", "-dBATCH",
            f"-sOutputFile={output_path}", input_path
        ]
        
        try:
            subprocess.run(gs_cmd, check=True)
            if os.path.exists(output_path):
                with open(output_path, "rb") as f:
                    return f.read()
        except Exception:
            pass
            
    return pdf_bytes

def authenticate_gdrive_local():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(creds_info)
        return build('drive', 'v3', credentials=creds)
    except Exception:
        return None

def get_wh_local(pdf_f):
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
    except: return None

class MemoryFile(io.BytesIO):
    """Memory ပေါ်ရှိ Bytes များကို UploadedFile ပုံစံအဖြစ် အသုံးပြုနိုင်ရန် Wrapper Class"""
    def __init__(self, name, data):
        super().__init__(data)
        self.name = name

# =========================================================
# UI RENDER FUNCTION
# =========================================================
def render_pdf_stamper_ui():
    st.subheader("📄 All-in-One Automation")
    st.info("Stamping, Insert Rex Text (TR/OT), Auto merging (on/off)")

    # Session States
    if "stamper_up_key" not in st.session_state: st.session_state.stamper_up_key = 0
    if "stamper_res" not in st.session_state: st.session_state.stamper_res = None

    def clear_files():
        st.session_state.stamper_up_key += 1
        st.session_state.stamper_res = None
        st.rerun()

    # 🗜️ Toggle Options
    c_tog1, c_tog2 = st.columns([1, 1])
    with c_tog1:
        do_compress = st.toggle("🗜️ **Compress Output PDFs**", value=True)
        if do_compress and not shutil.which("gs"):
            st.warning("⚠️ သင့်စက်တွင် Ghostscript မရှိပါ။ Compression အလုပ်လုပ်မည် မဟုတ်ပါ။")
    with c_tog2:
        do_auto_merge = st.toggle("🔗 **Auto-Merge after Stamping** (Document Combiner အတိုင်း Auto ပေါင်းမည်)", value=False)
    
    st.markdown("---")

    # 📂 All-in-One File Uploader
    uploaded_raw_files = st.file_uploader(
        "📁 Upload Invoices & Packing Lists (PDFs or ZIP)", 
        type=["pdf", "zip"], 
        accept_multiple_files=True, 
        key=f"stamp_all_{st.session_state.stamper_up_key}"
    )

    c1, c2 = st.columns(2)
    
    if c1.button("⚡ Process All Files", use_container_width=True, type="primary"):
        if not uploaded_raw_files:
            st.error("❌ ကျေးဇူးပြု၍ PDF သို့မဟုတ် ZIP ဖိုင်များကို အရင် Upload တင်ပေးပါ။")
        else:
            stamp_inv_path = "assets/images/stamp_invoice.png"
            stamp_pl_path = "assets/images/stamp_pl.png"
            
            if not os.path.exists(stamp_inv_path) or not os.path.exists(stamp_pl_path):
                st.error("⚠️ တံဆိပ်တုံးပုံများ မပြည့်စုံပါ။ `assets/images/` ဖိုဒါအောက်တွင် `stamp_invoice.png` နှင့် `stamp_pl.png` ရှိမရှိ စစ်ဆေးပါ။")
            else:
                with open(stamp_inv_path, "rb") as f: inv_stamp_bytes = f.read()
                with open(stamp_pl_path, "rb") as f: pl_stamp_bytes = f.read()

                with st.spinner("စနစ်မှ ဖိုင်များကို စစ်ဆေးပြီး အလုပ်လုပ်နေပါသည်..."):
                    extracted_files = extract_files(uploaded_raw_files)
                    
                    inv_results = []
                    pl_results = []
                    inv_names = []
                    pl_names = []
                    
                    for up_pdf in extracted_files:
                        try:
                            up_pdf.seek(0)
                            doc = fitz.open(stream=up_pdf.read(), filetype="pdf")
                            text = "".join([p.get_text() for p in doc])
                            txt_lower = text.lower()
                            
                            # 🔍 Auto-Detect
                            if "product weight" in txt_lower or "packing list" in txt_lower:
                                doc_type = "PackingList"
                            elif "invoice" in txt_lower:
                                doc_type = "Invoice"
                            else:
                                doc_type = "PackingList" if "pl" in up_pdf.name.lower() else "Invoice"

                            # 🏷️ PO & Dest
                            hm_m = re.search(r"H&M Order No:\s*(\d{6})", text)
                            dest_m = re.search(r"Final Destination:.*?\b([A-Z]{2})\b", text, re.DOTALL)
                            po = hm_m.group(1).strip() if hm_m else ""
                            ds = dest_m.group(1).strip() if dest_m else ""
                            
                            original_name = os.path.splitext(up_pdf.name)[0]
                            if original_name.startswith("PackerView-"): 
                                original_name = original_name.replace("PackerView-", "", 1)
                            
                            b_name = f"{po} {ds}" if (po and ds) else original_name
                            
                            if doc_type == "Invoice":
                                found = False
                                for p in doc:
                                    inst = p.search_for("Signature:")
                                    if inst:
                                        p.insert_image(fitz.Rect(inst[0].x1 + 30, inst[0].y0 - 3, inst[0].x1 + 140, inst[0].y0 + 42), stream=inv_stamp_bytes)
                                        found = True; break
                                if not found: 
                                    doc[-1].insert_image(fitz.Rect(450, 700, 560, 745), stream=inv_stamp_bytes)
                                    
                                final_name = b_name
                                inv_names.append(final_name)
                                
                            else: # PackingList
                                p = doc[0]
                                inst = p.search_for("Product weight")
                                rect = fitz.Rect(380, inst[0].y0 + 30, 520, inst[0].y0 + 100) if inst else fitz.Rect(400, 620, 540, 690)
                                p.insert_image(rect, stream=pl_stamp_bytes)
                                
                                if ds in ["TR", "OT"] or "/ot/" in txt_lower or "/tr/" in txt_lower:
                                    last_p = doc[-1]
                                    blocks = last_p.get_text("blocks")
                                    lowest_y = max([blk[3] for blk in blocks]) if blocks else 36
                                    
                                    if (last_p.rect.height - lowest_y) < 100:
                                        doc.new_page(width=doc[0].rect.width, height=doc[0].rect.height)
                                        last_p = doc[-1]
                                        lowest_y = 36
                                        
                                    dec_txt = 'Declaration: "The exporter Rex MMREX01032 of the products covered by this the document declares that, except where otherwise clearly indicated, these products are of MYANMAR preferential origin according to rules of origin of the Generalized System of Preferences of the Türkiye and that the origin criterion met is W6110"'
                                    rect_dec = fitz.Rect(36, lowest_y + 10, last_p.rect.width - 36, last_p.rect.height - 20)
                                    last_p.insert_textbox(rect_dec, dec_txt, fontsize=9, fontname="helv", align=fitz.TEXT_ALIGN_JUSTIFY)
                                    
                                final_name = f"{b_name} PL" if not b_name.endswith(" PL") else b_name
                                pl_names.append(final_name)
                                
                            # Save & Compress
                            pdf_o = io.BytesIO()
                            doc.save(pdf_o, deflate=True, garbage=4)
                            doc.close()
                            
                            final_bytes = pdf_o.getvalue()
                            if do_compress:
                                final_bytes = compress_pdf_bytes(final_bytes)
                                
                            if doc_type == "Invoice":
                                inv_results.append((final_name, final_bytes, up_pdf.name))
                            else:
                                pl_results.append((final_name, final_bytes, up_pdf.name))
                                
                        except Exception as e:
                            pass
                            
                    # -------------------------------------------------------------
                    # 🔀 OUTPUT GENERATION LOGIC (Normal VS Auto-Merge)
                    # -------------------------------------------------------------
                    if not do_auto_merge:
                        zip_buf = io.BytesIO()
                        inv_counts = Counter(); inv_total = Counter(inv_names)
                        pl_counts = Counter(); pl_total = Counter(pl_names)
                        
                        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                            for n, c, orig_name in inv_results:
                                inv_counts[n] += 1
                                fname = f"{n}.pdf" if (inv_total[n] == 1 or inv_counts[n] == 1) else f"{n}-{inv_counts[n]-1}.pdf"
                                zf.writestr(f"Invoices/{fname}", c)
                                
                            for n, c, orig_name in pl_results:
                                pl_counts[n] += 1
                                fname = f"{n}.pdf" if (pl_total[n] == 1 or pl_counts[n] == 1) else f"{n}-{pl_counts[n]-1}.pdf"
                                zf.writestr(f"Packing_Lists/{fname}", c)
                                
                        total_processed = len(inv_results) + len(pl_results)
                        if total_processed > 0:
                            add_log(st.session_state.current_user, f"Auto-Stamped {len(inv_results)} Invoices & {len(pl_results)} PLs")
                            st.session_state.stamper_res = {
                                "type": "stamped_only",
                                "data": zip_buf.getvalue(), 
                                "inv_cnt": len(inv_results),
                                "pl_cnt": len(pl_results)
                            }
                    else:
                        st.info("🔄 Auto-Merge ဖွင့်ထားသဖြင့် Document Combiner လုပ်ငန်းစဉ်ကို ဆက်လက်လုပ်ဆောင်နေပါသည် (Google Drive မှ ဖိုင်များ ရယူနေပါသည်)...")
                        
                        # မှတ်ဉာဏ်ထဲရှိ တံဆိပ်တုံးထုပြီးသား ဖိုင်များကို Combiner သုံးနိုင်ရန် ပြောင်းလဲခြင်း
                        ext_u_i = [MemoryFile(orig_name, b) for _, b, orig_name in inv_results]
                        ext_u_p = [MemoryFile(orig_name, b) for _, b, orig_name in pl_results]
                        
                        drive_service = authenticate_gdrive_local()
                        if not drive_service:
                            st.error("❌ Google Drive သို့ ချိတ်ဆက်၍ မရပါ။ Auto-Merge ကို ရပ်နားလိုက်ပါသည်။")
                        else:
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

                            pkl_map = {}
                            ext_u_s = []
                            
                            req_pos = set()
                            for inv in ext_u_i:
                                po_m = re.search(r"(\d{6})", inv.name)
                                if po_m: req_pos.add(po_m.group(1))

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

                            skc_pos = set()
                            for s in ext_u_s:
                                m = re.search(r"(\d{6})", s.name)
                                if m: skc_pos.add(m.group(1))
                            
                            for p in ext_u_p:
                                m = re.search(r"(\d{6})(?:\s+|-)?([A-Za-z]{2}).*?([A-Z]{3}\d{3})", p.name, re.IGNORECASE)
                                if m: 
                                    pkl_map[(m.group(1), m.group(2).upper(), m.group(3).upper())] = p
                            
                            zip_b = io.BytesIO()
                            count = 0
                            error_logs = []
                            used_pkls = set()

                            with zipfile.ZipFile(zip_b, "w", zipfile.ZIP_DEFLATED) as zf:
                                for inv in ext_u_i:
                                    po_m = re.search(r"(\d{6})(?:\s+|-)?([A-Z]{2,})?", inv.name, re.IGNORECASE)
                                    if po_m:
                                        po = po_m.group(1)
                                        sku = po_m.group(2).upper() if po_m.group(2) else "" 
                                        wh = get_wh_local(inv)
                                        
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
                                            
                                            for ex in ext_u_s: 
                                                if po in ex.name:
                                                    ex.seek(0)
                                                    merger.append(ex)
                                            
                                            if sku:
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
                                add_log(st.session_state.current_user, f"Auto-Stamped & Merged {count} docs")
                            st.session_state.stamper_res = {
                                "type": "merged",
                                "count": count, 
                                "data": zip_b.getvalue() if count > 0 else None, 
                                "error_logs": error_logs
                            }

    if c2.button("🗑️ Clear Files", use_container_width=True): 
        clear_files()
        
    # =========================================================
    # RESULTS DISPLAY SECTION
    # =========================================================
    if st.session_state.stamper_res:
        res = st.session_state.stamper_res
        
        if res.get("type") == "stamped_only":
            st.success(f"🎉 အောင်မြင်ပါသည်။ **Invoices ({res['inv_cnt']})** နှင့် **Packing Lists ({res['pl_cnt']})** စုစုပေါင်း ({res['inv_cnt'] + res['pl_cnt']}) ဖိုင်ကို တံဆိပ်တုံးထုပြီး Folder ခွဲပေးထားပါသည်။")
            st.download_button(
                label="📥 Download Processed Files (ZIP)", 
                data=res["data"], 
                file_name="Stamped_Processed_Files.zip", 
                mime="application/zip",
                use_container_width=True
            )
            
        elif res.get("type") == "merged":
            if res["count"] > 0:
                st.success(f"🎉 အောင်မြင်ပါသည်။ တံဆိပ်တုံးထုခြင်းနှင့် ဖိုင်ပေါင်းစည်းခြင်းအဆင့် ပြီးဆုံးပါပြီ။ (Merged {res['count']} files)")
                st.download_button(
                    label="📥 Download Auto-Merged ZIP", 
                    data=res["data"], 
                    file_name="Auto_Stamped_and_Merged_Documents.zip", 
                    mime="application/zip",
                    use_container_width=True
                )
            else: 
                st.warning("⚠️ No matching INV and PKL found to merge.")
                
            if res.get("error_logs"):
                st.markdown("---")
                st.subheader("⚠️ Missing Documents Report")
                df_errors = pd.DataFrame(res["error_logs"])
                df_errors.insert(0, 'Sr No', [str(i) for i in range(1, 1 + len(df_errors))])
                df_errors = df_errors[["Sr No", "Type", "File Name", "Status", "Reason"]]
                
                def highlight_alt_rows(x): return ['background-color: rgba(59, 130, 246, 0.05)' if i % 2 == 0 else '' for i in range(len(x))]
                st.dataframe(df_errors.style.apply(highlight_alt_rows, axis=0), use_container_width=True, hide_index=True)
                
                csv_data = df_errors.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Error Report (CSV)", 
                    data=csv_data, 
                    file_name="Missing_Docs_Report.csv", 
                    mime="text/csv", 
                    use_container_width=True
                )