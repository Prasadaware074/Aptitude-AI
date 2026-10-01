"""Aptitude Scope Validator for AptitudeAI.
Provides deterministic, rule-based validation to ensure user queries
are strictly restricted to Aptitude preparation topics BEFORE any LLM call.
"""

import re
from typing import Optional, Tuple
from app.config.topics import TOPIC_REGISTRY, normalize_topic, is_valid_topic

RESTRICTION_MESSAGE = (
    "I am **AptitudeAI**, an aptitude-focused tutor. "
    "I can help with Quantitative Aptitude, Logical Reasoning, Verbal Ability, aptitude questions, concepts, practice, and mock tests. "
    "Please ask an aptitude-related question."
)

# Explicit keywords/phrases that indicate out-of-scope domains
OUT_OF_SCOPE_PATTERNS = [
    # General programming & software development
    r'\bpython\b', r'\bjava\b(?!script)', r'\bjavascript\b', r'\bc\+\+\b', r'\bc\#\b',
    r'\bhtml\b', r'\bcss\b', r'\breact\b', r'\bangular\b', r'\bvue\b', r'\bdjango\b',
    r'\bflask\b', r'\bfastapi\b', r'\bspring\s*boot\b', r'\bnode\.?js\b', r'\bdocker\b',
    r'\bkubernetes\b', r'\boperating\s+systems?\b', r'\blinux\s+commands?\b',
    r'\bbinary\s+search\b', r'\bbubble\s+sort\b', r'\bwrite\s+a\s+(?:python|java|c\+\+|code|program|script)\b',
    r'\bcoding\s+tutorial\b', r'\bprogramming\s+tutorial\b', r'\bsoftware\s+development\b',
    
    # Non-aptitude general domains
    r'\bmovie\b', r'\bmovies\b', r'\bcinema\b', r'\bactor\b', r'\bactress\b',
    r'\bsports\b', r'\bcricket\b', r'\bfootball\b', r'\bmatch\s+score\b',
    r'\bpolitics\b', r'\bpresident\b', r'\belection\b', r'\bpolitical\b',
    r'\bcooking\b', r'\brecipe\b', r'\bdish\b', r'\bhow\s+to\s+cook\b',
    r'\bsong\b', r'\blyrics\b', r'\bpoem\b', r'\bnovel\b', r'\bweather\b',
    r'\btell\s+me\s+a\s+joke\b', r'\bpersonal\s+advice\b', r'\brelationship\s+advice\b'
]

# Explicit aptitude domain keywords
APTITUDE_KEYWORDS = [
    "percentage", "profit", "loss", "cost price", "selling price", "discount", "ratio", "proportion",
    "time and work", "pipe", "cistern", "probability", "dice", "coin", "cards deck", "average", "mean",
    "speed", "distance", "time", "train", "number system", "lcm", "hcf", "divisibility", "algebra",
    "equation", "series", "missing number", "syllogism", "blood relation", "seating arrangement",
    "coding-decoding", "vocabulary", "synonym", "antonym", "grammar", "reading comprehension",
    "quant", "logical reasoning", "verbal ability", "aptitude", "mcq", "mcqs", "mock test", "practice",
    "weak", "strong", "performance", "accuracy", "score", "progress", "streak", "study plan", "schedule",
    "study", "routine", "what to study", "should i study", "flashcard", "lesson", "teach"
]

class ScopeValidator:
    """Validates whether a user query falls within aptitude scope."""

    @staticmethod
    def is_aptitude_query(query: str, topic: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Determines if query is aptitude-related.
        
        Returns:
            (is_aptitude: bool, canonical_topic_or_reason: str)
        """
        clean_q = (query or "").lower().strip()
        if not clean_q:
            return True, None

        # If an explicit valid topic parameter was passed
        if topic and is_valid_topic(topic):
            return True, normalize_topic(topic)

        # Exception check: "coding-decoding" topic vs out-of-scope "coding"
        is_coding_decoding = any(term in clean_q for term in ["coding-decoding", "coding decoding", "decoding"])

        # 1. Check explicit out-of-scope triggers
        if not is_coding_decoding:
            for pattern in OUT_OF_SCOPE_PATTERNS:
                if re.search(pattern, clean_q, re.IGNORECASE):
                    return False, "OUT_OF_SCOPE"

        # 2. Greetings & tutor identity
        greetings = [
            "hi", "hello", "hey", "good morning", "good evening", "greetings",
            "who are you", "what can you do", "help me", "thanks", "thank you", "start"
        ]
        if any(re.search(rf'\b{re.escape(w)}\b', clean_q) for w in greetings):
            return True, None

        # 3. Platform & study management queries
        platform_terms = [
            "weak topic", "weak topics", "weak", "my accuracy", "my score", "my performance",
            "study plan", "schedule", "mock test", "diagnostic", "streak", "progress", "trend",
            "study", "routine", "what to study", "should i study"
        ]
        if any(term in clean_q for term in platform_terms):
            return True, None

        # 4. Check for canonical topics or aliases in query text
        detected_topic = normalize_topic(clean_q)
        if detected_topic:
            return True, detected_topic

        # 5. Check aptitude keywords
        if any(kw in clean_q for kw in APTITUDE_KEYWORDS):
            return True, None

        # 6. Math / calculation expressions (e.g., "15% of 240", "5x + 3 = 18", "solve 240 / 12")
        if re.search(r'\d+[\%\+\-\*\/\=]', clean_q) or re.search(r'\b\d+\b.*(?:km|hr|meter|days|rs|\$|percent|ratio)', clean_q):
            return True, None

        # 7. Check if user asks "teach me X" or "questions on X" where X is unknown (non-aptitude)
        m = re.search(r'(?:teach|explain|lesson|concept|about|questions\s+on)\s+(?:me\s+)?(?:on\s+)?([a-zA-Z0-9\s\+\#]+)', clean_q)
        if m:
            target = m.group(1).strip()
            norm = normalize_topic(target)
            if norm:
                return True, norm
            else:
                return False, "OUT_OF_SCOPE"

        # Default fallback for completely ambiguous or unrelated general queries
        return False, "OUT_OF_SCOPE"
