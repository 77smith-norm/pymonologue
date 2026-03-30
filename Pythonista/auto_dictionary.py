"""
auto_dictionary.py — Custom vocabulary manager for PyMonologue.

Inspired by Monologue's "Auto Dictionary" feature.
Learns proper nouns (names, product names, acronyms) from transcribed text
to improve future transcription accuracy.

Usage:
1. After transcription, call suggest_new_words()
2. Review suggestions
3. Approve or dismiss via approve_word() / dismiss_word()
4. Save dictionary to disk
"""

import json
import os
import re
from typing import Optional

DEFAULT_DICT_PATH = 'pymonologue_dictionary.json'

# Words that look like proper nouns but shouldn't be auto-added
SKIP_PATTERNS = [
    r'^[A-Z]{2,}$',   # All-caps acronyms (DM, API, URL)
    r'^\d+$',          # Pure numbers
    r'^[^a-zA-Z]+$',  # No letters at all
]


def looks_like_proper_noun(word: str) -> bool:
    """
    Heuristic: does this word look like a proper noun?

    - Capitalized (not first position in sentence)
    - Not an acronym
    - Not a number
    - Has letters

    Raises:
        TypeError: if word is None
    """
    if word is None:
        raise TypeError("word cannot be None")
    if not word or len(word) < 2:
        return False

    # Skip pure numbers
    if re.match(r'^\d+$', word):
        return False

    # Skip all-caps acronyms
    if re.match(r'^[A-Z]{2,}$', word):
        return False

    # Skip words with no alphabetic characters
    if not re.search(r'[a-zA-Z]', word):
        return False

    # Must have capital letter somewhere (not just first char)
    has_capital = any(c.isupper() for c in word)
    if not has_capital:
        return False

    # Skip if it's just a capitalized common word
    common_words = {
        'the', 'and', 'but', 'for', 'nor', 'or', 'so', 'yet',
        'after', 'before', 'from', 'into', 'over', 'under',
        'this', 'that', 'these', 'those',
    }
    if word.lower() in common_words:
        return False

    return True


def extract_capitalized_words(text: str) -> list[str]:
    """
    Extract all capitalized words from text.
    Returns unique words in order of appearance.
    """
    words = text.split()
    seen = set()
    result = []
    for word in words:
        # Strip punctuation
        cleaned = re.sub(r'^[^\w]+|[^\w]+$', '', word)
        if cleaned and cleaned not in seen and looks_like_proper_noun(cleaned):
            seen.add(cleaned)
            result.append(cleaned)
    return result


def suggest_new_words(transcribed: str, known_words: list[str]) -> list[str]:
    """
    Return words in transcribed text that look like proper nouns but aren't known.

    Args:
        transcribed: The raw transcribed text
        known_words: List of already-known vocabulary words

    Returns:
        List of new word suggestions (unique, in order of appearance)
    """
    known_lower = {w.lower() for w in known_words}
    capitalized = extract_capitalized_words(transcribed)
    suggestions = [w for w in capitalized if w.lower() not in known_lower]
    return suggestions


# --- Storage ---

DEFAULT_DICTIONARY = {
    'approved': ['Juliet', 'Norah', 'Ezra', 'Liam', 'MagX'],
    'pending': [],  # Suggested but not yet approved
}


def load_dictionary(path: Optional[str] = None) -> dict:
    """Load dictionary from JSON file."""
    path = path or DEFAULT_DICT_PATH
    if not os.path.exists(path):
        return DEFAULT_DICTIONARY.copy()
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_dictionary(dictionary: dict, path: Optional[str] = None) -> None:
    """Save dictionary to JSON file."""
    path = path or DEFAULT_DICT_PATH
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, indent=2, ensure_ascii=False)


def approve_word(dictionary: dict, word: str) -> dict:
    """
    Move a word from pending to approved.
    Also removes from pending if present.
    """
    if word not in dictionary['approved']:
        dictionary['approved'].append(word)
    if word in dictionary['pending']:
        dictionary['pending'].remove(word)
    return dictionary


def dismiss_word(dictionary: dict, word: str) -> dict:
    """
    Remove a word from pending (reject the suggestion).
    Does not affect approved words.
    """
    if word in dictionary['pending']:
        dictionary['pending'].remove(word)
    return dictionary


def add_pending(dictionary: dict, word: str) -> dict:
    """Add a word to pending suggestions."""
    if word not in dictionary['pending'] and word not in dictionary['approved']:
        dictionary['pending'].append(word)
    return dictionary


def get_approved_list(dictionary: dict) -> list[str]:
    """Get sorted list of all approved vocabulary words."""
    return sorted(dictionary.get('approved', []), key=str.lower)


# --- Integration with transcription ---

def process_transcription(transcribed: str, dictionary: Optional[dict] = None) -> tuple[str, dict, list[str]]:
    """
    After a transcription, check for new words and update dictionary.

    Returns:
        (dictionary, new_suggestions)
    """
    if dictionary is None:
        dictionary = load_dictionary()

    suggestions = suggest_new_words(transcribed, dictionary.get('approved', []))
    for word in suggestions:
        add_pending(dictionary, word)

    return dictionary, suggestions


if __name__ == '__main__':
    # Demo
    text = "Juliet was working on the MagX project with Norah and Ezra"
    dictionary = DEFAULT_DICTIONARY.copy()

    suggestions = suggest_new_words(text, dictionary['approved'])
    print(f"Text: {text!r}")
    print(f"Suggestions: {suggestions}")

    # Approve
    for word in suggestions:
        approve_word(dictionary, word)
    print(f"Approved: {dictionary['approved']}")
