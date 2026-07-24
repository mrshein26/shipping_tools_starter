import streamlit as st
import io
import re
import pandas as pd
from openpyxl.styles import PatternFill, Font, Alignment
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime
from dateutil.relativedelta import relativedelta
from core.utils import add_log

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def authenticate_gdrive():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(creds_info)
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        return None

def extract_pos_from_uploads(u_e, target_skus):
    """SKC နှင့် Care Label စစ်ဆေးရန် PO များကို Excel မှ ဆွဲထုတ်ပေးသော Function"""
    req_pos = set()
    excel_care_label_pos = set()
    
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
                pass
                
    return req_pos, excel_care_label_pos

def extract_azo_targets(u_e):
    """Excel မှ SKU 'IN', 'OI', 'TR', 'OT' ပါသော PO များကိုသာ AZO စစ်ဆေးရန် ဆွဲထုတ်သည်"""
    azo_targets = []
    global_tod = "Unknown_TOD"
    
    if not u_e:
        return azo_targets, global_tod
        
    for excel_file in u_e:
        try:
            if excel_file.name.lower().endswith('.csv'):
                continue 
                
            xls = pd.ExcelFile(excel_file)
            sheet_name = xls.sheet_names[0]
            
            # ခေါင်းစဉ်မှ TOD Date ရှာခြင်း
            df_title = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, nrows=1)
            main_title = str(df_title.iloc[0, 0])
            tod_match = re.search(r"TOD\s+(.*)", main_title, re.IGNORECASE)
            if tod_match:
                tod_str = f"TOD {tod_match.group(1).strip()}"
                global_tod = tod_str
            else:
                tod_str = "Unknown TOD"
                
            df = pd.read_excel(excel_file, sheet_name=sheet_name, skiprows=1)
            
            if 'PO NO' in df.columns and 'SKU' in df.columns:
                df['PO NO'] = df['PO NO'].ffill()
                df['SKU'] = df['SKU'].ffill()
                df_filtered = df.dropna(subset=['PO NO', 'SKU'])
                
                for _, row in df_filtered.iterrows():
                    try:
                        po = str(int(row['PO NO']))
                    except:
                        po = str(row['PO NO']).replace('.0', '').strip()
                        
                    sku = str(row['SKU']).strip().upper()
                    
                    # 💡 IN, OI အပြင် TR, OT ပါ ထပ်ထည့်ထားပါသည်
                    if sku in ['IN', 'OI', 'TR', 'OT']:
                        if not any(d['po'] == po for d in azo_targets):
                            azo_targets.append({'po': po, 'sku': sku, 'tod': tod_str})
                            
        except Exception as e:
            st.error(f"❌ '{excel_file.name}' ဖိုင်ဖတ်ရာတွင် အမှားအယွင်းရှိပါသည်: {e}")
            
    return azo_targets, global_tod

def create_missing_df(missing_set, doc_type):
    lst = sorted(list(missing_set))
    return pd.DataFrame({
        "Sr No.": range(1, len(lst) + 1),
        "PO Number": lst,
        "Document Type": [doc_type] * len(lst),
        "Status": ["Missing"] * len(lst),
        "Remarks": [""] * len(lst)
    }) if lst else pd.DataFrame(columns=["Sr No.", "PO Number", "Document Type", "Status", "Remarks"])

def format_excel_sheet(worksheet):
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

# =========================================================
# MAIN UI: DOCUMENT CHECKER
# =========================================================
def render_document_checker_ui():
    st.subheader("🔍 Document Checker (SKC, Care Labels, AZO)")
    st.info("PO နံပါတ်များသိရှိရန် Excel (PO List) ကို Upload တင်ပြီး လိုအပ်သော Document များ ပြည့်စုံမှုရှိမရှိ စစ်ဆေးနိုင်ပါသည်။")

    if "chk_up_key" not in st.session_state: 
        st.session_state.chk_up_key = 0
    if "doc_checker_res" not in st.session_state:
        st.session_state.doc_checker_res = None
        
    def clear_files():
        st.session_state.chk_up_key += 1
        st.session_state.doc_checker_res = None

    u_e = st.file_uploader(
        "📊 Upload Excel/CSV (PO List for SKC, Care Label & AZO Checking)", 
        type=["xlsx", "xls", "csv"], 
        accept_multiple_files=True, 
        key=f"chk_e_{st.session_state.chk_up_key}"
    )

    st.markdown("---")
    
    # ခလုတ် (၃) ခု ထည့်သွင်းခြင်း
    c1, c2, c3 = st.columns(3)
    check_skc_cl = c1.button("🔍 Check SKC & Care Labels", width="stretch", type="primary")
    check_azo = c2.button("🧪 Check AZO Reports", width="stretch", type="primary")
    clear_btn = c3.button("🗑️ Clear Files", width="stretch")

    target_skus = ["CN", "OB", "RU", "OR", "MX", "LD", "TW", "CO", "EC", "JP", "OJ"]

    if clear_btn:
        clear_files()
        st.rerun()

    # -------------------------------------------------------------------------
    # 1️⃣ SKC & CARE LABELS CHECKING LOGIC
    # -------------------------------------------------------------------------
    if check_skc_cl:
        if not u_e:
            st.error("⚠️ လိုအပ်သော PO နံပါတ်များ သိရှိရန် Excel (PO List) ကို အရင် Upload လုပ်ပေးပါ။")
        else:
            with st.spinner("Google Drive တွင် Sketch နှင့် Care Label များ စစ်ဆေးနေပါသည်..."):
                drive_service = authenticate_gdrive()
                if drive_service:
                    req_pos, excel_care_label_pos = extract_pos_from_uploads(u_e, target_skus)
                    
                    if not req_pos:
                        st.warning("⚠️ Upload လုပ်ထားသော ဖိုင်များထဲတွင် PO နံပါတ် (ဂဏန်း ၆ လုံး) ရှာမတွေ့ပါ။")
                    else:
                        missing_skcs = set()
                        missing_carelabels = set()
                        SKC_FOLDER_ID = "1G79u-7bMJIoaKJJ7Nytir6Gmw2JsA9hW"
                        CARELABEL_FOLDER_ID = "1yC8jPbMHbAG422yNQzaWS9SLPvpXd7_1"
                        
                        for po in req_pos:
                            skc_query = f"name contains '{po}' and '{SKC_FOLDER_ID}' in parents and trashed=false"
                            try:
                                skc_items = drive_service.files().list(q=skc_query, fields="files(id, name)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute().get('files', [])
                                if not skc_items: missing_skcs.add(po)
                            except: missing_skcs.add(po)
                                
                            if po in excel_care_label_pos:
                                cl_query = f"name contains '{po}' and '{CARELABEL_FOLDER_ID}' in parents and trashed=false"
                                try:
                                    cl_items = drive_service.files().list(q=cl_query, fields="files(id, name)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute().get('files', [])
                                    if not cl_items: missing_carelabels.add(po)
                                except: missing_carelabels.add(po)

                        df_skc = create_missing_df(missing_skcs, "SKC (Sketch)")
                        df_cl = create_missing_df(missing_carelabels, "Care Label")
                        
                        towrite_bytes = None
                        if missing_skcs or missing_carelabels:
                            towrite = io.BytesIO()
                            with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
                                if missing_skcs: df_skc.to_excel(writer, index=False, sheet_name='Missing_SKCs')
                                if missing_carelabels: df_cl.to_excel(writer, index=False, sheet_name='Missing_CareLabels')
                                for sheet_name in writer.sheets:
                                    format_excel_sheet(writer.sheets[sheet_name])
                            towrite_bytes = towrite.getvalue()

                        # 💡 မှတ်ဉာဏ်ထဲတွင် သိမ်းဆည်းခြင်း
                        st.session_state.doc_checker_res = {
                            "type": "skc_cl",
                            "missing_skcs": missing_skcs,
                            "missing_carelabels": missing_carelabels,
                            "df_skc": df_skc,
                            "df_cl": df_cl,
                            "excel_data": towrite_bytes
                        }
                        add_log(st.session_state.get('current_user', 'Unknown'), f"Checked SKC/CL: Found {len(missing_skcs)} SKC, {len(missing_carelabels)} CL")
                else:
                    st.error("❌ Google Drive သို့ ချိတ်ဆက်၍ မရပါ။ (Secrets.toml ကို စစ်ဆေးပါ)")

    # -------------------------------------------------------------------------
    # 2️⃣ AZO REPORTS CHECKING LOGIC
    # -------------------------------------------------------------------------
    if check_azo:
        if not u_e:
            st.error("⚠️ AZO စစ်ဆေးရန်အတွက် PO နှင့် SKU များပါဝင်သော Excel ဖိုင် (SEA BOOKING LIST) ကို အရင် Upload လုပ်ပေးပါ။")
        else:
            with st.spinner("Google Drive တွင် AZO Report များ စစ်ဆေးနေပါသည်..."):
                drive_service = authenticate_gdrive()
                if drive_service:
                    azo_targets, global_tod = extract_azo_targets(u_e)
                    
                    if not azo_targets:
                        # 💡 Message တွင်ပါ TR, OT ကို ပြင်ဆင်ထားပါသည်
                        st.warning("⚠️ Upload လုပ်ထားသော Excel ဖိုင်ထဲတွင် SKU 'IN', 'OI', 'TR' သို့မဟုတ် 'OT' ပါသော PO များ မတွေ့ရှိပါ။")
                    else:
                        missing_azos = []
                        expiring_azos = []
                        AZO_FOLDER_ID = "16xBMKlJjD7F5jEvnywMp8EWojxWyccQK" 
                        current_date = datetime.now()
                        
                        for target in azo_targets:
                            po = target['po']
                            azo_query = f"name contains '{po}' and '{AZO_FOLDER_ID}' in parents and trashed=false"
                            try:
                                azo_items = drive_service.files().list(q=azo_query, fields="files(id, name)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute().get('files', [])
                                
                                if not azo_items:
                                    missing_azos.append(target)
                                else:
                                    filename = azo_items[0]['name']
                                    date_m = re.search(r"([A-Za-z]+_\d{1,2}_\d{4})", filename)
                                    if date_m:
                                        try:
                                            report_date = datetime.strptime(date_m.group(1), "%B_%d_%Y")
                                            expiry_date = report_date + relativedelta(months=6)
                                            days_left = (expiry_date - current_date).days
                                            
                                            if days_left <= 15:
                                                target['expiry'] = expiry_date.strftime("%B %d, %Y")
                                                target['days_left'] = days_left
                                                expiring_azos.append(target)
                                        except Exception:
                                            pass 
                            except:
                                missing_azos.append(target)

                        def create_azo_df(targets_list, is_expiring=False):
                            data = []
                            for i, t in enumerate(targets_list):
                                row = {
                                    "Sr No.": i + 1,
                                    "PO Number": t['po'],
                                    "Sku": t['sku'],
                                    "Document Type": "AZO Report",
                                    "Status": "Missing" if not is_expiring else ("Expired" if t['days_left'] < 0 else "Expiring Soon"),
                                }
                                if is_expiring:
                                    row["Expiry Date"] = t['expiry']
                                    row["Remarks"] = f"{t['tod']} (Days left: {t['days_left']})"
                                else:
                                    row["Remarks"] = t['tod']
                                data.append(row)
                            cols = ["Sr No.", "PO Number", "Sku", "Document Type", "Status", "Expiry Date", "Remarks"] if is_expiring else ["Sr No.", "PO Number", "Sku", "Document Type", "Status", "Remarks"]
                            return pd.DataFrame(data, columns=cols) if targets_list else pd.DataFrame(columns=cols)

                        df_missing_azo = create_azo_df(missing_azos, is_expiring=False)
                        df_expiring_azo = create_azo_df(expiring_azos, is_expiring=True)
                        
                        missing_excel_bytes = None
                        expiring_excel_bytes = None
                        clean_tod = global_tod.replace('/', '-').replace(':', '') if global_tod != "Unknown_TOD" else "Unknown_Date"

                        if missing_azos:
                            towrite_miss = io.BytesIO()
                            with pd.ExcelWriter(towrite_miss, engine='openpyxl') as writer:
                                df_missing_azo.to_excel(writer, index=False, sheet_name='Missing_AZO')
                                format_excel_sheet(writer.sheets['Missing_AZO'])
                            missing_excel_bytes = towrite_miss.getvalue()
                            
                        if expiring_azos:
                            towrite_exp = io.BytesIO()
                            with pd.ExcelWriter(towrite_exp, engine='openpyxl') as writer:
                                df_expiring_azo.to_excel(writer, index=False, sheet_name='Expiring_AZO')
                                format_excel_sheet(writer.sheets['Expiring_AZO'])
                            expiring_excel_bytes = towrite_exp.getvalue()

                        # 💡 မှတ်ဉာဏ်ထဲတွင် သိမ်းဆည်းခြင်း
                        st.session_state.doc_checker_res = {
                            "type": "azo",
                            "missing_azos": missing_azos,
                            "expiring_azos": expiring_azos,
                            "df_missing_azo": df_missing_azo,
                            "df_expiring_azo": df_expiring_azo,
                            "missing_excel": missing_excel_bytes,
                            "expiring_excel": expiring_excel_bytes,
                            "clean_tod": clean_tod
                        }
                        add_log(st.session_state.get('current_user', 'Unknown'), f"Checked AZO: Missing {len(missing_azos)}, Expiring {len(expiring_azos)}")
                else:
                    st.error("❌ Google Drive သို့ ချိတ်ဆက်၍ မရပါ။ (Secrets.toml ကို စစ်ဆေးပါ)")

    # -------------------------------------------------------------------------
    # 3️⃣ RENDER RESULTS (Session State မှ ပြန်ခေါ်ပြခြင်း)
    # -------------------------------------------------------------------------
    if st.session_state.doc_checker_res:
        res = st.session_state.doc_checker_res
        
        if res["type"] == "skc_cl":
            tab_skc, tab_cl = st.tabs(["🖼️ Missing Sketch", "🏷️ Missing Care Labels"])
            
            with tab_skc:
                if res["missing_skcs"]:
                    st.warning(f"⚠️ Drive တွင် မရှိသေးသော Sketch များ စုစုပေါင်း: **{len(res['missing_skcs'])}** ခု")
                    st.dataframe(res["df_skc"], width="stretch", hide_index=True)
                else:
                    st.success("✅ လိုအပ်သော Sketch ဖိုင်များအားလုံး Drive တွင် ရှိပြီးဖြစ်ပါသည်။")
                    
            with tab_cl:
                if res["missing_carelabels"]:
                    st.warning(f"⚠️ Drive တွင် မရှိသေးသော Care Labels များ စုစုပေါင်း: **{len(res['missing_carelabels'])}** ခု")
                    st.dataframe(res["df_cl"], width="stretch", hide_index=True)
                else:
                    st.success("✅ လိုအပ်သော Care Label ဖိုင်များအားလုံး Drive တွင် ရှိပြီးဖြစ်ပါသည်။")
            
            if res["excel_data"]:
                st.divider()
                st.download_button(
                    label="📥 Download Missing Report (Excel)",
                    data=res["excel_data"],
                    file_name="Missing_SKC_CareLabels_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width="stretch"
                )

        elif res["type"] == "azo":
            tab_azo_miss, tab_azo_exp = st.tabs(["🧪 Missing AZO Reports", "⏳ Expiring AZO Reports"])
            
            with tab_azo_miss:
                if res["missing_azos"]:
                    st.warning(f"⚠️ Drive တွင် မရှိသေးသော AZO Reports များ: **{len(res['missing_azos'])}** ခု")
                    st.dataframe(res["df_missing_azo"], width="stretch", hide_index=True)
                else:
                    st.success("✅ လိုအပ်သော AZO Report ဖိုင်များအားလုံး Drive တွင် ရှိပြီးဖြစ်ပါသည်။")
                    
            with tab_azo_exp:
                if res["expiring_azos"]:
                    st.warning(f"⚠️ သက်တမ်းကုန်ခါနီး (သို့) ကုန်သွားသော AZO Reports များ: **{len(res['expiring_azos'])}** ခု")
                    st.dataframe(res["df_expiring_azo"], width="stretch", hide_index=True)
                else:
                    st.success("✅ သက်တမ်းကုန်ခါနီး AZO Report များ မရှိပါ။")
            
            if res["missing_excel"] or res["expiring_excel"]:
                st.divider()
                col_d1, col_d2 = st.columns(2)
                if res["missing_excel"]:
                    col_d1.download_button(
                        label="📥 Download Missing AZO (Excel)",
                        data=res["missing_excel"],
                        file_name=f"Missing_AZO_{res['clean_tod']}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width="stretch"
                    )
                if res["expiring_excel"]:
                    col_d2.download_button(
                        label="📥 Download Expiring AZO (Excel)",
                        data=res["expiring_excel"],
                        file_name=f"Expire_azo_report_{res['clean_tod']}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width="stretch"
                    )
