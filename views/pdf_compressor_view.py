import streamlit as st
import subprocess
import os
import io
import zipfile
import tempfile
import shutil
from core.utils import add_log

def process_and_compress_pdf(pdf_data, pdf_name, folder_name, temp_dir, gs_setting, zf, stats):
    """Folder အလိုက် Zip အတွင်းသို့ ပြန်ထည့်ပေးမည့် လုပ်ငန်းစဉ်"""
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
        # Ghostscript ဖြင့် ချုံ့ခြင်း
        subprocess.run(gs_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(output_path):
            comp_size = os.path.getsize(output_path)
            
            # 💡 Smart Fallback: ချုံ့လိုက်၍ ဖိုင်ဆိုဒ်ပိုကြီးသွားပါက မူရင်းဖိုင်ကိုသာ ပြန်သုံးမည်
            if comp_size >= orig_size:
                final_data = pdf_data
                final_size = orig_size
            else:
                with open(output_path, "rb") as f:
                    final_data = f.read()
                final_size = comp_size
                
            stats['compressed_size'] += final_size
            # 💡 သတ်မှတ်ထားသော ဖိုဒါနာမည်ဖြင့် ZIP အတွင်းသို့ သိမ်းဆည်းခြင်း
            zf.writestr(f"{folder_name}/{pdf_name}", final_data)
            stats['count'] += 1
            
    except Exception as e:
        st.error(f"❌ Error compressing {pdf_name}: {e}")

def render_pdf_compressor_ui():
    st.subheader("🗜️ Multi-Quality PDF Compressor")
    
    if not shutil.which("gs"):
        st.error("⚠️ Server တွင် Ghostscript (`gs`) ကို install လုပ်ထားခြင်း မရှိပါ။ သင့်စက်တွင် `brew install ghostscript` သို့မဟုတ် Cloud `packages.txt` တွင် `ghostscript` ထည့်ပေးပါ။")
        return

    if "compressor_up_key" not in st.session_state: 
        st.session_state.compressor_up_key = 0
        
    def clear_files(): 
        st.session_state.compressor_up_key += 1
        if "compress_result" in st.session_state:
            del st.session_state.compress_result

    uploaded_files = st.file_uploader(
        "Upload PDF(s) or ZIP to Compress", 
        type=["pdf", "zip"], 
        accept_multiple_files=True, 
        key=f"compress_{st.session_state.compressor_up_key}"
    )

    c1, c2 = st.columns([1, 2])
    with c1:
        # 💡 "Max Prepress Quality" ရွေးချယ်စရာ ထပ်တိုးခြင်း
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
    
    if col_btn1.button("⚡ Compress PDFs", use_container_width=True, type="primary"):
        if not uploaded_files:
            st.error("❌ ကျေးဇူးပြု၍ PDF သို့မဟုတ် ZIP ဖိုင်များကို အရင် Upload တင်ပေးပါ။")
        else:
            with st.spinner(f"Compressing PDFs using {gs_setting} setting... Please wait..."):
                zip_buffer = io.BytesIO()
                stats = {'count': 0, 'original_size': 0, 'compressed_size': 0}
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                        for uploaded_file in uploaded_files:
                            
                            # 📦 ZIP ဖိုင်ဖြစ်ပါက ဖိုင်နာမည်ကို Folder အမည်အဖြစ် သတ်မှတ်မည်
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
                                    
                            # 📄 PDF ဖိုင်သီးသန့်ဖြစ်ပါက 'Standalone_PDFs' Folder အတွင်းထည့်မည်
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

    if col_btn2.button("🗑️ Clear Files", use_container_width=True):
        clear_files()
        st.rerun()

    # --- Result Display ---
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
            use_container_width=True
        )