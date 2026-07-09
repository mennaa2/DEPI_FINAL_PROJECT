import streamlit as st
from auth.auth_manager import require_login
from utils.components import (
    set_page,
    render_navbar,
    render_user_bar,
    render_footer,
    section_header,
)

set_page("About", "ℹ️")
user = require_login()
render_navbar(active="About")
render_user_bar(user)

# -----------------------------
# Hero
# -----------------------------
st.markdown(
    """
    <div class="hero-wrap" style="padding-top:30px;padding-bottom:10px;">
        <div class="hero-eyebrow">ℹ️ About the project</div>
        <div class="hero-title" style="font-size:clamp(2rem,4.5vw,3rem);">
            Built to make maternal care<br><span class="grad">a little clearer</span>
        </div>
        <div class="hero-subtitle">
            Maternal Care Platform is an AI-powered pregnancy monitoring system
            developed as a Graduation Project — combining machine learning,
            education, and everyday tracking in one place.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Mission / Objectives
# -----------------------------
section_header("Our mission", "Project Objectives")

objectives = [
    "Predict maternal pregnancy risk using Machine Learning.",
    "Track pregnancy week and estimated due date.",
    "Provide educational health recommendations.",
    "Increase awareness of pregnancy risk factors.",
    "Offer a simple AI assistant for common pregnancy questions.",
]
cols = st.columns(len(objectives))
for i, obj in enumerate(objectives):
    with cols[i]:
        with st.container(key=f"glass_obj{i}"):
            st.markdown(
                f"<div style='font-size:1.4rem;'>✔️</div>"
                f"<div style='font-size:0.85rem;color:var(--ink);margin-top:6px;'>{obj}</div>",
                unsafe_allow_html=True,
            )

# -----------------------------
# Technologies
# -----------------------------
section_header("Under the hood", "Technologies Used")

techs = ["Python", "Streamlit", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Joblib"]
badge_html = "".join(
    f"<span style='display:inline-block;background:white;border:1.5px solid var(--border-soft);"
    f"padding:8px 18px;border-radius:999px;margin:4px;font-weight:600;font-size:0.85rem;"
    f"color:var(--ink);box-shadow:var(--shadow-soft);'>{t}</span>"
    for t in techs
)
st.markdown(f"<div style='text-align:center;'>{badge_html}</div>", unsafe_allow_html=True)

st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)

# -----------------------------
# Platform Modules timeline
# -----------------------------
section_header("What's inside", "Platform Modules")

modules = [
    ("📊 Risk Prediction", "Predict pregnancy risk using a trained Random Forest model."),
    ("🤰 Pregnancy Tracker", "Track pregnancy week and estimated due date."),
    ("❤️ Health Tips", "Educational recommendations based on common pregnancy conditions."),
    ("💬 AI Assistant", "Rule-based assistant answering common pregnancy questions."),
]
timeline_html = "<div class='timeline-track'>"
for title, desc in modules:
    timeline_html += f"<div class='timeline-item'><h5>{title}</h5><p>{desc}</p></div>"
timeline_html += "</div>"
st.markdown(timeline_html, unsafe_allow_html=True)

# -----------------------------
# Team
# -----------------------------
section_header("Who built it", "Project Team")

team = [
    ("Person 1", "Machine Learning & Risk Prediction"),
    ("Person 2", "Pregnancy Tracker"),
    ("Person 3", "Health Tips System"),
    ("Person 4", "AI Assistant"),
    ("Person 5", "Streamlit Dashboard & Integration"),
]
cols = st.columns(len(team))
for i, (name, role) in enumerate(team):
    with cols[i]:
        with st.container(key=f"glass_team{i}"):
            st.markdown(
                f"<div style='width:48px;height:48px;border-radius:50%;"
                f"background:var(--grad-primary);display:flex;align-items:center;"
                f"justify-content:center;color:white;font-weight:800;margin:0 auto 10px auto;'>"
                f"{name.split()[-1]}</div>"
                f"<div style='text-align:center;font-weight:700;color:var(--ink);font-size:0.92rem;'>{name}</div>"
                f"<div style='text-align:center;font-size:0.78rem;'>{role}</div>",
                unsafe_allow_html=True,
            )
st.caption("(Replace these with your team members' names.)")

st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

# -----------------------------
# Disclaimer
# -----------------------------
with st.container(key="darkcard_disclaimer"):
    st.markdown(
        "#### ⚠ Disclaimer\n\n"
        "This platform is intended for educational purposes only.\n\n"
        "It is **NOT** a medical diagnosis tool and should not replace professional "
        "medical advice. Always consult a qualified healthcare provider for medical "
        "concerns."
    )

st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
st.success("Thank you for using Maternal Care Platform ❤️")
st.caption("Graduation Project • 2026")

render_footer()
