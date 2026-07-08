import streamlit as st
from auth.auth_manager import require_login
from utils.components import (
    set_page,
    render_navbar,
    render_user_bar,
    render_footer,
    section_header,
)

set_page("Health Tips", "❤️")
user = require_login()
render_navbar(active="Health Tips")
render_user_bar(user)

section_header(
    "Stay informed",
    "Health Tips & Risk Awareness",
    "Educational pregnancy health information based on common risk factors.",
)

# Content unchanged from the original app
conditions = {
    "High Blood Pressure": {
        "icon": "🩸",
        "risk": "High blood pressure during pregnancy may increase the risk of preeclampsia, preterm birth, and complications.",
        "tips": [
            "Monitor blood pressure regularly.",
            "Reduce salt intake.",
            "Drink enough water.",
            "Attend all prenatal visits.",
            "Take medications only if prescribed."
        ],
        "warning": [
            "Severe headache",
            "Blurred vision",
            "Swelling of face or hands",
            "Chest pain"
        ]
    },

    "Gestational Diabetes": {
        "icon": "🍬",
        "risk": "Gestational diabetes can affect both mother and baby if not monitored.",
        "tips": [
            "Maintain a balanced diet.",
            "Exercise regularly.",
            "Monitor blood sugar.",
            "Avoid sugary drinks.",
            "Follow doctor's advice."
        ],
        "warning": [
            "Excessive thirst",
            "Frequent urination",
            "Blurred vision"
        ]
    },

    "Anemia": {
        "icon": "🩹",
        "risk": "Low hemoglobin may reduce oxygen supply to mother and baby.",
        "tips": [
            "Eat iron-rich foods.",
            "Take iron supplements if prescribed.",
            "Include Vitamin C in meals.",
            "Attend follow-up blood tests."
        ],
        "warning": [
            "Extreme fatigue",
            "Shortness of breath",
            "Dizziness"
        ]
    },

    "Smoking": {
        "icon": "🚭",
        "risk": "Smoking increases miscarriage, low birth weight, and premature birth risk.",
        "tips": [
            "Stop smoking.",
            "Avoid passive smoking.",
            "Seek professional support.",
            "Maintain healthy nutrition."
        ],
        "warning": [
            "Reduced fetal movement",
            "Persistent bleeding",
            "Difficulty breathing"
        ]
    },

    "Obesity": {
        "icon": "⚖️",
        "risk": "Obesity may increase pregnancy complications including diabetes and hypertension.",
        "tips": [
            "Maintain healthy weight gain.",
            "Walk regularly.",
            "Eat balanced meals.",
            "Stay hydrated."
        ],
        "warning": [
            "High blood pressure",
            "Swelling",
            "Severe pain"
        ]
    },

    "Poor Nutrition": {
        "icon": "🥗",
        "risk": "Poor nutrition affects fetal growth and maternal health.",
        "tips": [
            "Eat fruits and vegetables.",
            "Consume enough protein.",
            "Take prenatal vitamins.",
            "Drink enough water."
        ],
        "warning": [
            "Rapid weight loss",
            "Persistent weakness",
            "Poor fetal growth"
        ]
    }
}

if "selected_condition" not in st.session_state:
    st.session_state.selected_condition = list(conditions.keys())[0]

# -------------------------
# Condition cards (replaces the plain selectbox)
# -------------------------
cols = st.columns(3)
for i, (name, data) in enumerate(conditions.items()):
    with cols[i % 3]:
        active = st.session_state.selected_condition == name
        if st.button(
            f"{data['icon']}  {name}",
            key=f"tip_btn_{name}",
            use_container_width=True,
        ):
            st.session_state.selected_condition = name
        if active:
            st.markdown(
                "<div style='text-align:center;margin-top:-8px;'>"
                "<span style='color:var(--accent);font-size:0.75rem;font-weight:700;'>● selected</span></div>",
                unsafe_allow_html=True,
            )

choice = st.session_state.selected_condition
data = conditions[choice]

st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

with st.container(key="glass_step"):
    st.markdown(f"### {data['icon']} {choice}")

    st.subheader("⚠️ Risk Awareness")
    st.warning(data["risk"])

    st.subheader("💡 Healthy Recommendations")
    for tip in data["tips"]:
        st.success("✔ " + tip)

    st.subheader("🚨 Warning Signs")
    for sign in data["warning"]:
        st.error(sign)

st.info(
    "This information is educational only and does not replace professional medical advice."
)

render_footer()
