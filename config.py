from pathlib import Path


APP_TITLE = "Teng Hui Shipping Tools"
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
TEMPLATES_DIR = ASSETS_DIR / "templates"
IMAGES_DIR = ASSETS_DIR / "images"
LOG_DIR = BASE_DIR / "data"
ACTIVITY_LOG = LOG_DIR / "activity_logs.csv"


TOOL_ACCESS = {
    "PDF Stamper": ["all"],
    "Extract Forms": ["all"],
    "Document Combiner": ["all"],
    "Air Docs Merge": ["admin"],
    "Admin Tools": ["admin"],
}


STAMP_FILES = {
    "Invoice": IMAGES_DIR / "stamp_invoice.png",
    "Packing List": IMAGES_DIR / "stamp_pl.png",
}


FORM_TEMPLATES = {
    "NWPM": TEMPLATES_DIR / "Declaration_Template.pdf",
    "CA_DR": TEMPLATES_DIR / "CA Template.pdf",
    "DMAM": TEMPLATES_DIR / "DMAM_Template.pdf",
    "ORG_CRITERION": TEMPLATES_DIR / "Originating Criterion (IN OI).pdf",
    "COVER_SHEET": TEMPLATES_DIR / "Cover_Sheet_Template.pdf",
    "CL_ORIGIN": TEMPLATES_DIR / "CERTIFICADO DE ORIGEN (CL).pdf",
}


GOOGLE_DRIVE_FOLDERS = {
    "SKC": "",
    "Carelabels": "",
    "Declaration of NWPM (CN)": "",
    "DMAM (JP)": "",
    "Org Criterion (IN)": "",
    "Statement of Origin (CA)": "",
    "Cover Sheets": "",
    "Certificate of Origin (CL)": "",
}
