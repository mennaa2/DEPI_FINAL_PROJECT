"""
Shared helper for running the maternal risk-prediction model.

`pages/1_Risk_Prediction.py` keeps its own inline copy of this logic
untouched (so the original wizard behavior is guaranteed not to change).
This module exists so the new Medical Report Scanner can run the exact
same model, on the exact same feature schema, without duplicating the
column-name bookkeeping in two places.
"""

import joblib
import pandas as pd
import streamlit as st

RISK_LABELS = {0: "🟢 Low Risk", 1: "🟡 Moderate Risk", 2: "🔴 High Risk"}
LEVEL_KEYS = {0: "low", 1: "medium", 2: "high"}
LEVEL_NAMES = {0: "Low", 1: "Moderate", 2: "High"}

RECOMMENDATIONS = {
    0: "Continue routine prenatal visits. Maintain healthy nutrition. "
       "Exercise regularly. Drink enough water.",
    1: "Increase prenatal monitoring. Track blood pressure. Follow "
       "medical advice. Maintain healthy weight.",
    2: "Seek immediate medical care. Monitor blood pressure daily. "
       "Attend all prenatal appointments. Follow physician "
       "recommendations.",
}


@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load("models/maternal_risk_model.pkl")


def predict_risk(features: dict) -> dict:
    """
    features must supply: age, gravidity, parity, gestational_age, bmi,
    systolic, diastolic, hemoglobin, glucose, anc, proteinuria, hiv, anemia
    — the same fields the Risk Prediction wizard collects.

    Returns a dict with the predicted class, label, confidence, and
    recommendation text.
    """
    model = load_model()

    bp_diff = features["systolic"] - features["diastolic"]
    input_data = pd.DataFrame([{
        "age_years": features["age"],
        "gravidity": features["gravidity"],
        "parity": features["parity"],
        "gestational_age_weeks": features["gestational_age"],
        "bmi_pre_pregnancy": features["bmi"],
        "systolic_bp_mmhg": features["systolic"],
        "diastolic_bp_mmhg": features["diastolic"],
        "hemoglobin_gdl": features["hemoglobin"],
        "anemia_status": features["anemia"],
        "fasting_glucose_mgdl": features["glucose"],
        "proteinuria": features["proteinuria"],
        "hiv_status": features["hiv"],
        "anc_visits": features["anc"],
        "bp_diff": bp_diff,
    }])

    prediction = int(model.predict(input_data)[0])

    confidence = None
    try:
        proba = model.predict_proba(input_data)[0]
        confidence = float(proba[prediction]) * 100
    except Exception:
        confidence = None

    return {
        "prediction": prediction,
        "label": RISK_LABELS[prediction],
        "level_key": LEVEL_KEYS[prediction],
        "level_name": LEVEL_NAMES[prediction],
        "confidence": confidence,
        "recommendation": RECOMMENDATIONS[prediction],
    }
