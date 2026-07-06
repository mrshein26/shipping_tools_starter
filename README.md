# Teng Hui Shipping Tools Starter

This is a clean Streamlit starter for rebuilding the existing shipping tools app in a maintainable way.

## First Version Scope

- Login and role-based menu
- Activity log
- PDF Stamper working module
- Document Combiner checker frame
- Extract Forms frame
- Air Docs Merge frame
- Admin Tools frame

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

For local secrets:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Then edit `.streamlit/secrets.toml`.

## Run as a Web App

Use GitHub + Streamlit Community Cloud. See [DEPLOYMENT.md](DEPLOYMENT.md).

## Required Assets

Put these files in `assets/images/`:

- `TH Logo.png`
- `stamp_invoice.png`
- `stamp_pl.png`

Put these files in `assets/templates/`:

- `Declaration_Template.pdf`
- `CA Template.pdf`
- `DMAM_Template.pdf`
- `Originating Criterion (IN OI).pdf`
- `Cover_Sheet_Template.pdf`
- `CERTIFICADO DE ORIGEN (CL).pdf`

## Build Order

1. Confirm login and dashboard.
2. Add stamp images and test PDF Stamper.
3. Configure Google Drive folder IDs in `config.py`.
4. Finish Document Combiner merge engine.
5. Move Extract Forms tools one by one.
6. Move Admin Tools one by one.
