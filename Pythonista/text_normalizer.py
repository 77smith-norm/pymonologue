"""
text_normalizer.py — Basic text cleanup for voice transcription.

No AI. No network. Pure regex.

Philosophy: Norm (the AI consumer) handles raw speech fine.
This normalizer only cleans the most egregious transcription artifacts:
- URLs, phone numbers
- Excessive whitespace
- Obvious filler word repetition
- Missing capitalization / punctuation
"""

import re


def normalize(text: str) -> str:
    """
    Clean up transcribed text for readability.

    Operations (in order):
    1. Strip URLs
    2. Strip phone numbers
    3. Collapse repeated whitespace
    4. Collapse repeated filler words
    5. Capitalize first letter
    6. Ensure ending punctuation

    Raises:
        TypeError: if text is None
    """
    if text is None:
        raise TypeError("text cannot be None")
    if not text:
        return text

    # 1. Strip URLs
    text = re.sub(r'https?://\S+', '', text)

    # 2. Strip phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text)

    # 3. Collapse repeated whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # 4. Collapse repeated filler words (um um um → um)
    # Only collapses 3+ repetitions. Two "ums" might be intentional.
    text = re.sub(
        r'\b(um|uh|like|you know|I mean)\b(?:\s+\1\b){2,}',
        r'\1',
        text,
        flags=re.IGNORECASE
    )

    # 5. Capitalize first letter
    text = text[0].upper() + text[1:]

    # 6. Ensure ending punctuation
    if text and text[-1] not in '.!?':
        text += '.'

    return text


# --- Filler word sets ---

COMMON_FILLERS = {'um', 'uh', 'like', 'you know', 'i mean', 'sort of', 'kind of'}


def remove_fillers(text: str, aggressive: bool = False) -> str:
    """
    Remove filler words from text.

    If aggressive=True, remove all occurrences of common fillers.
    If aggressive=False, only collapse consecutive repetitions.
    """
    if aggressive:
        pattern = r'\b(' + '|'.join(re.escape(f) for f in COMMON_FILLERS) + r')\b'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip()
        # Re-capitalize after removing first word
        if text:
            text = text[0].upper() + text[1:]
    else:
        # Just collapse repetitions (handled in normalize)
        pass
    return text


if __name__ == '__main__':
    # Quick demo
    examples = [
        "um so I was thinking maybe we could like go to the store later",
        "https://example.com is where I found this information",
        "call me at 555-123-4567 okay thanks",
        "        lots    of   spaces   here   ",
        "um um um this is getting ridiculous um",
        "hello world",  # no punctuation
        "",              # empty
    ]

    for ex in examples:
        print(f"IN:  {ex!r}")
        print(f"OUT: {normalize(ex)!r}")
        print()
