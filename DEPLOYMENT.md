# Streamlit + GitHub Deployment Guide

ဒီ app ကို local စက်ထဲမှာ run မထားချင်ရင် GitHub ပေါ်တင်ပြီး Streamlit Community Cloud ကနေ web app အဖြစ် run လုပ်ပါ။

## 1. GitHub Repository

GitHub မှာ repository အသစ်တစ်ခုလုပ်ပါ။

ဥပမာ:

```text
shipping-tools-app
```

ဒီ folder ထဲက file/folder အားလုံးကို GitHub repo root ထဲတင်ပါ:

```text
shipping_tools_starter/
  app.py
  auth.py
  config.py
  requirements.txt
  packages.txt
  .gitignore
  .streamlit/
    secrets.toml.example
  assets/
  services/
  tools/
  ui/
```

အရေးကြီးတာက GitHub repo root မှာ `app.py`, `requirements.txt`, `packages.txt` ရှိရပါမယ်။

## 2. Assets

PDF Stamper အတွက် ဒီ files တွေကို GitHub repo ထဲက `assets/images/` ထဲတင်ပါ:

```text
assets/images/stamp_invoice.png
assets/images/stamp_pl.png
assets/images/TH Logo.png
```

Form generator တွေအတွက် template PDFs တွေကို `assets/templates/` ထဲတင်ပါ:

```text
assets/templates/Declaration_Template.pdf
assets/templates/CA Template.pdf
assets/templates/DMAM_Template.pdf
assets/templates/Originating Criterion (IN OI).pdf
assets/templates/Cover_Sheet_Template.pdf
assets/templates/CERTIFICADO DE ORIGEN (CL).pdf
```

## 3. Secrets

`.streamlit/secrets.toml` ကို GitHub ထဲ မတင်ရပါ။

GitHub ထဲမှာ example file ပဲထားပါ:

```text
.streamlit/secrets.toml.example
```

Streamlit Community Cloud deploy လုပ်တဲ့အချိန်မှာ `Advanced settings` ထဲက `Secrets` field မှာ real secrets တွေ paste လုပ်ပါ။

Example:

```toml
DISCORD_WEBHOOK_URL = ""
GEMINI_API_KEY = ""

[passwords]
admin = "your-admin-password"
sheinmon = "your-user-password"

[gcp_service_account]
type = "service_account"
project_id = ""
private_key_id = ""
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = ""
client_id = ""
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = ""
```

## 4. Streamlit Community Cloud

1. Go to `https://share.streamlit.io`
2. Click `Create app`
3. Choose `Yup, I have an app`
4. Select your GitHub repository
5. Select branch: `main`
6. Main file path: `app.py`
7. Open `Advanced settings`
8. Paste secrets
9. Choose Python version, preferably `3.12`
10. Click `Deploy`

Deploy ပြီးရင် app URL က ဒီလိုပုံစံနဲ့ရပါမယ်:

```text
https://your-app-name.streamlit.app
```

## 5. Update Workflow

နောက်ပိုင်း code ပြင်ချင်ရင်:

```text
Edit code
  -> Push to GitHub
  -> Streamlit Cloud auto redeploys
  -> Web app updates
```

## 6. Important Notes

- Passwords, Google service account, Discord webhook, Gemini API key ကို GitHub ထဲ မတင်ရပါ။
- `requirements.txt` က Python libraries တွေ install လုပ်ဖို့ပါ။
- `packages.txt` က Linux system packages တွေ install လုပ်ဖို့ပါ။
- OCR သုံးမယ်ဆိုရင် `packages.txt` ထဲက `tesseract-ocr` လိုပါတယ်။
- `pdf2image` သုံးမယ်ဆိုရင် `poppler-utils` လိုပါတယ်။
