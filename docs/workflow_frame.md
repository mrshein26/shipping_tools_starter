# Shipping Tools App Workflow Frame

## Main Idea

The new app should be built as small modules, not one large file. The user sees a simple Streamlit interface, while the processing logic stays in separate tool files.

## App Flow

```text
Login
  -> Check user role
  -> Show allowed tools
  -> User selects tool
  -> Upload files
  -> Validate file type and required templates
  -> Process files
  -> Show success and error report
  -> Download output
  -> Save activity log
```

## Tool Flow

```text
PDF / ZIP Upload
  -> Extract PDFs from ZIP
  -> Read PDF text
  -> Find PO, SKU, WH, destination, invoice data
  -> Process PDF or Excel
  -> Create output files
  -> Bundle output into ZIP if multiple files
  -> Show download button
```

## Recommended Build Phases

### Phase 1: Foundation

- Login
- User role
- Dashboard
- Activity log
- Secrets setup
- Assets and templates folders

### Phase 2: Common Services

- PDF and ZIP extractor
- Excel reader helper
- Google Drive service
- Discord alert service
- Error report builder

### Phase 3: Core Tools

- PDF Stamper
- Document Combiner
- Missing SKC and Care Label checker

### Phase 4: Form Generators

- NWPM
- Statement of Origin CA/DR
- DMAM JP
- Org Criterion IN/OI
- Cover Sheet
- Certificate of Origin CL

### Phase 5: Admin Tools

- Air Booking
- Remove and Combine
- Export Data
- Import RO Data
- REX Data
- License Balance
- Import Lists
- Export Summary

## Module Rule

Keep `app.py` small.

`app.py` should only:

- Start Streamlit
- Check login
- Show menu
- Call the selected tool module

Each tool file should:

- Render its own upload UI
- Validate inputs
- Call helper functions
- Return download results and error reports

## Security Rule

Never put these directly in code:

- Passwords
- Discord webhook URL
- Google service account JSON
- Gemini API key
- Google Drive folder IDs if they are private

Use Streamlit secrets or config files.

## First Stable Release

The first stable release should include only:

- Login
- PDF Stamper
- Document Combiner checker
- Activity log

After that is stable, add form generators and admin tools.
