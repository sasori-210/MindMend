"""
engine.py — MindMend conversation engine.

Fully offline, no external API calls. Given the full message history plus
an optional language code, it:

  1. Checks for crisis language first, always (language-aware keyword list).
  2. Tries to remember the user's name if they've mentioned it.
  3. Scores the latest user message against known intents via keyword match.
  4. Picks a response variant for that intent and language, avoiding
     immediate repeats.
  5. Occasionally offers a grounding technique for anxiety/stress/sadness.
  6. Returns both the reply text and an emotion tag for the frontend orb.
"""

import random
import re

from knowledge import (
    BOT_NAME,
    CRISIS_KEYWORDS,
    CRISIS_RESPONSE,
    INTENT_KEYWORDS,
    RESPONSES,
    GROUNDING_TECHNIQUES,
    SUPPORTED_LANGUAGES,
    RELUCTANCE_KEYWORDS,
    RELUCTANT_RESPONSES,
)

NAME_PATTERN = re.compile(
    r"\b(?:my name is|i'?m called|call me)\s+([A-Za-z][A-Za-z'\-]{1,20})\b",
    re.IGNORECASE,
)

GROUNDING_ELIGIBLE = {"anxiety", "academic_stress", "sadness"}
DEFAULT_LANGUAGE = "en"


def _normalize_language(language):
    if language and language.lower() in SUPPORTED_LANGUAGES:
        return language.lower()
    return DEFAULT_LANGUAGE


def _extract_user_messages(messages):
    return [m.get("content", "") for m in messages if m.get("role") == "user"]


def _extract_assistant_messages(messages):
    return [m.get("content", "") for m in messages if m.get("role") == "assistant"]


def _detect_name(all_user_text):
    for text in all_user_text:
        match = NAME_PATTERN.search(text)
        if match:
            return match.group(1).capitalize()
    return None


def _contains_keyword(keyword, lowered_text):
    """Word-boundary match so short keywords (e.g. 'hey', 'hi', 'low') don't
    false-positive inside unrelated words (e.g. 'they', 'this', 'below').
    Devanagari/Telugu keywords have no ASCII word-boundary concept, so for
    those we fall back to plain substring matching."""
    if keyword.isascii():
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        return re.search(pattern, lowered_text) is not None
    return keyword in lowered_text


def _is_crisis(text):
    lowered = text.lower()
    return any(_contains_keyword(kw, lowered) for kw in CRISIS_KEYWORDS)


def _is_reluctant(text, language):
    lowered = text.lower()
    keywords = RELUCTANCE_KEYWORDS.get(language, []) + RELUCTANCE_KEYWORDS.get(DEFAULT_LANGUAGE, [])
    return any(_contains_keyword(kw, lowered) for kw in keywords)


def _detect_intent(text):
    lowered = text.lower()
    scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if _contains_keyword(kw, lowered))
        if score:
            scores[intent] = score
    if not scores:
        return "general_support"
    return max(scores, key=scores.get)


def _intent_depth(user_msgs, current_intent):
    """How many times (including now) this same intent has come up, so the
    engine can escalate from a first-mention 'open' reply to a 'deepen' and
    then a 'reflective' one instead of repeating itself."""
    return sum(1 for msg in user_msgs if _detect_intent(msg) == current_intent)


def _tier_for_depth(depth):
    if depth <= 1:
        return "open"
    if depth == 2:
        return "deepen"
    return "reflective"


def _get_variants(language, intent):
    lang_bank = RESPONSES.get(language, RESPONSES[DEFAULT_LANGUAGE])
    variants = lang_bank.get(intent)
    if not variants:
        # fall back to English for this intent if the language bank lacks it
        variants = RESPONSES[DEFAULT_LANGUAGE].get(intent, RESPONSES[DEFAULT_LANGUAGE]["general_support"])
    return variants


def _pick_variant(language, intent, recent_assistant_texts, depth=1):
    variants = _get_variants(language, intent)
    tier = _tier_for_depth(depth)

    # Prefer variants tagged for this depth; variants without a "tier" key
    # count as "open". Fall back to the full bank if this tier has nothing
    # (keeps partially-translated languages safe).
    tiered = [v for v in variants if v.get("tier", "open") == tier]
    pool = tiered or variants

    last = recent_assistant_texts[-1] if recent_assistant_texts else None
    candidates = [v for v in pool if (v["reflection"] + " " + v["follow_up"]) != last] or pool
    return random.choice(candidates)


def _pick_reluctant_variant(language, recent_assistant_texts):
    variants = RELUCTANT_RESPONSES.get(language, RELUCTANT_RESPONSES[DEFAULT_LANGUAGE])
    last = recent_assistant_texts[-1] if recent_assistant_texts else None
    candidates = [v for v in variants if (v["reflection"] + " " + v["follow_up"]) != last] or variants
    return random.choice(candidates)


def generate_reply(messages, language=None):
    """
    messages: list of {"role": "user"|"assistant"|"system", "content": str}
    language: one of "en", "hi", "te" (defaults to "en" if missing/unknown)

    Returns: (reply_text: str, emotion: str)
    """
    language = _normalize_language(language)
    user_msgs = _extract_user_messages(messages)
    assistant_msgs = _extract_assistant_messages(messages)

    if not user_msgs:
        return f"Hey, I'm {BOT_NAME}. I'm here whenever you're ready to talk.", "gentle"

    latest = user_msgs[-1]

    # 1. Crisis check — always first, overrides everything else, any language.
    if _is_crisis(latest):
        return CRISIS_RESPONSE.get(language, CRISIS_RESPONSE[DEFAULT_LANGUAGE]), "crisis"

    # 2. Reluctance check — if they've signaled they don't want to unpack
    # this right now, back off instead of asking another probing question.
    if _is_reluctant(latest, language):
        variant = _pick_reluctant_variant(language, assistant_msgs)
        reply = variant["reflection"] + " " + variant["follow_up"]
        return reply, variant["emotion"]

    # 3. Remember name if mentioned anywhere in the conversation so far.
    name = _detect_name(user_msgs)

    # 4. Intent + depth-aware response (gets warmer/more specific the more
    # times the same topic comes up, instead of repeating itself).
    intent = _detect_intent(latest)
    depth = _intent_depth(user_msgs, intent)
    variant = _pick_variant(language, intent, assistant_msgs, depth)

    reply = variant["reflection"]
    follow_up = variant["follow_up"]
    emotion = variant["emotion"]

    if name and intent not in ("smalltalk",):
        reply = reply.rstrip("।.") + f", {name}."

    reply += " " + follow_up

    # 5. Occasionally attach a grounding technique for heavier intents.
    if intent in GROUNDING_ELIGIBLE and random.random() < 0.35:
        techniques = GROUNDING_TECHNIQUES.get(language, GROUNDING_TECHNIQUES[DEFAULT_LANGUAGE])
        reply += "\n\n" + random.choice(techniques)

    return reply, emotion
