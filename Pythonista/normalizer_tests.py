"""
normalizer_tests.py — pytest unit tests for text_normalizer.py

Run on Mac:
    cd ~/Developer/pymonologue/Pythonista
    pytest normalizer_tests.py -v
"""

import pytest
from text_normalizer import normalize, remove_fillers


class TestNormalize:
    """Tests for the main normalize() function."""

    def test_strips_urls(self):
        # URL is stripped, not preserved
        assert normalize("check https://example.com for details") == "Check for details."

    def test_strips_http_url(self):
        assert normalize("visit http://test.com now") == "Visit now."

    def test_strips_phone_numbers(self):
        assert normalize("call 555-123-4567 tomorrow") == "Call tomorrow."

    def test_strips_phone_dots(self):
        assert normalize("phone 555.123.4567") == "Phone."

    def test_strips_phone_plain(self):
        assert normalize("number is 5551234567") == "Number is."

    def test_collapse_whitespace(self):
        assert normalize("lots    of   spaces") == "Lots of spaces."

    def test_collapse_leading_trailing_whitespace(self):
        assert normalize("  hello world  ") == "Hello world."

    def test_collapse_repeated_fillers(self):
        # "um um um" (3 occurrences) collapses to "um" (1 occurrence)
        # Non-consecutive "um" at end is preserved
        assert normalize("um um um this is ridiculous um") == "Um this is ridiculous um."

    def test_preserve_single_filler(self):
        # A single "um" is preserved (not a repetition)
        assert normalize("um I think we should go") == "Um I think we should go."

    def test_preserve_two_fillers(self):
        # Two "ums" is not a repetition of 3+, preserved
        assert normalize("um um I think we should go") == "Um um I think we should go."

    def test_capitalize_first_letter(self):
        assert normalize("hello world") == "Hello world."

    def test_preserve_already_capitalized(self):
        assert normalize("Hello world") == "Hello world."

    def test_add_period_if_missing(self):
        assert normalize("hello world") == "Hello world."

    def test_preserve_existing_period(self):
        assert normalize("hello world.") == "Hello world."

    def test_preserve_existing_question_mark(self):
        assert normalize("is this working?") == "Is this working?"

    def test_preserve_existing_exclamation(self):
        assert normalize("it works!") == "It works!"

    def test_empty_string(self):
        assert normalize("") == ""

    def test_none_raises(self):
        with pytest.raises(TypeError):
            normalize(None)

    def test_single_word_no_punct(self):
        assert normalize("hello") == "Hello."

    def test_single_word_with_punct(self):
        assert normalize("hello!") == "Hello!"

    def test_unicode_preserved(self):
        assert normalize("café") == "Café."

    def test_multiple_urls(self):
        assert normalize("visit https://a.com and http://b.com ok") == "Visit and ok."

    def test_mixed_cleanup(self):
        # Full realistic example
        text = "um so I was thinking maybe we could like go to the store later"
        result = normalize(text)
        assert result.startswith("Um so I was thinking")
        assert "um um" not in result.lower()
        assert result.endswith(".")

    def test_realistic_dictation(self):
        """Most realistic voice dictation example."""
        text = ("um so I was thinking maybe we could like refactor the auth "
                "module and also um yeah check if the expiry handling is "
                "being handled correctly I mean yeah")
        result = normalize(text)
        # Should be readable, starts capitalized, ends with period
        assert result[0].isupper()
        assert result[-1] in '.!?'


class TestRemoveFillers:
    """Tests for the aggressive filler removal option."""

    def test_remove_fillers_aggressive(self):
        text = "um I like sort of want to go"
        result = remove_fillers(text, aggressive=True)
        assert "um" not in result.lower()
        assert "sort of" not in result.lower()

    def test_remove_fillers_non_aggressive(self):
        # Non-aggressive: no-op (no collapse, no removal)
        text = "um um um yes"
        result = remove_fillers(text, aggressive=False)
        assert "um um um" in result.lower()
