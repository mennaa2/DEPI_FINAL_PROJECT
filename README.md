# Maternal Care Platform

An AI-powered maternal health platform built with Streamlit: machine-learning
risk prediction, pregnancy tracking, an AI assistant, and now full user
accounts with a persistent pregnancy history.

## What's new

This update adds a full authentication system and data-persistence layer on
top of the original app, **without changing the existing ML model, tracker
math, health-tips content, or visual design.**

1. **Login & Sign Up** (`auth/auth_manager.py`) — email/password accounts
   stored in SQLite, passwords hashed with `bcrypt`, session kept in
   `st.session_state` until the user logs out. Every page is gated behind
   `require_login()`.
2. **Pregnancy History** (`pages/6_Pregnancy_History.py`) — every prediction
   you run is saved automatically (date, vitals, predicted risk, AI
   recommendation). Search, filter by risk level/date, sort, delete records,
   export to CSV, and view Plotly charts of your risk distribution and blood
   pressure trend over time.
3. **Smarter AI Assistant** (`ai_assistant/`) — a much larger knowledge base
   (30+ topics: symptoms, nutrition, baby development, medical risk factors,
   lifestyle, postpartum) with fuzzy keyword matching so it understands
   different phrasings of the same question, plus emergency-keyword
   detection. Conversations are saved per-user.
4. **Personal Dashboard** (`app.py`) — welcome message, today's date, current
   pregnancy week (if you've used the Tracker), quick stat cards, your most
   recent prediction, and a summary of your last AI conversation, shown above
   the existing marketing homepage.
5. **Medical Report Scanner** (`pages/7_Medical_Report_Scanner.py`,
   `report_scanner/`) — upload a photo or PDF of a lab report; the app
   cleans up the image, reads it with OCR, extracts medical values with
   regex-based parsing (tolerant of different labs' wording/abbreviations),
   shows an editable review + plain-language AI summary, and can feed the
   results straight into the risk-prediction model. See "Medical Report
   Scanner" below for details.
6. **SQLite database** (`database/db_manager.py`) — a single
   `data/maternal_care.db` file holding `users`, `predictions`, and
   `chat_messages` tables, created automatically on first run.

## Medical Report Scanner

Upload a JPG/JPEG/PNG photo or a PDF of a lab report and the scanner will:

1. **Clean up the image** (`report_scanner/image_processing.py`) —
   auto-rotate, denoise, boost contrast, sharpen, and best-effort crop to
   the document boundary. PDFs are rendered page-by-page; if a PDF already
   has a text layer (not a scanned image), that's read directly instead of
   running OCR at all — faster and more accurate.
2. **Read the text** (`report_scanner/ocr.py`) — tries EasyOCR first;
   if it isn't installed or fails at runtime, transparently falls back to
   Tesseract. Both are optional at the Python-import level, so the rest of
   the app keeps working even if one OCR engine isn't available in a given
   environment.
3. **Extract medical values** (`report_scanner/report_parser.py`) — regex
   patterns per field tolerate different labs' abbreviations and
   separators (`BP 130/85`, `SBP 130` / `DBP 85`, `Glucose = 120`,
   `GLU ..... 120`, `FBS 110`, `Hb 10.5`, `+2` / `2+` for urine
   protein/ketones, etc).
4. **Summarize in plain language** (`report_scanner/medical_summary.py`) —
   e.g. "High blood sugar detected," "Blood pressure appears elevated,"
   always ending with a reminder to confirm with a healthcare provider.
5. **Let you review and fix values** — every field is shown in an editable
   box, pre-filled when detected and clearly marked "Not detected — please
   enter manually" when it isn't, so nothing gets fed into the model
   without a chance to check it first.
6. **Run the same risk-prediction model** used on the main Prediction page
   (via `utils/risk_engine.py`, sharing the exact feature schema) and save
   the outcome to your Pregnancy History.
7. **Save everything** (`report_scanner/database.py`) — the uploaded file,
   OCR text, OCR engine + confidence, extracted values, missing fields, AI
   summary, and prediction result, all tied to your account in the same
   SQLite database.

## Project structure

```
Maternal_Care/
├── app.py                      # Home page + personal dashboard
├── auth/
│   └── auth_manager.py         # Login / Sign Up UI, hashing, session mgmt
├── database/
│   └── db_manager.py           # All core SQLite reads/writes
├── report_scanner/
│   ├── image_processing.py     # Upload loading + image cleanup pipeline
│   ├── ocr.py                  # EasyOCR (preferred) / Tesseract (fallback)
│   ├── report_parser.py        # Regex-based medical value extraction
│   ├── medical_summary.py      # Plain-language summary + flags
│   └── database.py             # Scanned-report persistence
├── ai_assistant/
│   ├── knowledge_base.py       # Topic → keywords → answer content
│   └── assistant.py            # Keyword/fuzzy matching ("retrieval")
├── utils/
│   ├── components.py           # Shared UI (navbar, footer, cards, etc.)
│   ├── risk_engine.py          # Shared model loader/predictor (Scanner only)
│   └── style.py                # Backward-compatible re-export
├── pages/
│   ├── 1_Risk_Prediction.py    # Same model + inputs, now saves to history
│   ├── 2_Pregnancy_Tracker.py  # Same date/week math, now shared with Dashboard
│   ├── 3_Health_Tips.py        # Unchanged content
│   ├── 4_AI_Assistant.py       # New knowledge base, persisted chat
│   ├── 5_About.py              # Unchanged content
│   ├── 6_Pregnancy_History.py  # Searchable history + charts
│   └── 7_Medical_Report_Scanner.py  # NEW — OCR lab-report scanner
├── assets/style.css            # Unchanged design system (+ small additions)
├── models/                     # Unchanged ML model + scaler
└── data/
    ├── maternal_care.db        # Created automatically on first run
    └── uploaded_reports/       # Saved copies of scanned lab reports
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The first time you run the app, `data/maternal_care.db` is created
automatically. Sign up for an account, then use the app as normal — every
prediction and AI conversation is now saved to your account.

## New dependencies

- `bcrypt` — password hashing for the authentication system
- `plotly` — charts on the Pregnancy History page
- `easyocr`, `pytesseract` — OCR engines for the Medical Report Scanner
  (EasyOCR preferred, Tesseract as fallback)
- `opencv-python-headless`, `pillow`, `numpy` — image preprocessing
- `pymupdf`, `pdf2image` — PDF page rendering / text-layer extraction

Tesseract also needs the system binary installed (`apt install
tesseract-ocr` on Debian/Ubuntu, `brew install tesseract` on macOS) —
`pytesseract` is just a Python wrapper around it.

## Notes & limitations

- Login sessions use `st.session_state`, so you stay logged in for the
  duration of your browser session (per the requested design). Restarting
  the Streamlit server or opening a new browser session will require
  logging in again — a "remember me across restarts" option would need a
  persistent cookie library (e.g. `streamlit-cookies-manager`), which is a
  reasonable next enhancement but outside this update's scope.
- The AI Assistant uses a fast, dependency-free keyword + fuzzy-matching
  retrieval system rather than a hosted embeddings/vector-database RAG
  pipeline, so it can run fully offline with no API keys.
- The Risk Prediction model, its input columns, and its `predict()` /
  `predict_proba()` calls are byte-for-byte the same as before. Body
  Temperature and Heart Rate are new *optional logging fields* only — they
  are saved to your history but are not fed into the model.
- The Medical Report Scanner's field extraction is regex/keyword-based
  rather than a trained NLP model, so it stays fast and fully offline —
  but very unusual report layouts may still need manual entry, which is
  why every extracted field is editable and missing fields are clearly
  flagged before prediction.
- Fields the model needs but a lab report wouldn't normally contain
  (gravidity, parity, ANC visit count, HIV status) are collected via a
  few small extra inputs on the Scanner page itself, defaulting to
  typical values you can adjust.

## Notes on navigation

Streamlit multipage apps route between pages via full page loads, so the
top navbar uses real `st.page_link` navigation (sticky, pill-styled) for
Prediction / Tracker / History / Scanner / AI Assistant / Health Tips /
About, and an in-page anchor for "Features" on the home page.
