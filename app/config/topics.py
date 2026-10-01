"""Central Topic Registry for AptitudeAI.
Defines supported aptitude topics, categories, normalized names, and keyword aliases.
"""

import re
from typing import Dict, Any, List, Optional

TOPIC_REGISTRY: Dict[str, Dict[str, Any]] = {
    # --- QUANTITATIVE APTITUDE ---
    "Percentage": {
        "category": "Quantitative Aptitude",
        "aliases": ["percentage", "percent", "percentages", "%"],
        "description": "Calculation of per-hundred ratios, percentage increases/decreases, and successive changes."
    },
    "Profit and Loss": {
        "category": "Quantitative Aptitude",
        "aliases": ["profit and loss", "profit & loss", "profit", "loss", "cost price", "selling price", "marked price", "discount", "cp", "sp", "mp"],
        "description": "Financial profit, loss, cost price, selling price, marked price, and discount calculations."
    },
    "Ratio and Proportion": {
        "category": "Quantitative Aptitude",
        "aliases": ["ratio and proportion", "ratio & proportion", "ratio", "proportion", "ratios", "proportions"],
        "description": "Quantitative comparison by division and equality of ratios."
    },
    "Time and Work": {
        "category": "Quantitative Aptitude",
        "aliases": ["time and work", "time & work", "work and time", "pipes and cisterns", "work done", "pipe", "cistern", "man hours"],
        "description": "Efficiency, completion rates, combined work duration, and pipe filling/emptying problems."
    },
    "Probability": {
        "category": "Quantitative Aptitude",
        "aliases": ["probability", "dice", "coin", "coins", "cards deck", "chance", "random draw"],
        "description": "Likelihood of events, sample spaces, dice rolling, coin flips, and card/ball selections."
    },
    "Average": {
        "category": "Quantitative Aptitude",
        "aliases": ["average", "averages", "mean", "weighted average", "arithmetic mean"],
        "description": "Calculation of arithmetic mean, weighted averages, and replacement/addition in groups."
    },
    "Speed, Distance and Time": {
        "category": "Quantitative Aptitude",
        "aliases": ["speed, distance and time", "speed distance and time", "speed distance time", "speed and distance", "trains", "relative speed", "distance and time", "speed", "distance", "time distance", "boat and stream"],
        "description": "Speed, distance, time relationships, train motion, relative speeds, and river streams."
    },
    "Number System": {
        "category": "Quantitative Aptitude",
        "aliases": ["number system", "divisibility", "lcm and hcf", "hcf", "lcm", "remainders", "factors", "prime numbers", "integers"],
        "description": "Divisibility rules, LCM/HCF, remainders, factors, and properties of numbers."
    },
    "Algebra": {
        "category": "Quantitative Aptitude",
        "aliases": ["algebra", "linear equations", "quadratic equations", "equations", "algebraic identities"],
        "description": "Linear and quadratic equations, algebraic expansions, and age-related word problems."
    },

    # --- LOGICAL REASONING ---
    "Number Series": {
        "category": "Logical Reasoning",
        "aliases": ["number series", "missing number", "series completion", "numerical series", "number sequence", "sequence"],
        "description": "Mathematical sequence pattern recognition, difference analysis, and next-term prediction."
    },
    "Syllogism": {
        "category": "Logical Reasoning",
        "aliases": ["syllogism", "syllogisms", "venn diagram reasoning", "statements and conclusions", "deductive logic"],
        "description": "Deductive logical conclusions from given premises using Venn diagram logic."
    },
    "Blood Relations": {
        "category": "Logical Reasoning",
        "aliases": ["blood relations", "blood relation", "family tree", "relations", "relationship puzzle"],
        "description": "Deciphering family relationships, pointing-to-photo puzzles, and genealogical structures."
    },
    "Seating Arrangement": {
        "category": "Logical Reasoning",
        "aliases": ["seating arrangement", "linear arrangement", "circular arrangement", "seating", "row arrangement"],
        "description": "Positional arrangement of individuals in linear rows or circular setups."
    },
    "Coding-Decoding": {
        "category": "Logical Reasoning",
        "aliases": ["coding-decoding", "coding decoding", "letter coding", "number coding", "cipher", "decode"],
        "description": "Deciphering position shifts, letter transformations, and secret message codes."
    },

    # --- VERBAL ABILITY ---
    "Vocabulary": {
        "category": "Verbal Ability",
        "aliases": ["vocabulary", "vocab", "synonym", "synonyms", "antonym", "antonyms", "word meaning", "word power"],
        "description": "Understanding word meanings, synonyms, antonyms, root words, and contextual usage."
    },
    "Grammar": {
        "category": "Verbal Ability",
        "aliases": ["grammar", "error spotting", "sentence correction", "subject verb agreement", "tenses", "prepositions", "articles"],
        "description": "English sentence structure, subject-verb agreement, verb tenses, and modifier placement."
    },
    "Reading Comprehension": {
        "category": "Verbal Ability",
        "aliases": ["reading comprehension", "passage", "comprehension", "reading passage", "rc"],
        "description": "Passage analysis, main idea identification, contextual inference, and reading retention."
    }
}

ALL_TOPICS: List[str] = list(TOPIC_REGISTRY.keys())

def is_valid_topic(topic: str) -> bool:
    """Check if topic exists in registry (case-insensitive)."""
    return normalize_topic(topic) is not None

def normalize_topic(topic: str) -> Optional[str]:
    """Resolve a raw topic string, alias, or query containing a topic to canonical Topic name."""
    if not topic:
        return None
    t_clean = topic.strip().lower()

    # 1. Exact match
    for canon_name, info in TOPIC_REGISTRY.items():
        if canon_name.lower() == t_clean:
            return canon_name
        for alias in info["aliases"]:
            if alias.lower() == t_clean:
                return canon_name

    # 2. Substring match for longest alias inside text
    best_match = None
    best_len = 0
    for canon_name, info in TOPIC_REGISTRY.items():
        # Check canonical name in text
        pattern_canon = r'\b' + re.escape(canon_name.lower()) + r'\b'
        if re.search(pattern_canon, t_clean) and len(canon_name) > best_len:
            best_match = canon_name
            best_len = len(canon_name)
        # Check aliases in text
        for alias in info["aliases"]:
            pattern_alias = r'\b' + re.escape(alias.lower()) + r'\b'
            if re.search(pattern_alias, t_clean) and len(alias) > best_len:
                best_match = canon_name
                best_len = len(alias)

    return best_match

def get_category_for_topic(topic: str) -> str:
    """Get canonical category for a given topic."""
    norm = normalize_topic(topic)
    if norm and norm in TOPIC_REGISTRY:
        return TOPIC_REGISTRY[norm]["category"]
    return "Quantitative Aptitude"
