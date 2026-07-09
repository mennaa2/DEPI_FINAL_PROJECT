"""
Authentication logic for the Maternal Care platform.

Responsibilities:
    * Hashing / verifying passwords with bcrypt.
    * Validating sign-up input (email format, password match, etc).
    * Rendering the Login / Sign Up screen.
    * Managing the "who is logged in" session state.

Nothing in here touches SQLite directly — it delegates all persistence
to `database.db_manager`, keeping the auth layer and the storage layer
independent (per the "separate modules" requirement).
"""

import re
import sqlite3
import bcrypt
import streamlit as st

from database import db_manager

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# -----------------------------------------------------------------------
# Password helpers
# -----------------------------------------------------------------------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email.strip()))


# -----------------------------------------------------------------------
# Session helpers
# -----------------------------------------------------------------------
def _ensure_session_keys():
    st.session_state.setdefault("authenticated", False)
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("user_name", None)
    st.session_state.setdefault("user_email", None)


def current_user():
    """Return the logged-in user's info as a dict, or None."""
    _ensure_session_keys()
    if not st.session_state.authenticated:
        return None
    return {
        "id": st.session_state.user_id,
        "full_name": st.session_state.user_name,
        "email": st.session_state.user_email,
    }


def _log_user_in(user: dict):
    st.session_state.authenticated = True
    st.session_state.user_id = user["id"]
    st.session_state.user_name = user["full_name"]
    st.session_state.user_email = user["email"]


def logout():
    """Clear the session and send the user back to the login screen."""
    for key in ("authenticated", "user_id", "user_name", "user_email"):
        st.session_state.pop(key, None)
    st.rerun()


# -----------------------------------------------------------------------
# Forms
# -----------------------------------------------------------------------
def _render_login_form():
    with st.form("login_form", clear_on_submit=False):
        st.markdown("#### Welcome back")
        email = st.text_input("Email", placeholder="you@example.com", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Log In", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Please enter both your email and password.")
            return

        user = db_manager.verify_password(
            email, lambda stored_hash: check_password(password, stored_hash)
        )
        if user:
            _log_user_in(user)
            st.success(f"Welcome back, {user['full_name']}! Redirecting…")
            st.rerun()
        else:
            st.error("Incorrect email or password. Please try again.")


def _render_signup_form():
    with st.form("signup_form", clear_on_submit=False):
        st.markdown("#### Create your account")
        full_name = st.text_input("Full Name", placeholder="Jane Doe", key="signup_name")
        email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm = st.text_input(
            "Confirm Password", type="password", key="signup_confirm"
        )
        submitted = st.form_submit_button("Sign Up", use_container_width=True)

    if submitted:
        errors = []
        if not full_name.strip():
            errors.append("Full name is required.")
        if not email.strip():
            errors.append("Email is required.")
        elif not is_valid_email(email):
            errors.append("Please enter a valid email address.")
        if not password:
            errors.append("Password is required.")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm:
            errors.append("Passwords do not match.")

        if errors:
            for err in errors:
                st.error(err)
            return

        if db_manager.get_user_by_email(email):
            st.error("An account with this email already exists. Please log in instead.")
            return

        try:
            user = db_manager.create_user(full_name, email, hash_password(password))
        except sqlite3.IntegrityError:
            st.error("An account with this email already exists. Please log in instead.")
            return

        _log_user_in(user)
        st.success(f"Account created — welcome, {user['full_name']}!")
        st.rerun()


def require_login():
    """
    Call this at the top of every page (right after `set_page(...)`).

    Renders a Login / Sign Up screen and stops script execution when
    nobody is authenticated. Returns the current user dict when they
    are, so callers can use it immediately without a second lookup.
    """
    db_manager.init_db()
    _ensure_session_keys()

    if st.session_state.authenticated:
        return current_user()

    st.markdown(
        """
        <div class="hero-wrap" style="padding-top:20px;padding-bottom:6px;">
            <div class="hero-eyebrow">🤰 Maternal Care</div>
            <div class="hero-title" style="font-size:clamp(1.8rem,4vw,2.6rem);">
                Sign in to continue
            </div>
            <div class="hero-subtitle">
                Your predictions, pregnancy history, and AI conversations are
                kept securely tied to your account.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, mid, right = st.columns([1, 1.4, 1])
    with mid:
        with st.container(key="glass_step"):
            tab_login, tab_signup = st.tabs(["🔐 Log In", "📝 Sign Up"])
            with tab_login:
                _render_login_form()
            with tab_signup:
                _render_signup_form()

        st.caption(
            "🔒 Passwords are hashed with bcrypt and never stored in plain text."
        )

    st.stop()
