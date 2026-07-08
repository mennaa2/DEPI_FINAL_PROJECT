from datetime import date

import streamlit as st

from auth.auth_manager import require_login
from database import db_manager
from utils.components import (
    set_page,
    render_navbar,
    render_user_bar,
    render_footer,
    render_hero,
    section_header,
    feature_card_html,
    render_card_grid,
    render_stat_cards,
)

# -----------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------
set_page("Home", "🤰")

# -----------------------------------------------------------------------
# Authentication gate — shows Login / Sign Up and stops here if the
# visitor isn't logged in yet.
# -----------------------------------------------------------------------
user = require_login()

# -----------------------------------------------------------------------
# Navbar
# -----------------------------------------------------------------------
render_navbar(active="Home")
render_user_bar(user)

# -----------------------------------------------------------------------
# Personal Dashboard
# -----------------------------------------------------------------------
section_header(
    "Your dashboard",
    f"Welcome back, {user['full_name'].split(' ')[0]} 👋",
    f"Here's a quick snapshot of your maternal care journey — {date.today().strftime('%A, %d %B %Y')}.",
)

stats = db_manager.get_prediction_stats(user["id"])
last_chat = db_manager.get_last_chat_summary(user["id"])
pregnancy_week = st.session_state.get("current_pregnancy_week")

with st.container(key="glass_dash_stats"):
    dash_cards = [
        ("🗓️", "Today", date.today().strftime("%d %b %Y")),
        (
            "🤰",
            "Pregnancy Week",
            f"Week {pregnancy_week}" if pregnancy_week else "Not tracked yet",
        ),
        ("📊", "Predictions Logged", str(stats["count"])),
        (
            "💓",
            "Avg. Blood Pressure",
            f"{stats['avg_systolic']}/{stats['avg_diastolic']}" if stats["count"] else "—",
        ),
    ]
    render_stat_cards(dash_cards)

dash_l, dash_r = st.columns(2)
with dash_l:
    with st.container(key="glass_dash_recent"):
        st.markdown("##### 📋 Recent Prediction")
        if stats["latest"]:
            latest = stats["latest"]
            st.write(f"**Risk:** {latest['predicted_risk']}")
            st.caption(f"Logged on {latest['created_at']}")
            st.write(
                f"BP {latest['systolic_bp']}/{latest['diastolic_bp']} · "
                f"Glucose {latest['blood_sugar']} mg/dL"
            )
            st.page_link("pages/6_Pregnancy_History.py", label="View full history →")
        else:
            st.write("No predictions yet.")
            st.page_link("pages/1_Risk_Prediction.py", label="Run your first prediction →")

with dash_r:
    with st.container(key="glass_dash_chat"):
        st.markdown("##### 💬 Last AI Conversation")
        if last_chat:
            st.write(f"**You asked:** {last_chat['question']}")
            if last_chat["answer"]:
                preview = last_chat["answer"].split("\n")[0]
                st.caption(preview)
            st.page_link("pages/4_AI_Assistant.py", label="Continue the conversation →")
        else:
            st.write("You haven't chatted with the AI assistant yet.")
            st.page_link("pages/4_AI_Assistant.py", label="Ask a question →")

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
st.page_link(
    "pages/7_Medical_Report_Scanner.py",
    label="🧾 New: scan a lab report to auto-fill your risk prediction →",
)

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# Hero
# -----------------------------------------------------------------------
render_hero(
    eyebrow="AI-Powered Maternal Care",
    title_html="A calmer way to navigate<br><span class='grad'>pregnancy risk</span>",
    subtitle=(
        "Maternal Care brings together machine-learning risk prediction, weekly "
        "pregnancy tracking, and an always-on AI assistant — in one beautifully "
        "simple platform built for expecting mothers and the people who care for them."
    ),
)

hero_l, hero_c1, hero_c2, hero_c3, hero_r = st.columns([1.3, 1, 1, 1, 1.3])
with hero_c1:
    st.page_link("pages/1_Risk_Prediction.py", label="Try Prediction")
with hero_c2:
    with st.container(key="ghostbtn1"):
        st.page_link("pages/2_Pregnancy_Tracker.py", label="Track My Pregnancy")
with hero_c3:
    with st.container(key="ghostbtn2"):
        st.page_link("pages/4_AI_Assistant.py", label="Watch Demo · Ask AI")

st.markdown(
    """
    <div class="hero-stats">
        <div><div class="hero-stat-num">5</div><div class="hero-stat-label">Platform Modules</div></div>
        <div><div class="hero-stat-num">3</div><div class="hero-stat-label">Risk Classes</div></div>
        <div><div class="hero-stat-num">40</div><div class="hero-stat-label">Weeks Tracked</div></div>
        <div><div class="hero-stat-num">RF</div><div class="hero-stat-label">Random Forest Model</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# Features
# -----------------------------------------------------------------------
st.markdown("<div id='features'></div>", unsafe_allow_html=True)
section_header(
    "What's inside",
    "Everything a modern maternal-care platform needs",
    "Five focused modules, one consistent experience — from risk prediction to "
    "everyday guidance.",
)

features = [
    (
        "📊",
        "AI Risk Prediction",
        "A Random Forest model trained on clinical indicators estimates maternal risk level from vitals, history, and lab values.",
    ),
    (
        "🤰",
        "Pregnancy Tracking",
        "Log your last menstrual period and instantly see your current week, due date, and what's happening at each stage.",
    ),
    (
        "📈",
        "Health Dashboard",
        "Blood pressure, glucose, and other vitals summarized in one clean, glanceable view.",
    ),
    (
        "🩺",
        "Medical Analytics",
        "Risk scores and prediction history are logged so patterns become visible over time.",
    ),
    (
        "💬",
        "AI Chatbot",
        "Ask common pregnancy questions and get clear, educational answers in a familiar chat interface.",
    ),
    (
        "❤️",
        "Health Tips",
        "Condition-specific guidance — from blood pressure to nutrition — organized into easy-to-scan cards.",
    ),
]

cols = st.columns(3)

for i, (icon, title, desc) in enumerate(features):
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"## {icon}")
            st.subheader(title)
            st.write(desc)


# -----------------------------------------------------------------------
# How it works
# -----------------------------------------------------------------------
section_header("How it works", "Six steps from data to guidance")

steps = [
    ("1", "Go to Risk Prediction"),
    ("2", "Enter your health information"),
    ("3", "Get an instant AI risk prediction"),
    ("4", "Track your pregnancy progress"),
    ("5", "Read personalized health tips"),
    ("6", "Chat with the AI assistant anytime"),
]
cols = st.columns(3)
for i, (num, text) in enumerate(steps):
    with cols[i % 3]:
        with st.container(key=f"glass_how{i}"):
            st.markdown(
                f"<div style='font-family:var(--font-display);font-weight:800;"
                f"color:var(--accent);font-size:1.4rem;'>{num}</div>"
                f"<div style='color:var(--ink);font-weight:600;margin-top:6px;'>{text}</div>",
                unsafe_allow_html=True,
            )

st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# Disclaimer banner
# -----------------------------------------------------------------------
with st.container(key="glass_disclaimer"):
    st.markdown(
        "⚠️ &nbsp;**Educational use only.** This platform supports awareness and "
        "routine monitoring — it is **not** a medical diagnosis and does not "
        "replace professional healthcare advice.",
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------
render_footer()
