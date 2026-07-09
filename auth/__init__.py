"""
Authentication package for the Maternal Care platform.

`auth_manager.require_login()` is the single entry point every page
should call right after `set_page(...)`. It renders the Login / Sign Up
screen and halts the script with `st.stop()` when nobody is logged in,
or lets the rest of the page render normally when they are.
"""

from auth.auth_manager import require_login, logout, current_user

__all__ = ["require_login", "logout", "current_user"]
