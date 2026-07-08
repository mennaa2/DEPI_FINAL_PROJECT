import streamlit as st
from datetime import date, timedelta
from auth.auth_manager import require_login
from utils.components import (
    set_page,
    render_navbar,
    render_user_bar,
    render_footer,
    section_header,
    progress_ring,
)

set_page("Pregnancy Tracker", "🤰")
user = require_login()
render_navbar(active="Tracker")
render_user_bar(user)

section_header(
    "Week by week",
    "Pregnancy Tracker",
    "Track your pregnancy progress and estimated due date.",
)

# -------------------------
# Last Menstrual Period  (logic unchanged — now remembered across pages
# via session_state so the Dashboard can show the current week too)
# -------------------------
with st.container(key="glass_step"):
    lmp = st.date_input(
        "Select the First Day of Your Last Menstrual Period (LMP)",
        value=st.session_state.get("lmp_date", date.today()),
    )
st.session_state.lmp_date = lmp

today = date.today()

days = (today - lmp).days

week = days // 7

if week < 1:
    week = 1

if week > 40:
    week = 40

due_date = lmp + timedelta(days=280)
st.session_state.current_pregnancy_week = week

# -------------------------
# Summary cards
# -------------------------
ring_col, m1, m2 = st.columns([1.1, 1, 1])

with ring_col:
    with st.container(key="glass_ring"):
        progress_ring(
            percent=(week / 40) * 100,
            big_text=f"Week {week}",
            small_text=f"{week}/40 weeks",
        )

with m1:
    st.metric("Current Pregnancy Week", f"Week {week}")
    st.metric("Trimester", "1st" if week <= 13 else ("2nd" if week <= 27 else "3rd"))

with m2:
    st.metric("Expected Due Date", due_date.strftime("%d %B %Y"))
    st.metric("Days Remaining", max(0, (due_date - today).days))

st.progress(week / 40)
st.caption(f"Pregnancy Progress : {week}/40 Weeks")

st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

# -------------------------
# Weekly Information  (data unchanged)
# -------------------------
weekly_data = {

1:{
"baby":"The fertilized egg begins implantation.",
"mother":"You may not notice symptoms yet.",
"tips":"Take folic acid and avoid smoking."
},

5:{
"baby":"Baby's heart starts beating.",
"mother":"Morning sickness may begin.",
"tips":"Stay hydrated and eat small meals."
},

10:{
"baby":"Major organs are forming.",
"mother":"Fatigue and nausea are common.",
"tips":"Continue prenatal vitamins."
},

20:{
"baby":"Baby can hear sounds.",
"mother":"You may feel fetal movements.",
"tips":"Attend routine ultrasound appointments."
},

30:{
"baby":"Baby gains weight rapidly.",
"mother":"Back pain is common.",
"tips":"Sleep on your left side."
},

40:{
"baby":"Baby is ready for birth.",
"mother":"Labor may begin anytime.",
"tips":"Prepare for delivery."
}

}

nearest = min(
weekly_data.keys(),
key=lambda x:abs(x-week)
)

info = weekly_data[nearest]

section_header("This week", f"Week {week} Spotlight")

c1, c2, c3 = st.columns(3)
with c1:
    with st.container(key="glass_baby"):
        st.markdown("##### 👶 Baby Development")
        st.write(info["baby"])
with c2:
    with st.container(key="glass_mother"):
        st.markdown("##### 🤱 Mother's Symptoms")
        st.write(info["mother"])
with c3:
    with st.container(key="glass_tips"):
        st.markdown("##### ❤️ Weekly Tips")
        st.write(info["tips"])

# -------------------------
# Milestone Timeline
# -------------------------
section_header("The Journey", "Pregnancy Milestones")

for m in sorted(weekly_data.keys()):
    current = m == nearest

    with st.container(border=True):
        if current:
            st.markdown(f"### 🩷 Week {m} (You are here)")
        else:
            st.markdown(f"### Week {m}")

        st.write(weekly_data[m]["baby"])

st.caption(
"Educational information only. Consult your healthcare provider for medical advice."
)

render_footer()
