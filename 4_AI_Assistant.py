import streamlit as st

from auth.auth_manager import require_login
from database import db_manager
from ai_assistant.assistant import get_answer
from utils.components import (
    set_page,
    render_navbar,
    render_user_bar,
    render_footer,
    section_header,
)

set_page("AI Assistant", "💬")
user = require_login()
render_navbar(active="AI Assistant")
render_user_bar(user)

section_header(
    "Ask anything",
    "AI Pregnancy Assistant",
    "Ask a pregnancy-related question — from morning sickness to warning "
    "signs. This assistant provides educational information only and every "
    "conversation is saved to your account.",
)


def _append_and_save(role: str, content: str):
    st.session_state.chat_history.append({"role": role, "content": content})
    db_manager.save_chat_message(user["id"], role, content)


# -----------------------------
# Chat history — loaded from SQLite so it survives across sessions,
# instead of resetting every time the page reruns.
# -----------------------------
if "chat_history" not in st.session_state:
    stored = db_manager.get_chat_history(user["id"])
    if stored:
        st.session_state.chat_history = [
            {"role": m["role"], "content": m["content"]} for m in stored
        ]
    else:
        greeting = (
            "Hi! 👋 I'm your pregnancy assistant. Ask me about symptoms, "
            "nutrition, baby development, warning signs, or anything else on "
            "your mind."
        )
        st.session_state.chat_history = [{"role": "assistant", "content": greeting}]
        db_manager.save_chat_message(user["id"], "assistant", greeting)

with st.container(key="glass_step"):
    for msg in st.session_state.chat_history:
        avatar = "🤰" if msg["role"] == "assistant" else "🙂"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    # Suggested questions
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    suggestions = [
        "Is headache normal?",
        "Can I exercise?",
        "What should I eat?",
        "When should I go to the doctor?",
    ]
    chip_cols = st.columns(len(suggestions))
    for i, q in enumerate(suggestions):
        with chip_cols[i]:
            with st.container(key=f"ghostbtn7_{i}"):
                if st.button(q, key=f"chip_{i}", use_container_width=True):
                    _append_and_save("user", q)
                    _append_and_save("assistant", get_answer(q))
                    st.rerun()

question = st.chat_input("Ask your question…")

if question:
    if question.strip() == "":
        st.warning("Please enter a question.")
    else:
        _append_and_save("user", question)
        _append_and_save("assistant", get_answer(question))
        st.rerun()

st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

clear_l, clear_r = st.columns([5, 1])
with clear_r:
    with st.container(key="ghostbtn_clearchat"):
        if st.button("Clear Chat", use_container_width=True):
            db_manager.clear_chat_history(user["id"])
            del st.session_state["chat_history"]
            st.rerun()

with st.expander("📋 Example Questions"):
    st.markdown("""
- Is headache normal?
- Can I exercise?
- What should I eat?
- Can I drink coffee?
- Is nausea normal?
- When should I go to the doctor?
- Can I travel?
- What vitamins should I take?
- What is preeclampsia?
- Is it normal to have swollen feet?
- When will I feel the baby move?
- What should I know about breastfeeding?
""")

st.caption(
    "Educational purposes only. This assistant is not a substitute for professional medical advice."
)

render_footer()
