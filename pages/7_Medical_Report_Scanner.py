import hashlib

import streamlit as st

from auth.auth_manager import require_login
from database import db_manager
from utils.components import (
    set_page,
    render_navbar,
    render_user_bar,
    render_footer,
    section_header,
    render_stat_cards,
    risk_result_card,
)
from utils.risk_engine import predict_risk
from report_scanner import image_processing, ocr, report_parser, medical_summary
from report_scanner import database as scan_db

set_page("Medical Report Scanner", "🧾")
user = require_login()
render_navbar(active="Scanner")
render_user_bar(user)
scan_db.init_reports_table()

section_header(
    "AI-powered scanning",
    "Medical Report Scanner",
    "Upload a photo or PDF of your lab results — we'll read it automatically, "
    "pull out the key values, and get them ready for a risk prediction.",
)

QUALITATIVE_FIELDS = {"urine_protein", "ketones"}
REQUIRED_FOR_PREDICTION = {"systolic_bp", "diastolic_bp", "hemoglobin", "blood_sugar"}


def _file_signature(uploaded_file) -> str:
    return hashlib.md5(uploaded_file.getvalue()).hexdigest()


# -----------------------------------------------------------------------
# Upload
# -----------------------------------------------------------------------
with st.container(key="glass_scan_upload"):
    st.markdown("#### 📤 Upload Your Lab Report")
    st.caption("Drag & drop a JPG, JPEG, PNG, or PDF file below.")
    uploaded_file = st.file_uploader(
        "Upload report",
        type=["jpg", "jpeg", "png", "pdf"],
        label_visibility="collapsed",
    )

if uploaded_file is None:
    st.info("👆 Upload a lab report to get started. Your file stays tied to your account only.")
    render_footer()
    st.stop()

signature = _file_signature(uploaded_file)

# -----------------------------------------------------------------------
# Preview
# -----------------------------------------------------------------------
try:
    pages = image_processing.load_pages_from_upload(uploaded_file)
except image_processing.UnsupportedFileError as e:
    st.error(f"⚠️ {e}")
    render_footer()
    st.stop()
except Exception:
    st.error(
        "⚠️ We couldn't open this file. It may be corrupted or in an "
        "unsupported format — please try a different photo or PDF."
    )
    render_footer()
    st.stop()

with st.container(key="glass_scan_preview"):
    st.markdown("#### 🖼️ Preview")
    preview_cols = st.columns(min(len(pages), 3) or 1)
    for i, page in enumerate(pages[:3]):
        with preview_cols[i % len(preview_cols)]:
            st.image(page, use_container_width=True, caption=f"Page {i + 1}")
    if len(pages) > 3:
        st.caption(f"…and {len(pages) - 3} more page(s).")

# -----------------------------------------------------------------------
# Scan
# -----------------------------------------------------------------------
scan_col, _ = st.columns([1, 3])
with scan_col:
    scan_clicked = st.button("🔍 Scan Report", type="primary", use_container_width=True)

if scan_clicked or st.session_state.get("scan_signature") == signature:
    if st.session_state.get("scan_signature") != signature:
        # New file — run the full pipeline with visible progress.
        progress = st.progress(0, text="Reading file…")
        try:
            pdf_text_layer = ""
            if (uploaded_file.name or "").lower().endswith(".pdf"):
                pdf_text_layer = image_processing.extract_pdf_text_layer(uploaded_file.getvalue())

            progress.progress(25, text="Enhancing image quality…")

            if pdf_text_layer and len(pdf_text_layer) > 30:
                # The PDF already has a text layer — skip OCR entirely for
                # a faster, near-perfect read.
                ocr_result = ocr.OCRResult(
                    text=pdf_text_layer, confidence=99.0, engine="PDF Text Layer", success=True
                )
                progress.progress(80, text="Reading text…")
            else:
                progress.progress(40, text="Running OCR (this can take a moment)…")
                processed_pages = [image_processing.preprocess_for_ocr(p) for p in pages]
                ocr_result = ocr.run_ocr_on_pages(processed_pages)
                progress.progress(80, text="Extracting medical values…")

            if not ocr_result.success:
                progress.empty()
                st.error(
                    "⚠️ We couldn't read any text from this report — it may be "
                    "too blurry, too dark, or rotated. Try retaking the photo "
                    "in better lighting, holding the camera flat over the page."
                )
                render_footer()
                st.stop()

            extracted = report_parser.parse_report(ocr_result.text)
            st.write("OCR Text:")
            st.text(ocr_result.text)

            st.write("Extracted Values:")
            st.write(extracted)
            missing = report_parser.missing_fields(extracted)

            file_path = scan_db.save_uploaded_file(user["id"], uploaded_file.name, uploaded_file.getvalue())
            plain_values = {k: v.value for k, v in extracted.items()}
            summary_lines, flags = medical_summary.build_summary(plain_values)

            report_id = scan_db.save_report(
                user_id=user["id"],
                file_name=uploaded_file.name,
                file_path=file_path,
                ocr_engine=ocr_result.engine,
                ocr_confidence=ocr_result.confidence,
                ocr_text=ocr_result.text,
                extracted_values={k: v.value for k, v in extracted.items()},
                missing_fields=missing,
                ai_summary=summary_lines,
            )

            progress.progress(100, text="Done!")
            progress.empty()

            st.session_state.scan_signature = signature
            st.session_state.scan_report_id = report_id
            st.session_state.scan_ocr_result = ocr_result
            st.session_state.scan_extracted = extracted
            st.session_state.scan_missing = missing
            st.session_state.scan_summary = summary_lines
            st.session_state.scan_flags = flags
            st.success("✅ Report scanned successfully!")
        except Exception as exc:
            progress.empty()
            st.error(
                "⚠️ Something went wrong while scanning this report. Please "
                f"try again with a clearer photo or a different file. ({exc})"
            )
            render_footer()
            st.stop()

    # -------------------------------------------------------------
    # Results — pulled from session_state so edits persist across reruns
    # -------------------------------------------------------------
    ocr_result = st.session_state.scan_ocr_result
    extracted = st.session_state.scan_extracted
    missing = st.session_state.scan_missing
    summary_lines = st.session_state.scan_summary
    flags = st.session_state.scan_flags
    report_id = st.session_state.scan_report_id

    # OCR quality metrics
    with st.container(key="glass_scan_quality"):
        st.markdown("#### 📊 Scan Quality")
        render_stat_cards([
            ("🔎", "OCR Engine", ocr_result.engine),
            ("📈", "OCR Confidence", f"{ocr_result.confidence:.0f}%"),
            ("✅", "Fields Detected", f"{len(extracted)}/{len(report_parser.CANONICAL_FIELDS)}"),
            ("❓", "Missing Fields", str(len(missing))),
        ])
        if ocr_result.confidence < 60:
            st.warning(
                "⚠️ OCR confidence is low — the scan may have missed or "
                "misread some values. Please double-check every field below "
                "before running a prediction."
            )
        if ocr_result.error:
            st.caption(f"ℹ️ {ocr_result.error}")

        with st.expander("View raw extracted text"):
            st.text(ocr_result.text or "(no text detected)")

    # Editable value cards
    with st.container(key="glass_scan_values"):
        st.markdown("#### ✏️ Extracted Values — review & edit before predicting")
        edited_values = {}
        field_cols = st.columns(3)
        for i, field in enumerate(report_parser.CANONICAL_FIELDS):
            label = report_parser.FIELD_LABELS[field]
            unit = report_parser.FIELD_UNITS[field]
            found = extracted.get(field)
            input_key = f"scan_value_{field}"

            with field_cols[i % 3]:
                if field in QUALITATIVE_FIELDS:
                    default_val = str(found.value) if found else ""
                    val = st.text_input(f"{label}", value=st.session_state.get(input_key, default_val), key=input_key)
                    try:
                        edited_values[field] = float(val)
                    except (TypeError, ValueError):
                        edited_values[field] = val or None
                else:
                    default_val = float(found.value) if found else 0.0
                    val = st.number_input(
                        f"{label} ({unit})" if unit else label,
                        value=float(st.session_state.get(input_key, default_val)),
                        key=input_key,
                        step=1.0,
                    )
                    edited_values[field] = val

                if not found:
                    st.caption("⚠️ Not detected — please enter manually")

    # AI summary card
    with st.container(key="glass_scan_summary"):
        st.markdown("#### 🩺 AI Summary")
        severity_icon = {"info": "ℹ️", "warning": "⚠️", "danger": "🚨"}
        for flag in flags:
            icon = severity_icon.get(flag.severity, "ℹ️")
            if flag.severity == "danger":
                st.error(f"{icon} {flag.message}")
            elif flag.severity == "warning":
                st.warning(f"{icon} {flag.message}")
            else:
                st.info(f"{icon} {flag.message}")
        if not flags:
            st.success("🎉 " + summary_lines[0])
        st.caption(summary_lines[-1])

    # -------------------------------------------------------------
    # Risk prediction integration
    # -------------------------------------------------------------
    with st.container(key="glass_scan_predict"):
        st.markdown("#### 🤖 Use These Results for Risk Prediction")

        missing_required = [
            report_parser.FIELD_LABELS[f] for f in REQUIRED_FOR_PREDICTION
            if not edited_values.get(f)
        ]
        if missing_required:
            st.caption(
                "Required for prediction: " + ", ".join(
                    report_parser.FIELD_LABELS[f] for f in REQUIRED_FOR_PREDICTION
                )
            )

        st.markdown("###### A few extra details the lab report doesn't include")
        extra_cols = st.columns(4)
        with extra_cols[0]:
            age = st.number_input("Age", 15, 55, int(edited_values.get("age") or 25), key="scan_age_extra")
        with extra_cols[1]:
            gravidity = st.number_input("Gravidity", 1, 15, 1, key="scan_gravidity_extra")
        with extra_cols[2]:
            parity = st.number_input("Parity", 0, 15, 0, key="scan_parity_extra")
        with extra_cols[3]:
            anc = st.number_input("ANC Visits", 0, 20, 4, key="scan_anc_extra")

        predict_disabled = bool(missing_required)
        if st.button(
            "🔮 Use These Results for Risk Prediction",
            type="primary",
            use_container_width=True,
            disabled=predict_disabled,
        ):
            bmi = edited_values.get("bmi") or 24.5
            gestational_age = edited_values.get("gestational_week") or st.session_state.get(
                "current_pregnancy_week", 20
            )
            hemoglobin = edited_values.get("hemoglobin") or 12.0
            anemia = 1 if hemoglobin < 11.0 else 0
            urine_protein_val = edited_values.get("urine_protein")
            proteinuria = 1 if (isinstance(urine_protein_val, (int, float)) and urine_protein_val > 0) else 0

            features = {
                "age": age,
                "gravidity": gravidity,
                "parity": parity,
                "gestational_age": gestational_age,
                "bmi": bmi,
                "systolic": edited_values.get("systolic_bp") or 120,
                "diastolic": edited_values.get("diastolic_bp") or 80,
                "hemoglobin": hemoglobin,
                "glucose": edited_values.get("blood_sugar") or 90,
                "anc": anc,
                "proteinuria": proteinuria,
                "hiv": 0,
                "anemia": anemia,
            }

            result = predict_risk(features)

            risk_result_card(
                level=result["level_key"],
                confidence=result["confidence"],
                title=result["label"],
                sub="Based on the values extracted from your uploaded lab report.",
            )

            if result["prediction"] == 0:
                st.success(result["recommendation"])
            elif result["prediction"] == 1:
                st.warning(result["recommendation"])
            else:
                st.error(result["recommendation"])

            # Save to the main Pregnancy History...
            db_manager.save_prediction(
                user_id=user["id"],
                age=age,
                systolic_bp=int(features["systolic"]),
                diastolic_bp=int(features["diastolic"]),
                blood_sugar=features["glucose"],
                body_temperature=edited_values.get("body_temperature") or 36.8,
                heart_rate=int(edited_values.get("heart_rate") or 80),
                predicted_risk=result["label"],
                risk_level=result["level_name"],
                confidence=result["confidence"],
                recommendation=result["recommendation"],
            )
            # ...and link the outcome back to this scanned report.
            scan_db.update_report_prediction(
                report_id, result["label"], result["confidence"], result["recommendation"]
            )
            st.success("📈 Saved to your Pregnancy History.")

    reset_col, _ = st.columns([1, 3])
    with reset_col:
        if st.button("🔄 Scan a Different Report", use_container_width=True):
            for k in (
                "scan_signature", "scan_report_id", "scan_ocr_result",
                "scan_extracted", "scan_missing", "scan_summary", "scan_flags",
            ):
                st.session_state.pop(k, None)
            st.rerun()

# -----------------------------------------------------------------------
# Past scans
# -----------------------------------------------------------------------
past_reports = scan_db.get_reports(user["id"])
if past_reports:
    with st.container(key="glass_scan_history"):
        st.markdown("#### 🗂️ Previously Scanned Reports")
        for r in past_reports[:10]:
            with st.expander(f"{r['created_at']} — {r['file_name']}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("OCR Confidence", f"{r['ocr_confidence']:.0f}%")
                c2.metric("Fields Found", len(r["extracted_values"]))
                c3.metric("Prediction", r["prediction_label"] or "—")
                if st.button("Delete this report", key=f"del_report_{r['id']}"):
                    scan_db.delete_report(r["id"], user["id"])
                    st.rerun()

render_footer()
