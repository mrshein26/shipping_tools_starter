import streamlit as st
import subprocess
import os
import io
import zipfile
import tempfile
import shutil
import re
import fitz  # PyMuPDF
from core.utils import add_log, extract_files

def process_and_compress_pdf(pdf_data, pdf_name, folder_name, temp_dir, gs_setting, zf, stats):
    orig_size = len(pdf_data)
    stats['original_size'] += orig_size
    
    input_path = os.path.join(temp_dir, f"in_{pdf_name}")
    output_path = os.path.join(temp_dir, f"out_{pdf_name}")

    with open(input_path, "wb") as f:
        f.write(pdf_data)

    gs_cmd = [
        "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={gs_setting}", "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}", input_path
    ]

    try:
        subprocess.run(gs_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(output_path):
            comp_size = os.path.getsize(output_path)
            
            if comp_size >= orig_size:
                final_data = pdf_data
                final_size = orig_size
            else:
                with open(output_path, "rb") as f:
                    final_data = f.read()
                final_size = comp_size
                
            stats['compressed_size'] += final_size
            zf.writestr(f"{folder_name}/{pdf_name}", final_data)
            stats['count'] += 1
            
    except Exception as e:
        st.error(f"❌ Error compressing {pdf_name}: {e}")

# 💡 ပြင်ဆင်ထားသော AZO Test Report Renamer Function (Smart Text Extraction)
def get_azo_new_filename(file_bytes, original_name):
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join([page.get_text("text") for page in doc])
        doc.close()
        
        # 1. ORDER NO
        order_m = re.search(r"ORDER NO\s*([0-9,\s]+)", text)
        order_no = order_m.group(1).strip().replace(', ', '_').replace(' ', '_').replace(',', '_') if order_m else "UNKNOWN_PO"
        
        # 2. Test Report No
        report_m = re.search(r"Test Report:\s*([^\n]+)", text)
        report_no = report_m.group(1).strip().replace('/', '-') if report_m else "UNKNOWN_REPORT"
        
        # 3. Report Date
        date_m = re.search(r"Report Date:\s*([A-Za-z]+\s\d{1,2},\s\d{4})", text)
        report_date = date_m.group(1).strip().replace(', ', '_').replace(' ', '_').replace(',', '') if date_m else "UNKNOWN_DATE"
        
        # 4. Production Office / Country of Production (💡 မည်သည့်စာသားမဆို ဖမ်းယူမည့် စနစ်)
        prod_office = "UNKNOWN_OFFICE"
        prod_idx = text.upper().find("PRODUCTION")
        
        if prod_idx != -1:
            search_area = text[prod_idx:]
            tokens = re.split(r'\s+', search_area)
            
            # ကျော်သွားရမည့် Table Header စာသားများ (ဤစာသားများမဟုတ်သော ပထမဆုံးစကားလုံးကို ယူမည်)
            ignore_words = {
                "TEST", "PACKAGE", "APPLICANT", "APPLICANTS", "PROVIDED", "CARE", 
                "LABEL", "FINAL", "CONFIRMATION", "CONFIRMATIO", "RECEIVED", "DATE", 
                "REVISION", "REASON", "H", "M", "PRODUCTION", "OFFICE", "COUNTRY", "OF"
            }
            
            for i, token in enumerate(tokens):
                # အက္ခရာများသီးသန့် စစ်ထုတ်ခြင်း
                clean_token = re.sub(r'[^A-Za-z]', '', token)
                
                # Header စာသားမဟုတ်သော အဓိကစာသား (ဥပမာ - Myanmar သို့မဟုတ် Others) ကို ရှာတွေ့ပါက
                if len(clean_token) >= 3 and clean_token.upper() not in ignore_words:
                    prod_office = clean_token.title()
                    
                    # အကယ်၍ နိုင်ငံအမည် ၂ လုံးတွဲ (ဥပမာ - Sri Lanka, Hong Kong) ဖြစ်နေလျှင် တွဲယူရန်
                    if i + 1 < len(tokens):
                        next_clean = re.sub(r'[^A-Za-z]', '', tokens[i+1])
                        if next_clean.upper() in ["LANKA", "KONG", "KOREA", "KINGDOM", "AFRICA"]:
                            prod_office += f"_{next_clean.title()}"
                    break
        
        # ပေါင်းစပ်၍ နာမည်အသစ်ပေးခြင်း
        new_filename = f"{order_no}_{report_no}_{report_date}_{prod_office}.pdf"
        
        # နာမည်အရမ်းရှည်သွားပါက ဖြတ်တောက်ရန်
        if len(new_filename) > 200: 
            new_filename = new_filename[:190] + ".pdf"
            
        return new_filename
    except Exception:
        return original_name

def render_pdf_compressor_ui():
    st.subheader("🗜️ PDF Tools & Reports")
    
    if not shutil.which("gs"):
        st.error("⚠️ Server တွင် Ghostscript (`gs`) ကို install လုပ်ထားခြင်း မရှိပါ။ သင့်စက်တွင် `brew install ghostscript` သို့မဟုတ် Cloud `packages.txt` တွင် `ghostscript` ထည့်ပေးပါ။")
        return

    if "compressor_up_key" not in st.session_state: 
        st.session_state.compressor_up_key = 0
        
    def clear_files(): 
        st.session_state.compressor_up_key += 1
        if "compress_result" in st.session_state: del st.session_state.compress_result
        if "azo_res" in st.session_state: del st.session_state.azo_res

    # 💡 Tab ၂ ခု ခွဲလိုက်ပါပြီ
    tab1, tab2 = st.tabs(["🗜️ PDF Compressor", "🏷️ AZO Report Renamer"])

    # ---------------------------------------------------------
    # TAB 1: Multi-Quality PDF Compressor
    # ---------------------------------------------------------
    with tab1:
        uploaded_files = st.file_uploader(
            "Upload PDF(s) or ZIP to Compress", 
            type=["pdf", "zip"], 
            accept_multiple_files=True, 
            key=f"compress_{st.session_state.compressor_up_key}"
        )

        c1, c2 = st.columns([1, 2])
        with c1:
            quality_option = st.selectbox(
                "Compression Quality", 
                options=[
                    "Ebook (Recommended - Standard Quality, Small Size)", 
                    "Screen (Low Quality, Smallest Size)", 
                    "Printer (High Quality, Medium Size)",
                    "Prepress (Max Quality, Retains Original Colors)"
                ]
            )
            
            gs_setting = "/ebook"
            if "Screen" in quality_option: gs_setting = "/screen"
            elif "Printer" in quality_option: gs_setting = "/printer"
            elif "Prepress" in quality_option: gs_setting = "/prepress"

        st.markdown("---")
        col_btn1, col_btn2 = st.columns(2)
        
        if col_btn1.button("⚡ Compress PDFs", width="stretch", type="primary"):
            if not uploaded_files:
                st.error("❌ ကျေးဇူးပြု၍ PDF သို့မဟုတ် ZIP ဖိုင်များကို အရင် Upload တင်ပေးပါ။")
            else:
                with st.spinner(f"Compressing PDFs using {gs_setting} setting... Please wait..."):
                    zip_buffer = io.BytesIO()
                    stats = {'count': 0, 'original_size': 0, 'compressed_size': 0}
                    
                    with tempfile.TemporaryDirectory() as temp_dir:
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                            for uploaded_file in uploaded_files:
                                if uploaded_file.name.lower().endswith(".zip"):
                                    folder_name = os.path.splitext(uploaded_file.name)[0]
                                    try:
                                        with zipfile.ZipFile(uploaded_file, "r") as input_zip:
                                            for item in input_zip.infolist():
                                                if item.filename.lower().endswith(".pdf") and not item.filename.startswith("__MACOSX"):
                                                    pdf_data = input_zip.read(item.filename)
                                                    pdf_name = os.path.basename(item.filename)
                                                    process_and_compress_pdf(pdf_data, pdf_name, folder_name, temp_dir, gs_setting, zf, stats)
                                    except Exception as e:
                                        st.error(f"❌ Error reading ZIP {uploaded_file.name}: {e}")
                                        
                                elif uploaded_file.name.lower().endswith(".pdf"):
                                    folder_name = "Standalone_PDFs"
                                    pdf_data = uploaded_file.getvalue()
                                    pdf_name = uploaded_file.name
                                    process_and_compress_pdf(pdf_data, pdf_name, folder_name, temp_dir, gs_setting, zf, stats)

                    if stats['count'] > 0:
                        st.session_state.compress_result = {
                            "zip_data": zip_buffer.getvalue(),
                            "count": stats['count'],
                            "orig_mb": stats['original_size'] / (1024 * 1024),
                            "comp_mb": stats['compressed_size'] / (1024 * 1024)
                        }
                        add_log(st.session_state.current_user, f"Compressed {stats['count']} PDFs ({quality_option})")
                        st.rerun()

        if col_btn2.button("🗑️ Clear Files", key="clr_btn1", width="stretch"):
            clear_files()
            st.rerun()

        if st.session_state.get("compress_result"):
            res = st.session_state.compress_result
            st.success(f"🎉 Successfully processed {res['count']} PDFs!")
            
            saved_mb = res['orig_mb'] - res['comp_mb']
            saved_percent = (saved_mb / res['orig_mb']) * 100 if res['orig_mb'] > 0 else 0
            
            if saved_percent <= 0:
                st.info(f"💡 ဤဖိုင်များသည် မူလကတည်းက သေးငယ်ပြီးဖြစ်၍ ထပ်မံချုံ့၍ မရနိုင်တော့ပါ။ (အရည်အသွေးမကျစေရန် မူရင်းဖိုင်အတိုင်း ပြန်လည်သိမ်းဆည်းပေးထားပါသည်)")
            else:
                st.info(f"📊 **Compression Stats:** Original: **{res['orig_mb']:.2f} MB** ➡️ Compressed: **{res['comp_mb']:.2f} MB** (Saved: **{saved_mb:.2f} MB** | **{saved_percent:.1f}%** reduction)")
            
            st.download_button(
                label="📥 Download Compressed PDFs (ZIP)",
                data=res["zip_data"],
                file_name="Compressed_PDFs.zip",
                mime="application/zip",
                width="stretch"
            )

    # ---------------------------------------------------------
    # TAB 2: AZO Test Report Renaming
    # ---------------------------------------------------------
    with tab2:
        st.markdown("#### AZO Test Report Renamer")
        st.info("`ORDER NO_Test Report No_report date_Production` ပုံစံဖြင့် အလိုအလျောက် နာမည်ပြောင်းပေးပါသည်။")
        
        up_azos = st.file_uploader(
            "Upload AZO Reports (PDFs or ZIP)", 
            type=["pdf", "zip"], 
            accept_multiple_files=True, 
            key=f"azo_{st.session_state.compressor_up_key}"
        )
        
        # 💡 နာမည်ပြောင်းပြီးရင် တစ်ခါတည်း Compress လုပ်မလား မေးတဲ့အပိုင်း
        do_compress_azo = st.toggle("🗜️ Compress files after renaming?", value=False)
        if do_compress_azo:
            azo_quality = st.selectbox(
                "Select Compression Quality for AZO", 
                options=[
                    "Ebook (Recommended - Standard Quality, Small Size)", 
                    "Screen (Low Quality, Smallest Size)", 
                    "Printer (High Quality, Medium Size)",
                    "Prepress (Max Quality, Retains Original Colors)"
                ],
                key="azo_quality"
            )
            
            azo_gs_setting = "/ebook"
            if "Screen" in azo_quality: azo_gs_setting = "/screen"
            elif "Printer" in azo_quality: azo_gs_setting = "/printer"
            elif "Prepress" in azo_quality: azo_gs_setting = "/prepress"
        
        c_azo1, c_azo2 = st.columns(2)
        if c_azo1.button("🏷️ Rename Reports", type="primary", width="stretch"):
            if not up_azos:
                st.error("❌ ကျေးဇူးပြု၍ AZO Test Report ဖိုင်များကို အရင် Upload တင်ပေးပါ။")
            else:
                with st.spinner("Renaming Reports..."):
                    ext_files = extract_files(up_azos)
                    zip_buf = io.BytesIO()
                    stats = {'count': 0, 'original_size': 0, 'compressed_size': 0}
                    
                    with tempfile.TemporaryDirectory() as temp_dir:
                        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                            for f in ext_files:
                                f.seek(0)
                                file_bytes = f.read()
                                
                                # နာမည်အသစ်ရှာခြင်း
                                new_name = get_azo_new_filename(file_bytes, f.name)
                                
                                # ချုံ့ရန် ရွေးထားပါက
                                if do_compress_azo:
                                    process_and_compress_pdf(file_bytes, new_name, "Renamed_AZO_Reports", temp_dir, azo_gs_setting, zf, stats)
                                else:
                                    zf.writestr(f"Renamed_AZO_Reports/{new_name}", file_bytes)
                                    stats['count'] += 1
                                
                    if stats['count'] > 0:
                        add_log(st.session_state.current_user, f"Renamed {stats['count']} AZO Reports")
                        st.session_state.azo_res = {"count": stats['count'], "data": zip_buf.getvalue()}
                        st.rerun()
                        
        if c_azo2.button("🗑️ Clear Files", key="clr_btn2", width="stretch"):
            clear_files()
            st.rerun()
            
        if st.session_state.get("azo_res"):
            res = st.session_state.azo_res
            st.success(f"✅ အောင်မြင်ပါသည်။ ({res['count']} ဖိုင် နာမည်ပြောင်းပြီးပါပြီ)")
            st.download_button("📥 Download Renamed Files", res["data"], "Renamed_AZO_Reports.zip", mime="application/zip", width="stretch")