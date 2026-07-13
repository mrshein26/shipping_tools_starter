import streamlit as st
import fitz  # PyMuPDF
import io
import os
import re
import zipfile
import subprocess
import tempfile
import shutil
from collections import Counter
from core.utils import add_log, extract_files

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

def render_pdf_stamper_ui():
    st.subheader("📄 All-in-One Auto Stamping")
    st.info("💡 Invoice နှင့် Packing List များကို စနစ်မှ အလိုအလျောက် ခွဲခြား၍  Stamping, Rex Text (TR/OT) and File Size ချုံ့ခြင်းများကို တစ်ပြိုင်နက်တည်း ပြုလုပ်ပေးပါမည်။")

    # Session States
    if "stamper_up_key" not in st.session_state: st.session_state.stamper_up_key = 0
    if "stamper_res" not in st.session_state: st.session_state.stamper_res = None

    def clear_files():
        st.session_state.stamper_up_key += 1
        st.session_state.stamper_res = None
        st.rerun()

    # 🗜️ Expander ကို ဖြုတ်ပြီး Toggle သီးသန့် ထားရှိခြင်း
    do_compress = st.toggle("🗜️ **Compress Output PDFs** (ဖိုင်ဆိုဒ်ကို Quality မကျဘဲ အလိုအလျောက် ချုံ့ပေးမည်)", value=True)
    if do_compress and not shutil.which("gs"):
        st.warning("⚠️ သင့်စက်တွင် Ghostscript ကို Install မလုပ်ထားပါ။ Compression အလုပ်လုပ်မည် မဟုတ်ပါ။")
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

                with st.spinner("စနစ်မှ ဖိုင်များကို အလိုအလျောက် စစ်ဆေးပြီး အလုပ်လုပ်နေပါသည်..."):
                    extracted_files = extract_files(uploaded_raw_files)
                    
                    zip_buf = io.BytesIO()
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
                            
                            # 🔍 Auto-Detect (Invoice လား / PL လား ခွဲခြားခြင်း)
                            if "product weight" in txt_lower or "packing list" in txt_lower:
                                doc_type = "PackingList"
                            elif "invoice" in txt_lower:
                                doc_type = "Invoice"
                            else:
                                doc_type = "PackingList" if "pl" in up_pdf.name.lower() else "Invoice"

                            # 🏷️ PO နှင့် Destination ရှာဖွေခြင်း
                            hm_m = re.search(r"H&M Order No:\s*(\d{6})", text)
                            dest_m = re.search(r"Final Destination:.*?\b([A-Z]{2})\b", text, re.DOTALL)
                            po = hm_m.group(1).strip() if hm_m else ""
                            ds = dest_m.group(1).strip() if dest_m else ""
                            
                            # 💡 ဖိုင်အမည် အသစ်သတ်မှတ်ခြင်း
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
                                
                                # TR/OT အတွက် Declaration ထည့်ခြင်း
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
                                inv_results.append((final_name, final_bytes))
                            else:
                                pl_results.append((final_name, final_bytes))
                                
                        except Exception as e:
                            pass
                            
                    # 📂 ZIP ဖိုင်အတွင်း Sub-folders ခွဲ၍ ထည့်သွင်းခြင်း
                    inv_counts = Counter(); inv_total = Counter(inv_names)
                    pl_counts = Counter(); pl_total = Counter(pl_names)
                    
                    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                        # Invoices Folder
                        for n, c in inv_results:
                            inv_counts[n] += 1
                            fname = f"{n}.pdf" if (inv_total[n] == 1 or inv_counts[n] == 1) else f"{n}-{inv_counts[n]-1}.pdf"
                            zf.writestr(f"Invoices/{fname}", c)
                            
                        # Packing Lists Folder
                        for n, c in pl_results:
                            pl_counts[n] += 1
                            fname = f"{n}.pdf" if (pl_total[n] == 1 or pl_counts[n] == 1) else f"{n}-{pl_counts[n]-1}.pdf"
                            zf.writestr(f"Packing_Lists/{fname}", c)
                            
                    total_processed = len(inv_results) + len(pl_results)
                    
                    if total_processed > 0:
                        add_log(st.session_state.current_user, f"Auto-Stamped {len(inv_results)} Invoices & {len(pl_results)} PLs")
                        st.session_state.stamper_res = {
                            "data": zip_buf.getvalue(), 
                            "inv_cnt": len(inv_results),
                            "pl_cnt": len(pl_results)
                        }

    if c2.button("🗑️ Clear Files", use_container_width=True): 
        clear_files()
        
    # --- Results Display ---
    if st.session_state.stamper_res:
        res = st.session_state.stamper_res
        st.success(f"🎉 အောင်မြင်ပါသည်။ **Invoices ({res['inv_cnt']})** နှင့် **Packing Lists ({res['pl_cnt']})** စုစုပေါင်း ({res['inv_cnt'] + res['pl_cnt']}) ဖိုင်ကို တံဆိပ်တုံးထုပြီး ဖိုဒါခွဲပေးထားပါသည်။")
        st.download_button(
            label="📥 Download Processed Files (ZIP)", 
            data=res["data"], 
            file_name="Stamped_Processed_Files.zip", 
            mime="application/zip",
            use_container_width=True
        )