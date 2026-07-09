"""
OCR engine for the Medical Report Scanner.

Tries engines in order of quality and only falls back when the
preferred one is unavailable or fails at runtime:

    1. EasyOCR    (preferred — better on real-world phone photos)
    2. Tesseract  (fallback — lighter weight, no GPU/large model needed)

Both engines are imported lazily so that an environment without EasyOCR
installed still runs the whole app fine; it just always uses Tesseract.
`st.cache_resource` is used to load the EasyOCR model once per server
process rather than on every scan (loading it is slow).
"""

from dataclasses import dataclass, field
import numpy as np
import streamlit as st
from PIL import Image


@dataclass
class OCRResult:
    text: str
    confidence: float  # 0-100
    engine: str
    success: bool
    error: str = ""
    per_line: list = field(default_factory=list)  # [(text, confidence), ...]


@st.cache_resource(show_spinner=False)
def _get_easyocr_reader():
    import easyocr

    return easyocr.Reader(["en"], gpu=False, verbose=False)


def _run_easyocr(pil_img: Image.Image) -> OCRResult:
    reader = _get_easyocr_reader()
    results = reader.readtext(np.array(pil_img))

    if not results:
        return OCRResult(text="", confidence=0.0, engine="EasyOCR", success=True)

    lines, confidences = [], []
    for _, text, conf in results:
        lines.append(text)
        confidences.append(conf * 100)

    return OCRResult(
        text="\n".join(lines),
        confidence=sum(confidences) / len(confidences),
        engine="EasyOCR",
        success=True,
        per_line=list(zip(lines, confidences)),
    )


def _run_tesseract(pil_img: Image.Image) -> OCRResult:
    import pytesseract
    from pytesseract import Output

    data = pytesseract.image_to_data(pil_img, output_type=Output.DICT)

    lines, confidences = [], []
    for text, conf in zip(data["text"], data["conf"]):
        text = text.strip()
        conf = float(conf)
        if text and conf >= 0:
            lines.append(text)
            confidences.append(conf)

    full_text = pytesseract.image_to_string(pil_img)
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    return OCRResult(
        text=full_text.strip(),
        confidence=avg_conf,
        engine="Tesseract",
        success=True,
        per_line=list(zip(lines, confidences)),
    )


def run_ocr_on_image(pil_img: Image.Image) -> OCRResult:
    """
    Run OCR on a single preprocessed page image, preferring EasyOCR and
    transparently falling back to Tesseract if EasyOCR isn't installed
    or raises at runtime (corrupt model cache, unsupported platform, etc).
    """
    try:
        return _run_easyocr(pil_img)
    except Exception as easyocr_error:
        try:
            result = _run_tesseract(pil_img)
            result.error = f"(EasyOCR unavailable: {easyocr_error}; used Tesseract instead)"
            return result
        except Exception as tesseract_error:
            return OCRResult(
                text="",
                confidence=0.0,
                engine="none",
                success=False,
                error=(
                    "Both OCR engines failed — EasyOCR: "
                    f"{easyocr_error}; Tesseract: {tesseract_error}"
                ),
            )


def run_ocr_on_pages(pages: list) -> OCRResult:
    """
    Run OCR across every page image and merge the results into one
    OCRResult (confidence is the average across pages with any detected
    text).
    """
    if not pages:
        return OCRResult(text="", confidence=0.0, engine="none", success=False,
                          error="No pages to scan.")

    all_text, confidences, engines_used, per_line = [], [], set(), []
    any_success = False

    for page in pages:
        result = run_ocr_on_image(page)
        if result.success:
            any_success = True
            if result.text:
                all_text.append(result.text)
                confidences.append(result.confidence)
            engines_used.add(result.engine)
            per_line.extend(result.per_line)

    if not any_success:
        return OCRResult(
            text="", confidence=0.0, engine="none", success=False,
            error="OCR failed on every page of this document.",
        )

    return OCRResult(
        text="\n".join(all_text),
        confidence=(sum(confidences) / len(confidences)) if confidences else 0.0,
        engine="+".join(sorted(engines_used)) if engines_used else "none",
        success=True,
        per_line=per_line,
    )
