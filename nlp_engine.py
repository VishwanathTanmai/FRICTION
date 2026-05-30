"""
nlp_engine.py — Pure Python NLP Engine for Fix My Itch Clone
=============================================================

A production-quality NLP pipeline built entirely with Python standard
library modules (re, collections, math, json, string).  No external
dependencies such as nltk, spacy, or transformers are used.

Classes
-------
NLPEngine
    Tokenisation, stopword removal, sentiment analysis (AFINN-style
    lexicon with 500+ entries), TF-IDF keyword extraction, root-cause
    detection, inefficiency detection, market-size estimation,
    solvability scoring, and a unified ``analyze_problem`` pipeline.
"""

from __future__ import annotations

import math
import re
import string
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────────────
# Category multipliers used in market-size estimation
# ──────────────────────────────────────────────────────────────────────
CATEGORY_WEIGHTS: Dict[str, float] = {
    "Health": 1.3,
    "Finance": 1.4,
    "Education": 1.2,
    "Logistics": 1.1,
    "Food": 1.0,
    "Legal": 1.1,
    "Transport": 1.15,
    "Housing": 1.25,
    "Agriculture": 1.1,
    "Environment": 1.05,
    "Technology": 1.3,
    "Employment": 1.2,
    "Safety": 1.15,
    "Governance": 1.0,
    "General": 1.0,
}

# ──────────────────────────────────────────────────────────────────────
# 300+ English stop-words (curated superset of common NLP lists)
# ──────────────────────────────────────────────────────────────────────
_STOPWORDS: set = {
    "a", "about", "above", "across", "after", "afterwards", "again",
    "against", "ain", "all", "almost", "alone", "along", "already",
    "also", "although", "always", "am", "among", "amongst", "an", "and",
    "another", "any", "anyhow", "anyone", "anything", "anyway",
    "anywhere", "are", "aren", "aren't", "around", "as", "at", "back",
    "be", "became", "because", "become", "becomes", "becoming", "been",
    "before", "beforehand", "behind", "being", "below", "beside",
    "besides", "between", "beyond", "both", "bottom", "but", "by",
    "call", "can", "cannot", "co", "con", "could", "couldn", "couldn't",
    "d", "de", "did", "didn", "didn't", "do", "does", "doesn", "doesn't",
    "doing", "don", "done", "don't", "down", "due", "during", "each",
    "eg", "eight", "either", "eleven", "else", "elsewhere", "empty",
    "enough", "etc", "even", "ever", "every", "everyone", "everything",
    "everywhere", "except", "few", "fifteen", "fifty", "fill", "find",
    "fire", "first", "five", "for", "former", "formerly", "forty",
    "found", "four", "from", "front", "full", "further", "get", "give",
    "go", "got", "had", "hadn", "hadn't", "has", "hasn", "hasn't",
    "have", "haven", "haven't", "having", "he", "hence", "her", "here",
    "hereafter", "hereby", "herein", "hereupon", "hers", "herself",
    "him", "himself", "his", "how", "however", "hundred", "i", "ie",
    "if", "in", "inc", "indeed", "interest", "into", "is", "isn",
    "isn't", "it", "it's", "its", "itself", "just", "keep", "last",
    "latter", "latterly", "least", "less", "let", "like", "ll", "ltd",
    "m", "ma", "made", "many", "may", "me", "meanwhile", "might",
    "mightn", "mightn't", "mill", "mine", "more", "moreover", "most",
    "mostly", "move", "much", "must", "mustn", "mustn't", "my",
    "myself", "name", "namely", "needn", "needn't", "neither", "never",
    "nevertheless", "next", "nine", "no", "nobody", "none", "noone",
    "nor", "not", "nothing", "now", "nowhere", "o", "of", "off",
    "often", "on", "once", "one", "only", "onto", "or", "other",
    "others", "otherwise", "our", "ours", "ourselves", "out", "over",
    "own", "part", "per", "perhaps", "please", "put", "quite", "rather",
    "re", "really", "regarding", "s", "said", "same", "say", "see",
    "seem", "seemed", "seeming", "seems", "serious", "several", "shan",
    "shan't", "she", "she's", "should", "should've", "shouldn",
    "shouldn't", "show", "side", "since", "sincere", "six", "sixty",
    "so", "some", "somehow", "someone", "something", "sometime",
    "sometimes", "somewhere", "still", "such", "system", "t", "take",
    "ten", "than", "that", "that'll", "the", "their", "theirs", "them",
    "themselves", "then", "thence", "there", "thereafter", "thereby",
    "therefore", "therein", "thereupon", "these", "they", "thick",
    "thin", "third", "this", "those", "though", "three", "through",
    "throughout", "thru", "thus", "to", "together", "too", "top",
    "toward", "towards", "twelve", "twenty", "two", "un", "under",
    "until", "up", "upon", "us", "used", "using", "various", "ve",
    "very", "via", "was", "wasn", "wasn't", "we", "well", "were",
    "weren", "weren't", "what", "whatever", "when", "whence", "whenever",
    "where", "whereafter", "whereas", "whereby", "wherein", "whereupon",
    "wherever", "whether", "which", "while", "whither", "who", "whoever",
    "whole", "whom", "why", "will", "with", "within", "without", "won",
    "won't", "would", "wouldn", "wouldn't", "y", "yet", "you", "you'd",
    "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves",
    # Additional high-frequency filler words
    "actually", "already", "always", "am", "became", "becomes",
    "becoming", "begin", "beginning", "beginnings", "begins", "behind",
    "believe", "beside", "besides", "best", "better", "big", "bit",
    "came", "certain", "certainly", "change", "clear", "come", "comes",
    "coming", "consider", "considering", "day", "days", "despite",
    "different", "early", "end", "ends", "especially", "exactly",
    "example", "except", "fact", "far", "felt", "generally", "given",
    "going", "gone", "good", "great", "hand", "high", "home", "however",
    "important", "including", "instead", "just", "knew", "know", "known",
    "knows", "large", "later", "left", "let", "likely", "little",
    "long", "look", "looking", "looks", "lot", "make", "makes",
    "making", "man", "matter", "men", "might", "mind", "money", "need",
    "needed", "needs", "new", "number", "old", "order", "part",
    "particular", "particularly", "people", "place", "point", "possible",
    "probably", "problem", "problems", "put", "quite", "ran", "rather",
    "right", "room", "run", "running", "said", "saw", "second", "set",
    "shall", "simply", "small", "sort", "start", "started", "state",
    "sure", "tell", "thing", "things", "think", "thinking", "thought",
    "time", "times", "today", "told", "took", "turn", "turned", "two",
    "understand", "until", "use", "want", "wanted", "wants", "water",
    "way", "ways", "went", "while", "without", "woman", "women", "word",
    "words", "work", "working", "works", "world", "would", "year",
    "years", "young",
}

# ──────────────────────────────────────────────────────────────────────
# AFINN-style sentiment lexicon  (500+ entries, scores −5 … +5)
# ──────────────────────────────────────────────────────────────────────
_SENTIMENT_LEXICON: Dict[str, int] = {
    # --- strongly negative (-5) ---
    "scam": -5, "fraud": -5, "murder": -5, "rape": -5, "kill": -5,
    "suicide": -5, "terrorist": -5, "terrorism": -5, "massacre": -5,
    "genocide": -5, "catastrophe": -5, "devastating": -5, "atrocity": -5,
    "trafficking": -5, "slavery": -5, "extortion": -5, "homicide": -5,
    "abduction": -5, "famine": -5, "plague": -5, "pandemic": -5,
    "lethal": -5, "fatal": -5, "death": -5, "deadliest": -5,

    # --- very negative (-4) ---
    "terrible": -4, "frustrating": -4, "nightmare": -4, "hate": -4,
    "impossible": -4, "dangerous": -4, "toxic": -4, "corrupt": -4,
    "exploit": -4, "exploitation": -4, "awful": -4, "horrible": -4,
    "disgusting": -4, "horrific": -4, "dreadful": -4, "appalling": -4,
    "abysmal": -4, "unbearable": -4, "excruciating": -4, "vile": -4,
    "repulsive": -4, "outrageous": -4, "ruthless": -4, "disastrous": -4,
    "destructive": -4, "malicious": -4, "abusive": -4, "horrendous": -4,
    "deplorable": -4, "wretched": -4, "miserable": -4, "atrocious": -4,
    "heinous": -4, "oppressive": -4, "tyranny": -4, "agony": -4,
    "torment": -4, "fury": -4, "rage": -4, "hostile": -4,
    "venomous": -4, "treacherous": -4, "deceit": -4, "betrayal": -4,
    "crippling": -4, "paralyzing": -4, "suffocating": -4,

    # --- negative (-3) ---
    "broken": -3, "expensive": -3, "struggle": -3, "anxious": -3,
    "unreliable": -3, "complicated": -3, "painful": -3, "unfair": -3,
    "inefficient": -3, "worried": -3, "afraid": -3, "angry": -3,
    "annoyed": -3, "annoying": -3, "bad": -3, "boring": -3,
    "careless": -3, "chaos": -3, "collapse": -3, "complaint": -3,
    "conflict": -3, "confusing": -3, "costly": -3, "cruel": -3,
    "damage": -3, "damaging": -3, "decay": -3, "decline": -3,
    "defective": -3, "delay": -3, "denial": -3, "depressing": -3,
    "desperate": -3, "dirty": -3, "disappoint": -3, "disappointed": -3,
    "disappointing": -3, "disappointment": -3, "discrimination": -3,
    "dishonest": -3, "dislike": -3, "dismiss": -3, "disorder": -3,
    "distress": -3, "disturbing": -3, "downturn": -3, "drain": -3,
    "dreadful": -3, "drought": -3, "dump": -3, "dysfunction": -3,
    "embarrass": -3, "embarrassing": -3, "emergency": -3, "error": -3,
    "exhausted": -3, "exhausting": -3, "fail": -3, "failed": -3,
    "failing": -3, "failure": -3, "fake": -3, "fear": -3, "filthy": -3,
    "flaw": -3, "flawed": -3, "flood": -3, "foolish": -3, "fraud": -3,
    "frightening": -3, "grief": -3, "grim": -3, "gross": -3,
    "guilt": -3, "guilty": -3, "harassment": -3, "hardship": -3,
    "harm": -3, "harmful": -3, "harsh": -3, "heartbreaking": -3,
    "helpless": -3, "hopeless": -3, "hurt": -3, "ignorant": -3,
    "illness": -3, "immoral": -3, "impair": -3, "inadequate": -3,
    "incompetent": -3, "inferior": -3, "injustice": -3, "insecure": -3,
    "intimidate": -3, "intimidating": -3, "irrational": -3, "jail": -3,
    "jeopardize": -3, "lack": -3, "lame": -3, "lies": -3, "loneliness": -3,
    "lonely": -3, "lose": -3, "loss": -3, "lousy": -3, "manipulate": -3,
    "manipulation": -3, "menace": -3, "mess": -3, "misery": -3,
    "mislead": -3, "misleading": -3, "mistake": -3, "mob": -3,
    "mourn": -3, "neglect": -3, "negligence": -3, "nervous": -3,
    "obstacle": -3, "offend": -3, "offensive": -3, "overwhelm": -3,
    "overwhelming": -3, "pain": -3, "pathetic": -3, "penalty": -3,
    "pessimistic": -3, "pitiful": -3, "pity": -3, "pollute": -3,
    "pollution": -3, "poverty": -3, "prison": -3, "punish": -3,
    "punishment": -3, "reject": -3, "rejection": -3, "resent": -3,
    "resentment": -3, "risk": -3, "risky": -3, "rob": -3, "rude": -3,
    "ruin": -3, "ruthless": -3, "sacrifice": -3, "sad": -3, "scare": -3,
    "scary": -3, "scold": -3, "severe": -3, "shame": -3, "shock": -3,
    "shocking": -3, "sick": -3, "sickness": -3, "sinister": -3,
    "sob": -3, "sorrow": -3, "stagnant": -3, "steal": -3,
    "stereotype": -3, "stress": -3, "stressful": -3, "strike": -3,
    "stubborn": -3, "stupid": -3, "suffer": -3, "suffering": -3,
    "suspect": -3, "suspicious": -3, "terrible": -3, "terrify": -3,
    "terrifying": -3, "threat": -3, "threaten": -3, "threatening": -3,
    "trauma": -3, "trouble": -3, "troubling": -3, "ugly": -3,
    "unable": -3, "unacceptable": -3, "uncertain": -3, "unethical": -3,
    "unfortunate": -3, "unhappy": -3, "unhealthy": -3, "unjust": -3,
    "unlawful": -3, "unpleasant": -3, "unsafe": -3, "unstable": -3,
    "upset": -3, "useless": -3, "vandal": -3, "victim": -3,
    "violate": -3, "violation": -3, "violence": -3, "violent": -3,
    "vulnerability": -3, "vulnerable": -3, "war": -3, "warn": -3,
    "warning": -3, "waste": -3, "weak": -3, "weakness": -3, "weary": -3,
    "wicked": -3, "worse": -3, "worst": -3, "worthless": -3,
    "wrong": -3, "wrongful": -3,

    # --- mildly negative (-2) ---
    "slow": -2, "confused": -2, "bother": -2, "concern": -2,
    "criticism": -2, "critic": -2, "criticize": -2, "cynical": -2,
    "debt": -2, "deficit": -2, "difficulty": -2, "difficult": -2,
    "disadvantage": -2, "discomfort": -2, "discouraging": -2,
    "doubt": -2, "dull": -2, "envy": -2, "exaggerate": -2,
    "excess": -2, "excuse": -2, "fatigue": -2, "fee": -2, "feeble": -2,
    "fuss": -2, "gloom": -2, "gloomy": -2, "grumpy": -2, "hesitant": -2,
    "ignore": -2, "impatient": -2, "imperfect": -2, "impose": -2,
    "inconvenient": -2, "indifferent": -2, "inferior": -2,
    "interrupt": -2, "irritate": -2, "irritating": -2, "jealous": -2,
    "lag": -2, "lazy": -2, "limit": -2, "limited": -2, "mediocre": -2,
    "minor": -2, "miss": -2, "missing": -2, "monotonous": -2,
    "muddy": -2, "nag": -2, "narrow": -2, "negative": -2,
    "neglected": -2, "noise": -2, "noisy": -2, "odd": -2,
    "outdated": -2, "overpriced": -2, "penalty": -2, "poor": -2,
    "postpone": -2, "pressure": -2, "pretend": -2, "protest": -2,
    "quarrel": -2, "questionable": -2, "reluctant": -2, "restrict": -2,
    "rigid": -2, "rough": -2, "rush": -2, "scratch": -2, "selfish": -2,
    "shallow": -2, "skeptical": -2, "sluggish": -2, "sloppy": -2,
    "sour": -2, "stale": -2, "strain": -2, "strict": -2, "tense": -2,
    "tight": -2, "tired": -2, "tiresome": -2, "trivial": -2,
    "uncertain": -2, "unclear": -2, "uncomfortable": -2, "undermine": -2,
    "uneasy": -2, "unfamiliar": -2, "unfit": -2, "unfortunate": -2,
    "unpopular": -2, "unreasonable": -2, "unsatisfied": -2,
    "unsure": -2, "unwanted": -2, "unwilling": -2, "vague": -2,
    "wary": -2,

    # --- slightly negative (-1) ---
    "adequate": -1, "ambiguous": -1, "average": -1, "bare": -1,
    "basic": -1, "bland": -1, "busy": -1, "cautious": -1, "cold": -1,
    "complex": -1, "complicated": -1, "confuse": -1, "conservative": -1,
    "constrain": -1, "conventional": -1, "delay": -1, "disrupt": -1,
    "distract": -1, "dry": -1, "flat": -1, "formal": -1, "gap": -1,
    "hard": -1, "heavy": -1, "hesitate": -1, "hidden": -1,
    "hurry": -1, "idle": -1, "irregular": -1, "lengthy": -1, "load": -1,
    "moderate": -1, "mundane": -1, "naive": -1, "neutral": -1,
    "normal": -1, "ordinary": -1, "passive": -1, "plain": -1,
    "regret": -1, "repeat": -1, "routine": -1, "shy": -1, "simple": -1,
    "slight": -1, "static": -1, "subtle": -1, "suspect": -1,
    "typical": -1, "uncertain": -1, "unfamiliar": -1, "usual": -1,
    "wait": -1, "wander": -1,

    # --- slightly positive (+1) ---
    "accept": 1, "adequate": 1, "agree": 1, "calm": 1, "clean": 1,
    "clear": 1, "comfortable": 1, "common": 1, "complete": 1,
    "consistent": 1, "correct": 1, "decent": 1, "fair": 1,
    "familiar": 1, "fine": 1, "fit": 1, "flexible": 1, "focus": 1,
    "free": 1, "fresh": 1, "function": 1, "genuine": 1, "honest": 1,
    "hopeful": 1, "improve": 1, "include": 1, "inform": 1,
    "interest": 1, "kind": 1, "logical": 1, "manage": 1, "mild": 1,
    "natural": 1, "neat": 1, "normal": 1, "notable": 1, "ok": 1,
    "okay": 1, "open": 1, "patient": 1, "peace": 1, "pleasant": 1,
    "polite": 1, "possible": 1, "practical": 1, "proper": 1,
    "protect": 1, "pure": 1, "quiet": 1, "rational": 1,
    "reasonable": 1, "regular": 1, "relevant": 1, "reliable": 1,
    "resolve": 1, "respect": 1, "responsible": 1, "safe": 1,
    "satisfy": 1, "secure": 1, "sincere": 1, "smooth": 1, "solid": 1,
    "stable": 1, "steady": 1, "sufficient": 1, "suitable": 1,
    "support": 1, "thankful": 1, "timely": 1, "true": 1, "trust": 1,
    "useful": 1, "valid": 1, "warm": 1, "welcome": 1, "willing": 1,
    "wise": 1, "worthy": 1,

    # --- positive (+2) ---
    "affordable": 2, "advantage": 2, "appreciate": 2, "balanced": 2,
    "beneficial": 2, "benefit": 2, "bright": 2, "capable": 2,
    "cheerful": 2, "clever": 2, "confident": 2, "constructive": 2,
    "convenient": 2, "creative": 2, "dedicated": 2, "delight": 2,
    "eager": 2, "effective": 2, "efficient": 2, "empower": 2,
    "encourage": 2, "encouraging": 2, "energetic": 2, "enjoy": 2,
    "enjoyable": 2, "enthusiastic": 2, "ethical": 2, "exciting": 2,
    "favor": 2, "favorable": 2, "fortunate": 2, "friendly": 2,
    "fulfilling": 2, "fun": 2, "generous": 2, "glad": 2, "good": 2,
    "graceful": 2, "grateful": 2, "grow": 2, "growth": 2, "happy": 2,
    "harmony": 2, "healthy": 2, "helpful": 2, "hero": 2, "honest": 2,
    "ideal": 2, "impressive": 2, "innovative": 2, "inspire": 2,
    "inspiring": 2, "integrity": 2, "intelligent": 2, "joy": 2,
    "joyful": 2, "kind": 2, "leading": 2, "lively": 2, "loyal": 2,
    "merit": 2, "motivate": 2, "motivating": 2, "nice": 2,
    "nurture": 2, "optimistic": 2, "organized": 2, "passionate": 2,
    "peaceful": 2, "perfect": 2, "pleased": 2, "positive": 2,
    "powerful": 2, "precious": 2, "productive": 2, "progress": 2,
    "promise": 2, "promising": 2, "proud": 2, "quality": 2,
    "recommend": 2, "refresh": 2, "refreshing": 2, "rejoice": 2,
    "remarkable": 2, "resilient": 2, "resourceful": 2, "reward": 2,
    "rewarding": 2, "robust": 2, "satisfied": 2, "save": 2,
    "skillful": 2, "smart": 2, "solution": 2, "strength": 2,
    "strong": 2, "succeed": 2, "success": 2, "successful": 2,
    "sunny": 2, "superior": 2, "sustain": 2, "sustainable": 2,
    "thrive": 2, "thriving": 2, "transform": 2, "transparent": 2,
    "triumph": 2, "unique": 2, "uplift": 2, "uplifting": 2,
    "valuable": 2, "value": 2, "vibrant": 2, "victory": 2,
    "vital": 2, "win": 2, "wonderful": 2, "worthy": 2,

    # --- very positive (+3) ---
    "amazing": 3, "awesome": 3, "beautiful": 3, "best": 3,
    "blessing": 3, "bliss": 3, "booming": 3, "breakthrough": 3,
    "brilliant": 3, "celebrate": 3, "champion": 3, "charming": 3,
    "delightful": 3, "dream": 3, "easy": 3, "elegant": 3,
    "empower": 3, "enchanting": 3, "energize": 3, "enlighten": 3,
    "enthusiastic": 3, "epic": 3, "excellence": 3, "excellent": 3,
    "exceptional": 3, "exquisite": 3, "extraordinary": 3, "fabulous": 3,
    "fantastic": 3, "flourish": 3, "genius": 3, "glorious": 3,
    "gorgeous": 3, "grand": 3, "great": 3, "incredible": 3,
    "invaluable": 3, "joyous": 3, "jubilant": 3, "love": 3,
    "loving": 3, "magnificent": 3, "marvelous": 3, "masterpiece": 3,
    "miracle": 3, "outstanding": 3, "paradise": 3, "phenomenal": 3,
    "prosper": 3, "prosperity": 3, "radiant": 3, "remarkable": 3,
    "revolutionary": 3, "sensational": 3, "spectacular": 3,
    "splendid": 3, "stellar": 3, "stunning": 3, "superb": 3,
    "terrific": 3, "thrilling": 3, "top": 3, "tremendous": 3,
    "triumph": 3, "unbelievable": 3, "vibrant": 3, "victorious": 3,
    "wondrous": 3, "wow": 3,

    # --- strongly positive (+4) ---
    "adore": 4, "astonishing": 4, "beloved": 4, "blissful": 4,
    "breathtaking": 4, "dazzling": 4, "ecstatic": 4, "elated": 4,
    "empowered": 4, "euphoric": 4, "exhilarating": 4,
    "extraordinary": 4, "flawless": 4, "freedom": 4, "glowing": 4,
    "heavenly": 4, "heroic": 4, "impeccable": 4, "legendary": 4,
    "liberating": 4, "magical": 4, "majestic": 4, "monumental": 4,
    "overjoyed": 4, "perfection": 4, "priceless": 4, "supreme": 4,
    "transcendent": 4, "unforgettable": 4,

    # --- extremely positive (+5) ---
    "life-changing": 5, "life-saving": 5, "world-class": 5,
    "once-in-a-lifetime": 5,
}

# ──────────────────────────────────────────────────────────────────────
# Causal-phrase patterns used by detect_root_cause
# ──────────────────────────────────────────────────────────────────────
_CAUSAL_PATTERNS: List[re.Pattern] = [
    re.compile(r"\bbecause\s+(?:of\s+)?(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\bdue\s+to\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\breason\s+(?:is|being)\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\bcaused?\s+by\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\bresult\s+of\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\bstems?\s+from\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\black\s+of\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\babsence\s+of\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\bfailure\s+to\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\bthanks?\s+to\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\bowing\s+to\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\bas\s+a\s+result\s+of\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\bon\s+account\s+of\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\battributed?\s+to\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\bblamed?\s+on\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\broot\s+cause\s+(?:is|was|being)\s+(.+?)(?:\.|,|;|$)", re.I),
    re.compile(r"\bsince\s+(.+?)(?:\.|,|;|$)", re.I),
]

# ──────────────────────────────────────────────────────────────────────
# Inefficiency keyword groups
# ──────────────────────────────────────────────────────────────────────
_INEFFICIENCY_KEYWORDS: Dict[str, List[str]] = {
    "slow_process": ["slow", "delays", "delay", "waiting", "wait", "sluggish", "lag", "backlog"],
    "expensive": ["expensive", "costly", "overpriced", "unaffordable", "high cost", "high price", "exorbitant"],
    "complicated": ["complicated", "complex", "confusing", "convoluted", "bureaucratic", "red tape", "paperwork"],
    "broken_system": ["broken", "dysfunctional", "defunct", "non-functional", "not working", "malfunctioning"],
    "outdated": ["outdated", "obsolete", "archaic", "old-fashioned", "legacy", "antiquated"],
    "manual_process": ["manual", "paper-based", "handwritten", "offline", "non-digital", "pen and paper"],
    "fragmented": ["fragmented", "scattered", "disjointed", "siloed", "disconnected", "uncoordinated"],
    "inaccessible": ["inaccessible", "unavailable", "hard to find", "hard to reach", "limited access", "no access"],
    "unreliable": ["unreliable", "inconsistent", "unpredictable", "erratic", "untrustworthy"],
    "no_transparency": ["no transparency", "opaque", "hidden charges", "hidden fees", "no information", "no accountability"],
    "monopoly": ["monopoly", "cartel", "no competition", "single provider", "no alternative", "no choice"],
    "middlemen": ["middlemen", "middleman", "intermediary", "broker", "agent", "commission"],
    "bureaucracy": ["bureaucracy", "red tape", "government", "officials", "permits", "approvals", "clearance"],
    "corruption": ["corruption", "bribery", "bribe", "kickback", "under the table", "nepotism", "favouritism"],
    "lack_of_awareness": ["lack of awareness", "no awareness", "ignorance", "misinformation", "no education", "unaware"],
    "poor_quality": ["poor quality", "substandard", "inferior", "low quality", "adulterated", "counterfeit", "fake"],
    "no_accountability": ["no accountability", "unaccountable", "impunity", "no oversight", "no regulation"],
}

# ──────────────────────────────────────────────────────────────────────
# Market-size & solvability keyword lists
# ──────────────────────────────────────────────────────────────────────
_MARKET_KEYWORDS: Dict[str, int] = {
    # Broad reach
    "everyone": 10, "everybody": 10, "all": 5, "millions": 10,
    "billion": 12, "crores": 10, "lakhs": 8, "daily": 8, "everyday": 8,
    "common": 7, "widespread": 9, "prevalent": 8, "universal": 10,
    "massive": 9, "huge": 8, "growing": 7, "booming": 8, "trending": 6,
    # Geography
    "india": 8, "indian": 8, "national": 7, "country": 6, "nationwide": 8,
    "urban": 6, "rural": 7, "semi-urban": 6, "tier-2": 6, "tier-3": 6,
    "metro": 5, "village": 6, "district": 5, "state": 5, "pan-india": 9,
    "global": 10, "international": 9, "world": 8, "asia": 7,
    # Demographics
    "students": 7, "workers": 7, "farmers": 7, "women": 7, "youth": 7,
    "children": 7, "elderly": 6, "seniors": 6, "families": 7,
    "parents": 6, "mothers": 6, "homemakers": 6, "professionals": 6,
    "employees": 6, "migrants": 6, "freelancers": 5, "gig": 5,
    "drivers": 5, "teachers": 5, "doctors": 5, "patients": 6,
    "consumers": 7, "citizens": 7, "taxpayers": 6, "voters": 5,
    "entrepreneurs": 5, "startups": 5, "small business": 6, "msme": 7,
    "sme": 6, "vendors": 5, "shopkeepers": 5, "retailers": 5,
    # Frequency
    "annual": 4, "monthly": 5, "weekly": 6, "hourly": 7, "constant": 7,
    "regular": 5, "frequent": 6, "recurring": 6, "persistent": 6,
    "chronic": 6, "ongoing": 5, "continuous": 6, "perpetual": 6,
    # Intensity
    "urgent": 7, "critical": 8, "essential": 7, "necessary": 6,
    "mandatory": 6, "vital": 7, "important": 5, "significant": 6,
    "serious": 6, "severe": 7, "acute": 7, "emergency": 8,
}

_SOLVABILITY_POSITIVE: Dict[str, int] = {
    "app": 8, "application": 7, "platform": 8, "digital": 7,
    "automate": 9, "automated": 9, "automation": 9, "ai": 10,
    "artificial intelligence": 10, "machine learning": 9, "ml": 9,
    "marketplace": 8, "website": 6, "online": 6, "internet": 5,
    "mobile": 7, "software": 7, "algorithm": 8, "data": 6,
    "analytics": 7, "cloud": 7, "iot": 8, "sensor": 7, "gps": 7,
    "blockchain": 7, "api": 6, "dashboard": 6, "portal": 6,
    "chatbot": 7, "notification": 5, "sms": 5, "whatsapp": 6,
    "upi": 7, "payment": 6, "fintech": 8, "edtech": 7, "healthtech": 7,
    "agritech": 7, "saas": 7, "database": 5, "tracking": 6,
    "monitoring": 6, "real-time": 7, "scalable": 8, "open-source": 6,
    "crowdsource": 6, "peer-to-peer": 7, "p2p": 7, "decentralized": 7,
    "e-commerce": 7, "logistics": 6, "delivery": 6, "drone": 7,
    "robotics": 8, "3d-printing": 7, "telemedicine": 8, "telehealth": 8,
    "wearable": 7, "biometric": 7, "satellite": 7, "remote": 5,
    "virtual": 6, "augmented": 6, "gamification": 6,
}

_SOLVABILITY_NEGATIVE: Dict[str, int] = {
    "policy": 6, "regulation": 6, "regulatory": 6, "legislation": 7,
    "law": 5, "legal": 5, "government": 5, "political": 6,
    "cultural": 7, "tradition": 6, "traditional": 5, "mindset": 6,
    "infrastructure": 7, "roads": 6, "electricity": 6, "power grid": 7,
    "sanitation": 5, "sewage": 5, "water supply": 6, "physical": 4,
    "hardware": 5, "construction": 5, "land": 5, "climate": 6,
    "weather": 4, "geographical": 5, "terrain": 5, "remote area": 6,
    "literacy": 5, "illiteracy": 6, "poverty": 6, "caste": 7,
    "religion": 7, "communal": 7, "bureaucracy": 6,
}


# ======================================================================
# Main Engine
# ======================================================================

class NLPEngine:
    """Pure-Python NLP engine for problem analysis.

    Every public method is deterministic and relies only on the Python
    standard library.
    """

    # ------------------------------------------------------------------
    # Tokenisation & pre-processing
    # ------------------------------------------------------------------

    _TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z'-]*[a-zA-Z]|[a-zA-Z]")

    def tokenize(self, text: str) -> List[str]:
        """Regex-based word splitter; returns lowercased tokens."""
        return [t.lower() for t in self._TOKEN_RE.findall(text)]

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove tokens present in the hardcoded stopword set."""
        return [t for t in tokens if t not in _STOPWORDS]

    # ------------------------------------------------------------------
    # Sentiment analysis
    # ------------------------------------------------------------------

    def analyze_sentiment(self, text: str) -> float:
        """Lexicon-based sentiment score normalised to [−1.0, 1.0].

        Each token is looked up in the AFINN-style dictionary. The raw
        sum is divided by the number of *scored* tokens to obtain a
        per-word average, then clamped to [−1, 1].
        """
        tokens = self.tokenize(text)
        total = 0.0
        hits = 0
        for tok in tokens:
            if tok in _SENTIMENT_LEXICON:
                total += _SENTIMENT_LEXICON[tok]
                hits += 1
        if hits == 0:
            return 0.0
        avg = total / hits            # range approx −5…+5
        normalised = avg / 5.0        # → −1…+1
        return max(-1.0, min(1.0, normalised))

    # ------------------------------------------------------------------
    # TF-IDF keyword extraction
    # ------------------------------------------------------------------

    def extract_keywords(
        self, text: str, top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """Return *top_n* keywords ranked by a simplified TF-IDF score.

        *TF* is computed from the input text itself.  Because we do not
        have a true corpus, *IDF* is approximated using a heuristic:
        common English words (stopwords) get a low IDF; everything else
        gets a higher one.
        """
        tokens = self.tokenize(text)
        content = self.remove_stopwords(tokens)
        if not content:
            return []

        total = len(content)
        tf: Dict[str, float] = {}
        for tok in content:
            tf[tok] = tf.get(tok, 0) + 1
        for tok in tf:
            tf[tok] /= total

        # Heuristic IDF: log(vocab_universe / estimated_doc_freq)
        vocab_universe = 100_000  # imagined corpus size
        scored: Dict[str, float] = {}
        for tok, freq in tf.items():
            # Words that are very short or very common get lower IDF
            est_df = 50_000 if len(tok) <= 3 else 5_000 if len(tok) <= 5 else 500
            idf = math.log(vocab_universe / (1 + est_df))
            scored[tok] = freq * idf

        ranked = sorted(scored.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_n]

    # ------------------------------------------------------------------
    # Root-cause detection
    # ------------------------------------------------------------------

    def detect_root_cause(self, text: str) -> str:
        """Extract a root-cause clause from *text*.

        First tries explicit causal markers (''because'', ''due to'' …).
        Falls back to the top TF-IDF keyword cluster when no marker is
        found.
        """
        for pat in _CAUSAL_PATTERNS:
            m = pat.search(text)
            if m:
                clause = m.group(1).strip()
                # Clean trailing punctuation
                clause = clause.rstrip(".,;!?")
                if len(clause) > 5:
                    return clause

        # Fallback: synthesise a cause from top keywords
        kws = self.extract_keywords(text, top_n=5)
        if kws:
            return "Likely related to: " + ", ".join(k for k, _ in kws)
        return "No explicit root cause detected"

    # ------------------------------------------------------------------
    # Inefficiency detection
    # ------------------------------------------------------------------

    def detect_inefficiency(self, text: str) -> List[str]:
        """Return a list of inefficiency labels found in *text*."""
        lower = text.lower()
        found: List[str] = []
        for label, keywords in _INEFFICIENCY_KEYWORDS.items():
            for kw in keywords:
                if kw in lower:
                    found.append(label)
                    break  # one hit per category is enough
        return found

    # ------------------------------------------------------------------
    # Market-size estimation
    # ------------------------------------------------------------------

    def estimate_market_size(self, text: str, category: str = "General") -> float:
        """Return a score in [0, 100] indicating addressable market size.

        The score is the sum of keyword contributions (capped at 100)
        multiplied by a category-specific weight.
        """
        lower = text.lower()
        raw = 0
        for kw, pts in _MARKET_KEYWORDS.items():
            if kw in lower:
                raw += pts
        weight = CATEGORY_WEIGHTS.get(category, 1.0)
        return min(100.0, raw * weight)

    # ------------------------------------------------------------------
    # Solvability estimation
    # ------------------------------------------------------------------

    def estimate_solvability(self, text: str) -> float:
        """Return a score in [0, 100] indicating technology solvability.

        Positive keywords (app, AI, platform …) push the score up;
        negative keywords (policy, infrastructure …) pull it down.
        """
        lower = text.lower()
        pos = sum(pts for kw, pts in _SOLVABILITY_POSITIVE.items() if kw in lower)
        neg = sum(pts for kw, pts in _SOLVABILITY_NEGATIVE.items() if kw in lower)
        raw = 50 + pos - neg  # start from a neutral 50
        return max(0.0, min(100.0, float(raw)))

    # ------------------------------------------------------------------
    # Frustration scoring (private helper)
    # ------------------------------------------------------------------

    def _compute_frustration(self, text: str) -> float:
        """Derive a frustration intensity score in [0, 100].

        Uses a combination of negative-sentiment density, exclamation
        marks, question marks, ALL-CAPS words, and keyword hits.
        """
        tokens = self.tokenize(text)
        if not tokens:
            return 0.0

        # Negative sentiment density
        neg_count = sum(1 for t in tokens if _SENTIMENT_LEXICON.get(t, 0) < 0)
        neg_density = neg_count / len(tokens)

        # Punctuation signals
        exclamations = text.count("!")
        questions = text.count("?")

        # CAPS words (frustration proxy)
        caps = sum(1 for w in text.split() if w.isupper() and len(w) > 1)

        # Strong negative words
        strong = sum(1 for t in tokens if _SENTIMENT_LEXICON.get(t, 0) <= -3)

        score = (
            neg_density * 40
            + min(exclamations, 5) * 3
            + min(questions, 3) * 2
            + min(caps, 5) * 2
            + strong * 4
        )
        return max(0.0, min(100.0, score))

    # ------------------------------------------------------------------
    # Overall score
    # ------------------------------------------------------------------

    def compute_overall_score(
        self,
        frustration: float,
        market: float,
        solvability: float,
        sentiment: float,
    ) -> float:
        """Weighted composite score.

        Formula:
            0.35 × frustration + 0.30 × market + 0.20 × solvability
            + 0.15 × (1 − sentiment) × 50
        """
        sent_component = (1 - sentiment) * 50
        return (
            0.35 * frustration
            + 0.30 * market
            + 0.20 * solvability
            + 0.15 * sent_component
        )

    # ------------------------------------------------------------------
    # Full analysis pipeline
    # ------------------------------------------------------------------

    def analyze_problem(
        self, text: str, category: str = "General"
    ) -> Dict[str, Any]:
        """Run the complete analysis pipeline and return a result dict.

        Keys returned
        -------------
        sentiment, frustration_score, market_score, solvability_score,
        overall_score, root_cause, inefficiencies, keywords, category
        """
        combined = text  # operate on raw text

        sentiment = self.analyze_sentiment(combined)
        frustration = self._compute_frustration(combined)
        market = self.estimate_market_size(combined, category)
        solvability = self.estimate_solvability(combined)
        overall = self.compute_overall_score(
            frustration, market, solvability, sentiment
        )
        root_cause = self.detect_root_cause(combined)
        inefficiencies = self.detect_inefficiency(combined)
        keywords = self.extract_keywords(combined, top_n=10)

        return {
            "sentiment": round(sentiment, 4),
            "frustration_score": round(frustration, 2),
            "market_score": round(market, 2),
            "solvability_score": round(solvability, 2),
            "overall_score": round(overall, 2),
            "root_cause": root_cause,
            "inefficiencies": inefficiencies,
            "keywords": [(k, round(s, 4)) for k, s in keywords],
            "category": category,
        }


# ──────────────────────────────────────────────────────────────────────
# Quick smoke test when run directly
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = NLPEngine()
    sample = (
        "Public hospitals in India are a nightmare. The queues are "
        "terrible, doctors are overworked, and medicines are expensive. "
        "Patients suffer because of lack of accountability and broken "
        "infrastructure. We need a digital platform to fix this!"
    )
    result = engine.analyze_problem(sample, category="Health")
    for key, val in result.items():
        print(f"{key:>20}: {val}")
