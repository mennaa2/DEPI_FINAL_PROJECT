"""
Database layer for the Maternal Care platform.

Everything that touches SQLite (users, prediction history, AI chat
history) lives in `db_manager`. No other module should open a
connection to the database directly — always go through the
functions exposed here so the schema stays in one place.
"""

from database.db_manager import (
    init_db,
    create_user,
    get_user_by_email,
    verify_password,
    save_prediction,
    get_predictions,
    delete_prediction,
    get_prediction_stats,
    save_chat_message,
    get_chat_history,
    get_last_chat_summary,
    clear_chat_history,
)

__all__ = [
    "init_db",
    "create_user",
    "get_user_by_email",
    "verify_password",
    "save_prediction",
    "get_predictions",
    "delete_prediction",
    "get_prediction_stats",
    "save_chat_message",
    "get_chat_history",
    "get_last_chat_summary",
    "clear_chat_history",
]
