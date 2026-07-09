"""
AI Assistant package.

`knowledge_base` holds the topic/keyword/answer content (the
"retrieval corpus"). `assistant` holds the matching logic that turns a
free-text question into the best-matching answer, so the two concerns
— content vs. retrieval — can evolve independently.
"""

from ai_assistant.assistant import get_answer

__all__ = ["get_answer"]
