"""
auto_dictionary_tests.py — pytest unit tests for auto_dictionary.py

Run on Mac:
    cd ~/Developer/pymonologue/Pythonista
    pytest auto_dictionary_tests.py -v
"""

import pytest
import tempfile
import os
from auto_dictionary import (
    looks_like_proper_noun, extract_capitalized_words, suggest_new_words,
    load_dictionary, save_dictionary, approve_word, dismiss_word,
    add_pending, get_approved_list, process_transcription,
    DEFAULT_DICTIONARY
)


class TestLooksLikeProperNoun:
    """Tests for the proper noun heuristic."""

    def test_name_like_juliet(self):
        assert looks_like_proper_noun('Juliet') is True

    def test_name_like_norah(self):
        assert looks_like_proper_noun('Norah') is True

    def test_product_name(self):
        assert looks_like_proper_noun('MagX') is True

    def test_company_name(self):
        assert looks_like_proper_noun('Apple') is True

    def test_acronym_ignored(self):
        assert looks_like_proper_noun('API') is False
        assert looks_like_proper_noun('DM') is False
        assert looks_like_proper_noun('URL') is False

    def test_all_caps_ignored(self):
        assert looks_like_proper_noun('HTTP') is False

    def test_numbers_ignored(self):
        assert looks_like_proper_noun('2024') is False

    def test_single_letter_ignored(self):
        assert looks_like_proper_noun('A') is False

    def test_lowercase_ignored(self):
        assert looks_like_proper_noun('hello') is False

    def test_common_words_ignored(self):
        assert looks_like_proper_noun('The') is False
        assert looks_like_proper_noun('After') is False
        assert looks_like_proper_noun('Before') is False
        assert looks_like_proper_noun('This') is False

    def test_empty_string(self):
        assert looks_like_proper_noun('') is False

    def test_none_raises(self):
        with pytest.raises(TypeError):
            looks_like_proper_noun(None)


class TestExtractCapitalizedWords:
    """Tests for capitalized word extraction."""

    def test_single_capitalized(self):
        assert extract_capitalized_words('Juliet is here') == ['Juliet']

    def test_multiple_capitalized(self):
        result = extract_capitalized_words('Juliet and Norah went to MagX')
        assert 'Juliet' in result
        assert 'Norah' in result
        assert 'MagX' in result

    def test_deduplicates_in_order(self):
        result = extract_capitalized_words('Juliet Juliet Juliet')
        assert result == ['Juliet']

    def test_ignores_lowercase(self):
        result = extract_capitalized_words('hello world')
        assert result == []

    def test_ignores_acronyms(self):
        result = extract_capitalized_words('I use API and DM')
        assert 'API' not in result
        assert 'DM' not in result
        assert result == []

    def test_strips_punctuation(self):
        result = extract_capitalized_words('Hello, world!')
        assert 'Hello' in result
        assert 'world' not in result

    def test_empty_string(self):
        assert extract_capitalized_words('') == []


class TestSuggestNewWords:
    """Tests for word suggestion logic."""

    def test_suggests_unknown_proper_nouns(self):
        known = ['Juliet', 'Norah']
        text = 'Juliet and Ezra went to MagX'
        suggestions = suggest_new_words(text, known)
        assert 'Ezra' in suggestions
        assert 'MagX' in suggestions
        assert 'Juliet' not in suggestions
        assert 'Norah' not in suggestions

    def test_case_insensitive_dedup(self):
        known = ['Juliet']
        text = 'juliet and JULIET'
        suggestions = suggest_new_words(text, known)
        assert suggestions == []

    def test_empty_known(self):
        text = 'Juliet Norah Ezra'
        suggestions = suggest_new_words(text, [])
        assert len(suggestions) == 3

    def test_all_known(self):
        known = ['Juliet', 'Norah', 'Ezra']
        text = 'Juliet Norah Ezra'
        suggestions = suggest_new_words(text, known)
        assert suggestions == []


class TestStorage:
    """Tests for JSON dictionary storage."""

    def test_save_and_load(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name

        try:
            dictionary = {'approved': ['Juliet'], 'pending': ['Ezra']}
            save_dictionary(dictionary, path)
            loaded = load_dictionary(path)
            assert loaded == dictionary
        finally:
            os.unlink(path)

    def test_load_nonexistent_returns_default(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        os.unlink(path)

        loaded = load_dictionary(path)
        assert loaded == DEFAULT_DICTIONARY


class TestApproveWord:
    """Tests for word approval."""

    def test_approve_adds_to_approved(self):
        dictionary = {'approved': [], 'pending': ['Ezra']}
        result = approve_word(dictionary, 'Ezra')
        assert 'Ezra' in result['approved']
        assert 'Ezra' not in result['pending']

    def test_approve_removes_from_pending(self):
        dictionary = {'approved': ['Juliet'], 'pending': ['Ezra', 'Liam']}
        result = approve_word(dictionary, 'Ezra')
        assert 'Ezra' in result['approved']
        assert 'Ezra' not in result['pending']
        assert 'Liam' in result['pending']

    def test_approve_idempotent(self):
        dictionary = {'approved': ['Juliet'], 'pending': []}
        result = approve_word(dictionary, 'Juliet')
        assert result['approved'].count('Juliet') == 1


class TestDismissWord:
    """Tests for word dismissal."""

    def test_dismiss_removes_from_pending(self):
        dictionary = {'approved': [], 'pending': ['Ezra', 'Liam']}
        result = dismiss_word(dictionary, 'Ezra')
        assert 'Ezra' not in result['pending']
        assert 'Liam' in result['pending']

    def test_dismiss_does_not_affect_approved(self):
        dictionary = {'approved': ['Juliet'], 'pending': []}
        result = dismiss_word(dictionary, 'Juliet')
        assert 'Juliet' in result['approved']


class TestGetApprovedList:
    """Tests for getting sorted vocabulary list."""

    def test_sorts_alphabetically(self):
        dictionary = {'approved': ['Norah', 'Juliet', 'Ezra'], 'pending': []}
        result = get_approved_list(dictionary)
        assert result == ['Ezra', 'Juliet', 'Norah']

    def test_empty(self):
        dictionary = {'approved': [], 'pending': []}
        result = get_approved_list(dictionary)
        assert result == []


class TestProcessTranscription:
    """Tests for transcription processing integration."""

    def test_finds_new_words(self):
        dictionary = {'approved': ['Juliet'], 'pending': []}
        text = 'Juliet and Ezra were working on MagX'
        result_dict, suggestions = process_transcription(text, dictionary)
        assert 'Ezra' in suggestions
        assert 'MagX' in suggestions
        assert 'Juliet' not in suggestions
        assert 'Ezra' in result_dict['pending']

    def test_no_duplicates_in_pending(self):
        dictionary = {'approved': [], 'pending': []}
        text = 'Juliet Juliet Juliet'
        result_dict, suggestions = process_transcription(text, dictionary)
        assert result_dict['pending'].count('Juliet') == 1
