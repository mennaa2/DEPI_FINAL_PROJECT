"""
Medical value extraction for the Report Scanner.

Lab reports vary wildly in layout between providers — this module does
NOT try to match an exact template. Instead, for every canonical field
we keep a list of regex patterns covering the common abbreviations and
separators (":", "-", "=", "....", plain whitespace) so values are
found regardless of exact wording, e.g. all of the following resolve
to the same field:

    Blood Sugar: 120 mg/dL
    Glucose = 120
    GLU ..... 120
    FBS 110
    Random Blood Sugar 135

This is intentionally a lightweight, dependency-free "NLP-lite"
approach (regex + keyword aliasing) rather than a full statistical NER
model, which keeps the scanner fast and fully offline.
"""

import re
from dataclasses import dataclass

# Separator between a label and its value: colon, dash, equals, dots,
# or plain spaces/tabs — explicitly NOT newlines, so we never jump from
# a label on one line to an unrelated number on the next.
SEP = r"[\s:\-=\.]{0,50}"
NUM = r"(\d{1,4}(?:\.\d+)?)"


@dataclass
class ExtractedField:
    label: str          # human-readable label, e.g. "Systolic BP"
    value: float | str  # numeric value, or qualitative string (e.g. "Trace")
    unit: str
    raw_match: str


# -----------------------------------------------------------------------
# Canonical fields shown in the UI, in display order.
# -----------------------------------------------------------------------
CANONICAL_FIELDS = [
    "systolic_bp", "diastolic_bp", "heart_rate", "body_temperature",
    "blood_sugar", "hemoglobin", "rbc", "wbc", "platelets", "hematocrit",
    "cholesterol", "urine_protein", "ketones", "bmi", "age",
    "gestational_week",
]

FIELD_LABELS = {
    "systolic_bp": "Systolic BP",
    "diastolic_bp": "Diastolic BP",
    "heart_rate": "Heart Rate",
    "body_temperature": "Body Temperature",
    "blood_sugar": "Blood Sugar / Glucose",
    "hemoglobin": "Hemoglobin",
    "rbc": "RBC",
    "wbc": "WBC",
    "platelets": "Platelets",
    "hematocrit": "Hematocrit",
    "cholesterol": "Cholesterol",
    "urine_protein": "Urine Protein",
    "ketones": "Ketones",
    "bmi": "BMI",
    "age": "Age",
    "gestational_week": "Gestational Week",
}

FIELD_UNITS = {
    "systolic_bp": "mmHg", "diastolic_bp": "mmHg", "heart_rate": "bpm",
    "body_temperature": "°C", "blood_sugar": "mg/dL", "hemoglobin": "g/dL",
    "rbc": "million/µL", "wbc": "/µL", "platelets": "/µL",
    "hematocrit": "%", "cholesterol": "mg/dL", "urine_protein": "",
    "ketones": "", "bmi": "kg/m²", "age": "years", "gestational_week": "weeks",
}

QUALITATIVE_MAP = {
    "negative": 0, "neg": 0, "nil": 0, "none": 0, "trace": 0.5,
    "1+": 1, "+1": 1, "2+": 2, "+2": 2, "3+": 3, "+3": 3, "4+": 4, "+4": 4,
    "+": 1, "++": 2, "+++": 3,
}


def _first_match(patterns: list, text: str):
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m
    return None


# -----------------------------------------------------------------------
# Field-specific patterns
# -----------------------------------------------------------------------
def _extract_blood_pressure(text: str) -> dict:
    out = {}

    # BP: 120/80
    m = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", text)
    if m:
        out["systolic_bp"] = ExtractedField(
            FIELD_LABELS["systolic_bp"], float(m.group(1)),
            FIELD_UNITS["systolic_bp"], m.group(0)
        )
        out["diastolic_bp"] = ExtractedField(
            FIELD_LABELS["diastolic_bp"], float(m.group(2)),
            FIELD_UNITS["diastolic_bp"], m.group(0)
        )
        return out

    # Systolic BP: 120
    m = re.search(r"Systolic\s*BP[\s:\n]+(\d+)", text, re.I)
    if m:
        out["systolic_bp"] = ExtractedField(
            FIELD_LABELS["systolic_bp"], float(m.group(1)),
            FIELD_UNITS["systolic_bp"], m.group(0)
        )

    # Diastolic BP: 80
    m = re.search(r"Diastolic\s*BP[\s:\n]+(\d+)", text, re.I)
    if m:
        out["diastolic_bp"] = ExtractedField(
            FIELD_LABELS["diastolic_bp"], float(m.group(1)),
            FIELD_UNITS["diastolic_bp"], m.group(0)
        )

    return out
    """Handles combined 'BP 120/80' as well as separate SBP/DBP mentions."""
    out = {}

    combined_patterns = [
        rf"(?:blood\s*pressure|b\.?p\.?)\s*{SEP}{NUM}\s*/\s*{NUM}",
    ]
    m = _first_match(combined_patterns, text)
    if m:
        out["systolic_bp"] = ExtractedField(
            FIELD_LABELS["systolic_bp"], float(m.group(1)), FIELD_UNITS["systolic_bp"], m.group(0)
        )
        out["diastolic_bp"] = ExtractedField(
            FIELD_LABELS["diastolic_bp"], float(m.group(2)), FIELD_UNITS["diastolic_bp"], m.group(0)
        )
        return out

    # Bare "120/80 mmHg" without an explicit BP label nearby.
    m = re.search(rf"\b{NUM}\s*/\s*{NUM}\s*mm\s*hg\b", text, re.IGNORECASE)
    if m:
        out["systolic_bp"] = ExtractedField(
            FIELD_LABELS["systolic_bp"], float(m.group(1)), FIELD_UNITS["systolic_bp"], m.group(0)
        )
        out["diastolic_bp"] = ExtractedField(
            FIELD_LABELS["diastolic_bp"], float(m.group(2)), FIELD_UNITS["diastolic_bp"], m.group(0)
        )
        return out

    sys_m = _first_match([rf"\b(?:sbp|systolic)\b{SEP}{NUM}"], text)
    if sys_m:
        out["systolic_bp"] = ExtractedField(
            FIELD_LABELS["systolic_bp"], float(sys_m.group(1)), FIELD_UNITS["systolic_bp"], sys_m.group(0)
        )

    dia_m = _first_match([rf"\b(?:dbp|diastolic)\b{SEP}{NUM}"], text)
    if dia_m:
        out["diastolic_bp"] = ExtractedField(
            FIELD_LABELS["diastolic_bp"], float(dia_m.group(1)), FIELD_UNITS["diastolic_bp"], dia_m.group(0)
        )

    return out


def _extract_blood_sugar(text: str) -> ExtractedField | None:
    """Prefers a labeled fasting/random reading, falls back to generic glucose."""
    labeled_patterns = [
        rf"\b(?:fbs|fasting\s*blood\s*sugar|fasting\s*glucose)\b{SEP}{NUM}",
        rf"\b(?:rbs|random\s*blood\s*sugar)\b{SEP}{NUM}",
    ]
    m = _first_match(labeled_patterns, text)
    if not m:
        m = _first_match(
            [rf"\b(?:glucose|glu|blood\s*sugar|sugar)\b{SEP}{NUM}"], text
        )
    if m:
        return ExtractedField(FIELD_LABELS["blood_sugar"], float(m.group(1)), FIELD_UNITS["blood_sugar"], m.group(0))
    return None


def _extract_simple_numeric(text: str, field: str, patterns: list) -> ExtractedField | None:
    m = _first_match(patterns, text)
    if m:
        return ExtractedField(FIELD_LABELS[field], float(m.group(1)), FIELD_UNITS[field], m.group(0))
    return None


def _extract_qualitative(text: str, field: str, patterns: list) -> ExtractedField | None:
    m = _first_match(patterns, text)
    if not m:
        return None
    raw_value = m.group(1).strip().lower().replace(" ", "")
    if raw_value in QUALITATIVE_MAP:
        value = QUALITATIVE_MAP[raw_value]
    else:
        try:
            value = float(raw_value)
        except ValueError:
            value = raw_value
    return ExtractedField(FIELD_LABELS[field], value, FIELD_UNITS[field], m.group(0))


# -----------------------------------------------------------------------
# Public entry point
# -----------------------------------------------------------------------
def parse_report(text: str) -> dict:
    """
    Extract every recognizable canonical field from raw OCR text.

    Returns {field_key: ExtractedField}. Fields not found are simply
    absent from the dict — callers should diff against
    `CANONICAL_FIELDS` to know what's missing.
    """
    if not text or not text.strip():
        return {}
    # Normalize OCR text
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    extracted = {}

    extracted.update(_extract_blood_pressure(text))

    sugar = _extract_blood_sugar(text)
    if sugar:
        extracted["blood_sugar"] = sugar

    simple_specs = {
        "heart_rate": [rf"\b(?:heart\s*rate|hr|pulse)\b{SEP}{NUM}"],
        "body_temperature": [rf"\b(?:temp(?:erature)?|body\s*temp(?:erature)?)\b{SEP}{NUM}"],
        "hemoglobin": [rf"\b(?:hemoglobin|haemoglobin|hgb|hb)\b{SEP}{NUM}"],
        "rbc": [rf"\b(?:rbc|red\s*blood\s*cells?)\b{SEP}{NUM}"],
        "wbc": [rf"\b(?:wbc|white\s*blood\s*cells?)\b{SEP}{NUM}"],
        "platelets": [ r"(?:platelets?|plt)[\s:\n]+(\d{4,7})"],        "hematocrit": [rf"\b(?:hematocrit|haematocrit|hct)\b{SEP}{NUM}"],
        "cholesterol": [rf"\b(?:cholesterol|chol)\b{SEP}{NUM}"],
        "bmi": [rf"\bbmi\b{SEP}{NUM}"],
        "age": [rf"\bage\b{SEP}(\d{{1,3}})\s*(?:years|yrs|y)?\b"],
        "gestational_week": [
        r"Gestational\s*Age[\s:\n]+(\d+)",
        r"Gestational\s*Week[\s:\n]+(\d+)",
        r"Pregnancy\s*Week[\s:\n]+(\d+)",
        r"GA[\s:\n]+(\d+)"
    ],
    }
    for field, patterns in simple_specs.items():
        found = _extract_simple_numeric(text, field, patterns)
        if found:
            extracted[field] = found

    qualitative_specs = {
        "urine_protein": [
            rf"\b(?:urine\s*protein|proteinuria|protein)\b{SEP}"
            rf"(\d\s*\+|\+\s*\d|[+\-]{{1,3}}|negative|trace|nil|{NUM})"
        ],
        "ketones": [
            rf"\bketones?\b{SEP}(\d\s*\+|\+\s*\d|[+\-]{{1,3}}|negative|trace|nil|{NUM})"
        ],
    }
    for field, patterns in qualitative_specs.items():
        found = _extract_qualitative(text, field, patterns)
        if found:
            extracted[field] = found

    return extracted


def missing_fields(extracted: dict) -> list:
    """Canonical fields that weren't found in this report."""
    return [f for f in CANONICAL_FIELDS if f not in extracted]
