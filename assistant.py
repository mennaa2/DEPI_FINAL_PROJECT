"""
Retrieval logic for the Pregnancy AI Assistant.

Rather than a long chain of hardcoded if/else statements, questions are
scored against every keyword phrase in the knowledge base using a
combination of:

    1. Substring containment (fast path for exact phrasing)
    2. Word-overlap scoring (handles reordered / partial phrasing)
    3. Fuzzy string similarity via difflib (handles typos and different
       wording of the same underlying question)

The highest-scoring topic above a confidence threshold is returned.
This keeps the "knowledge" (knowledge_base.py) and the "retrieval"
(this file) cleanly separated, so the assistant can be extended by
adding entries to the knowledge base alone.
"""

import re
from difflib import SequenceMatcher

from ai_assistant.knowledge_base import KNOWLEDGE_BASE

STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "i", "my", "me", "to", "of", "in",
    "on", "for", "and", "or", "do", "does", "can", "could", "should", "will",
    "it", "this", "that", "what", "when", "how", "please", "im", "you",
    "your", "have", "has", "be", "being", "was", "were", "so", "if", "since",
    "with", "at", "as", "really", "very", "feel", "feeling", "feels",
}

MATCH_THRESHOLD = 0.32

NOT_A_DOCTOR_NOTE = (
    "\n\nℹ️ I'm an educational assistant, not a doctor — this doesn't "
    "replace professional medical advice."
)

FALLBACK = (
    "I don't have specific information on that yet. 🤔\n\n"
    "Please consult your healthcare provider for personalized medical "
    "advice, or try asking about topics like nutrition, exercise, baby "
    "development, or warning signs." + NOT_A_DOCTOR_NOTE
)

EMERGENCY_KEYWORDS = [
    "can't breathe", "cannot breathe", "unconscious", "seizure",
    "no movement", "not moving at all", "heavy bleeding", "severe bleeding",
]


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _significant_words(text: str) -> set:
    return {w for w in _normalize(text).split() if w not in STOPWORDS and len(w) > 1}


def _score_against_keyword(question_norm: str, question_words: set, keyword: str) -> float:
    keyword_norm = _normalize(keyword)

    # 1. Direct substring containment — strongest signal.
    if keyword_norm in question_norm or question_norm in keyword_norm:
        return 1.0

    # 2. Word overlap — handles reordered / partially-phrased questions.
    # Jaccard similarity (intersection / union) rather than raw keyword
    # coverage, so a short keyword can't win just by matching one common
    # word buried in a much longer, otherwise-unrelated question.
    keyword_words = _significant_words(keyword)
    union = keyword_words | question_words
    if union:
        overlap = len(keyword_words & question_words)
        overlap_score = overlap / len(union)
    else:
        overlap_score = 0.0

    # 3. Fuzzy similarity — catches typos / close rewording.
    fuzzy_score = SequenceMatcher(None, question_norm, keyword_norm).ratio()

    return max(overlap_score, fuzzy_score * 0.9)


def _is_emergency(question_norm: str) -> bool:
    return any(term in question_norm for term in EMERGENCY_KEYWORDS)


def get_answer(question: str) -> str:
    """
    Return the best-matching answer for a free-text pregnancy question.

    Always returns a non-empty, medically-cautious string — never raises
    on malformed input.
    """
    if not question or not question.strip():
        return "Please type a question and I'll do my best to help. 💬"

    question_norm = _normalize(question)
    question_words = _significant_words(question)

    if _is_emergency(question_norm):
        return (
            "🚨 This sounds like it could be a medical emergency. Please "
            "contact your healthcare provider immediately or go to the "
            "nearest emergency department. If you believe you or your baby "
            "are in immediate danger, call your local emergency number now."
        )

    best_entry = None
    best_score = 0.0

    for entry in KNOWLEDGE_BASE:
        for keyword in entry["keywords"]:
            score = _score_against_keyword(question_norm, question_words, keyword)
            if score > best_score:
                best_score = score
                best_entry = entry

    if best_entry and best_score >= MATCH_THRESHOLD:
        answer = best_entry["answer"]
        if "consult" not in answer.lower() and "provider" not in answer.lower():
            answer += NOT_A_DOCTOR_NOTE
        return answer

    return FALLBACK


def get_topics() -> list:
    """Return the list of distinct categories, for building UI suggestion chips."""
    seen = []
    for entry in KNOWLEDGE_BASE:
        if entry["category"] not in seen:
            seen.append(entry["category"])
    return seen
