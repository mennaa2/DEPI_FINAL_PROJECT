"""
Turns extracted lab values into a short, plain-language summary that a
pregnant patient — not a clinician — can understand at a glance.

This is deliberately rule-based (simple threshold checks against normal
pregnancy ranges) rather than diagnostic: it flags values worth a
conversation with a provider, it never states a diagnosis.
"""

from dataclasses import dataclass

# Reference ranges used purely to decide what to flag — NOT a diagnosis.
# Sources: general prenatal-care guidelines; always conservative (flag
# rather than miss something worth a provider's attention).
NORMAL_RANGES = {
    "systolic_bp": (90, 139),
    "diastolic_bp": (60, 89),
    "heart_rate": (60, 100),
    "body_temperature": (36.1, 37.5),
    "blood_sugar": (70, 139),
    "hemoglobin": (11.0, 15.0),
    "platelets": (150, 450),
    "wbc": (4000, 11000),
    "hematocrit": (33, 45),
}


@dataclass
class SummaryFlag:
    field: str
    label: str
    message: str
    severity: str  # "info" | "warning" | "danger"


def _flag_numeric(field: str, label: str, value: float, low_msg: str, high_msg: str, severity="warning"):
    if field not in NORMAL_RANGES:
        return None
    low, high = NORMAL_RANGES[field]
    if value < low:
        return SummaryFlag(field, label, low_msg, severity)
    if value > high:
        return SummaryFlag(field, label, high_msg, severity)
    return None


def build_summary(values: dict) -> tuple:
    """
    values: {field_key: numeric_or_qualitative_value} — plain values,
    not ExtractedField objects (callers should unwrap `.value` first).

    Returns (summary_lines: list[str], flags: list[SummaryFlag]).
    """
    flags = []

    if "systolic_bp" in values or "diastolic_bp" in values:
        sys_v = values.get("systolic_bp")
        dia_v = values.get("diastolic_bp")
        elevated = (sys_v is not None and sys_v >= 140) or (dia_v is not None and dia_v >= 90)
        low = (sys_v is not None and sys_v < 90) or (dia_v is not None and dia_v < 60)
        if elevated:
            flags.append(SummaryFlag(
                "blood_pressure", "Blood Pressure",
                "Your blood pressure appears elevated — this can be significant during pregnancy.",
                "danger",
            ))
        elif low:
            flags.append(SummaryFlag(
                "blood_pressure", "Blood Pressure",
                "Your blood pressure appears lower than the typical range.",
                "warning",
            ))

    if "blood_sugar" in values:
        v = values["blood_sugar"]
        if v >= 140:
            flags.append(SummaryFlag(
                "blood_sugar", "Blood Sugar",
                "High blood sugar detected — this may need follow-up for gestational diabetes.",
                "danger",
            ))
        elif v < 70:
            flags.append(SummaryFlag(
                "blood_sugar", "Blood Sugar",
                "Your blood sugar appears lower than the typical range.",
                "warning",
            ))

    if "hemoglobin" in values:
        v = values["hemoglobin"]
        if v < 11.0:
            flags.append(SummaryFlag(
                "hemoglobin", "Hemoglobin",
                "Hemoglobin is below the normal range — this can indicate anemia in pregnancy.",
                "warning",
            ))

    if "heart_rate" in values:
        v = values["heart_rate"]
        f = _flag_numeric(
            "heart_rate", "Heart Rate", v,
            "Your heart rate appears lower than typical.",
            "Your heart rate appears higher than typical.",
        )
        if f:
            flags.append(f)

    if "body_temperature" in values:
        v = values["body_temperature"]
        if v >= 37.8:
            flags.append(SummaryFlag(
                "body_temperature", "Body Temperature",
                "A fever was detected — please contact your provider, especially in pregnancy.",
                "danger",
            ))

    if "urine_protein" in values:
        v = values["urine_protein"]
        if isinstance(v, (int, float)) and v > 0:
            flags.append(SummaryFlag(
                "urine_protein", "Urine Protein",
                "Protein was detected in your urine — this is sometimes linked to preeclampsia and is worth discussing with your provider.",
                "danger",
            ))

    if "ketones" in values:
        v = values["ketones"]
        if isinstance(v, (int, float)) and v > 0:
            flags.append(SummaryFlag(
                "ketones", "Ketones",
                "Ketones were detected in your urine, which can happen with dehydration or poor blood sugar control.",
                "warning",
            ))

    if "platelets" in values:
        v = values["platelets"]
        if v < 150:
            flags.append(SummaryFlag(
                "platelets", "Platelets",
                "Your platelet count is lower than typical.",
                "warning",
            ))

    if "wbc" in values:
        v = values["wbc"]
        if v > 11000:
            flags.append(SummaryFlag(
                "wbc", "WBC",
                "Your white blood cell count is higher than typical, which can indicate an infection.",
                "warning",
            ))

    if "hematocrit" in values:
        v = values["hematocrit"]
        if v < 33:
            flags.append(SummaryFlag(
                "hematocrit", "Hematocrit",
                "Your hematocrit is below the typical range.",
                "warning",
            ))

    if "cholesterol" in values:
        v = values["cholesterol"]
        if v > 240:
            flags.append(SummaryFlag(
                "cholesterol", "Cholesterol",
                "Your cholesterol appears higher than typical.",
                "info",
            ))

    summary_lines = [f.message for f in flags]
    if not summary_lines:
        summary_lines.append("All detected values appear to fall within typical ranges. 🎉")

    summary_lines.append(
        "This is an automated summary, not a diagnosis — please share this report "
        "with your healthcare provider."
    )

    return summary_lines, flags
