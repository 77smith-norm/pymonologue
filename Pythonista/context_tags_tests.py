"""
context_tags_tests.py — pytest unit tests for context_tags.py

Run on Mac:
    cd ~/Developer/pymonologue/Pythonista
    pytest context_tags_tests.py -v
"""

import pytest
import tempfile
import os
from context_tags import (
    parse_tags, strip_tags, prepend_tags, build_tag_string,
    load_tags, save_tags, add_recent_project, add_recent_task,
    TagContext, DEFAULT_TAGS, VALID_PRIORITIES
)


class TestParseTags:
    """Tests for tag parsing."""

    def test_parse_project_tag(self):
        assert parse_tags('[project:cgmclaw]') == {'project': 'cgmclaw'}

    def test_parse_task_tag(self):
        assert parse_tags('[task:debug]') == {'task': 'debug'}

    def test_parse_priority_tag(self):
        assert parse_tags('[priority:urgent]') == {'priority': 'urgent'}

    def test_parse_freeform_tag(self):
        assert parse_tags('[note]') == {'note': ''}

    def test_parse_multiple_tags(self):
        text = '[project:cgmclaw][task:debug] the OAuth flow is broken'
        assert parse_tags(text) == {'project': 'cgmclaw', 'task': 'debug'}

    def test_parse_all_types(self):
        text = '[project:cgmclaw][task:debug][priority:urgent][note]'
        assert parse_tags(text) == {
            'project': 'cgmclaw',
            'task': 'debug',
            'priority': 'urgent',
            'note': ''
        }

    def test_parse_no_tags(self):
        assert parse_tags('hello world') == {}

    def test_parse_empty_string(self):
        assert parse_tags('') == {}

    def test_parse_partial_tag(self):
        # Unclosed bracket — should not match
        assert parse_tags('[project') == {}

    def test_parse_mixed_content(self):
        text = '[project:cgmclaw] the OAuth token [task:debug] is broken'
        assert parse_tags(text) == {'project': 'cgmclaw', 'task': 'debug'}

    def test_case_sensitive_keys(self):
        assert parse_tags('[PROJECT:cgmclaw]') == {}


class TestStripTags:
    """Tests for tag removal."""

    def test_strip_single_tag(self):
        assert strip_tags('[project:cgmclaw]') == ''

    def test_strip_with_content(self):
        result = strip_tags('[project:cgmclaw] the OAuth flow')
        assert result == 'the OAuth flow'

    def test_strip_multiple_tags(self):
        result = strip_tags('[project:cgmclaw][task:debug] the OAuth flow')
        assert result == 'the OAuth flow'

    def test_strip_no_tags(self):
        assert strip_tags('hello world') == 'hello world'

    def test_strip_normalizes_whitespace(self):
        result = strip_tags('[project:cgmclaw]   hello world')
        assert result == 'hello world'


class TestPrependTags:
    """Tests for tag prepending."""

    def test_prepend_single_tag(self):
        result = prepend_tags('hello', {'project': 'cgmclaw'})
        assert result == '[project:cgmclaw] hello'

    def test_prepend_multiple_tags(self):
        tags = {'project': 'cgmclaw', 'task': 'debug'}
        result = prepend_tags('hello', tags)
        assert result == '[project:cgmclaw][task:debug] hello'

    def test_prepend_empty_tags(self):
        assert prepend_tags('hello', {}) == 'hello'

    def test_prepend_freeform_tag(self):
        result = prepend_tags('hello', {'note': ''})
        assert result == '[note] hello'


class TestBuildTagString:
    """Tests for building tag strings from components."""

    def test_project_only(self):
        assert build_tag_string(project='cgmclaw') == '[project:cgmclaw]'

    def test_project_and_task(self):
        assert build_tag_string(project='cgmclaw', task='debug') == '[project:cgmclaw][task:debug]'

    def test_all_components(self):
        result = build_tag_string(project='cgmclaw', task='debug', priority='urgent', note='oauth')
        assert 'project:cgmclaw' in result
        assert 'task:debug' in result
        assert 'priority:urgent' in result
        assert '[note:oauth]' not in result  # note is freeform (key=note, value=oauth → [oauth])
        assert '[oauth]' in result

    def test_invalid_priority_ignored(self):
        result = build_tag_string(priority='invalid')
        assert result == ''

    def test_normal_priority_omitted(self):
        result = build_tag_string(priority='normal')
        assert result == ''

    def test_empty(self):
        assert build_tag_string() == ''


class TestRecentLists:
    """Tests for recent-list management."""

    def test_add_project_to_empty(self):
        tags = {'recent_projects': []}
        result = add_recent_project(tags, 'cgmclaw')
        assert result['recent_projects'] == ['cgmclaw']

    def test_add_project_moves_to_front(self):
        tags = {'recent_projects': ['cgmclaw', 'normanctl']}
        result = add_recent_project(tags, 'cgmclaw')
        assert result['recent_projects'] == ['cgmclaw', 'normanctl']

    def test_add_project_deduplicates(self):
        tags = {'recent_projects': ['cgmclaw', 'normanctl']}
        result = add_recent_project(tags, 'cgmclaw')
        assert result['recent_projects'].count('cgmclaw') == 1

    def test_add_project_max_ten(self):
        tags = {'recent_projects': [f'proj{i}' for i in range(10)]}
        result = add_recent_project(tags, 'newproj')
        assert len(result['recent_projects']) == 10
        assert result['recent_projects'][0] == 'newproj'
        # proj9 (oldest) is dropped; proj0 through proj8 are kept
        assert 'proj8' in result['recent_projects']
        assert 'proj9' not in result['recent_projects']


class TestTagContext:
    """Tests for TagContext runtime state."""

    def test_default_state(self):
        ctx = TagContext()
        assert ctx.get_current_tags() == {}
        assert ctx.get_tag_string() == ''

    def test_set_project(self):
        ctx = TagContext()
        ctx.set_project('cgmclaw')
        assert ctx.current_project == 'cgmclaw'
        assert ctx.get_current_tags() == {'project': 'cgmclaw'}

    def test_set_task(self):
        ctx = TagContext()
        ctx.set_task('debug')
        assert ctx.current_task == 'debug'
        assert ctx.get_current_tags() == {'task': 'debug'}

    def test_set_priority_normal_omitted(self):
        ctx = TagContext()
        ctx.set_priority('normal')
        assert ctx.get_current_tags() == {}
        assert ctx.get_tag_string() == ''

    def test_set_priority_urgent(self):
        ctx = TagContext()
        ctx.set_priority('urgent')
        assert ctx.get_current_tags() == {'priority': 'urgent'}

    def test_set_priority_invalid_ignored(self):
        ctx = TagContext()
        ctx.set_priority('invalid')
        assert ctx.get_current_tags() == {}

    def test_full_context(self):
        ctx = TagContext()
        ctx.set_project('cgmclaw')
        ctx.set_task('debug')
        ctx.set_priority('urgent')
        ctx.set_note('oauth')
        tags = ctx.get_current_tags()
        assert tags['project'] == 'cgmclaw'
        assert tags['task'] == 'debug'
        assert tags['priority'] == 'urgent'
        assert 'oauth' in tags  # freeform

    def test_recent_projects_updated(self):
        ctx = TagContext({'recent_projects': [], 'recent_tasks': [], 'default_priority': 'normal'})
        ctx.set_project('cgmclaw')
        assert 'cgmclaw' in ctx.tags['recent_projects']


class TestStorage:
    """Tests for JSON storage."""

    def test_save_and_load(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name

        try:
            tags = {'recent_projects': ['cgmclaw'], 'recent_tasks': [], 'default_priority': 'normal'}
            save_tags(tags, path)
            loaded = load_tags(path)
            assert loaded == tags
        finally:
            os.unlink(path)

    def test_load_nonexistent_returns_default(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        os.unlink(path)

        loaded = load_tags(path)
        assert loaded == DEFAULT_TAGS
