"""
context_tags.py — Lightweight tagging system for PyMonologue.

Tags are prepended to transcribed text to provide project/task context.

Format:
    [project:<name>]
    [task:<name>]
    [priority:<level>]   — urgent | normal | low
    [note]               — freeform, no colon

Example:
    [project:cgmclaw][task:debug] the OAuth token refresh is failing

Storage: JSON file in Pythonista documents directory.
"""

import json
import os
import re
from pathlib import Path
from typing import Optional

# --- Constants ---

DEFAULT_STORAGE_PATH = 'pymonologue_tags.json'

VALID_PRIORITIES = {'urgent', 'normal', 'low'}

# --- Tag parsing ---

TAG_PATTERN = re.compile(r'\[([a-z]+):([^\]]+)\]|\[([a-z]+)\]')
# Groups: (1=key, 2=value) or (3=freeform key) for tags without colon


def parse_tags(text: str) -> dict[str, str]:
    """
    Extract all tags from text.

    Returns a dict:
        {'project': 'cgmclaw', 'task': 'debug', 'note': 'something'}

    Freeform tags (no colon) get key = the tag text, value = ''.
    """
    result = {}
    for match in TAG_PATTERN.finditer(text):
        if match.group(1) is not None:
            # Has explicit key:value
            key, value = match.group(1), match.group(2)
            result[key] = value
        elif match.group(3) is not None:
            # Freeform tag [note]
            key = match.group(3)
            result[key] = ''
    return result


def strip_tags(text: str) -> str:
    """Remove all tags from text, leaving only the content."""
    return TAG_PATTERN.sub('', text).strip()


def prepend_tags(text: str, tags: dict[str, str]) -> str:
    """
    Prepend tags to text.

    Example:
        prepend_tags("hello world", {'project': 'cgmclaw', 'task': 'debug'})
        → "[project:cgmclaw][task:debug] hello world"
    """
    tag_str = ''
    for key, value in tags.items():
        if value:
            tag_str += f'[{key}:{value}]'
        else:
            tag_str += f'[{key}]'

    if tag_str:
        return tag_str + ' ' + text
    else:
        return text


def build_tag_string(project: Optional[str] = None,
                     task: Optional[str] = None,
                     priority: Optional[str] = None,
                     note: Optional[str] = None) -> str:
    """
    Build a tag string from individual components.

    Example:
        build_tag_string(project='cgmclaw', task='debug')
        → "[project:cgmclaw][task:debug]"

    Note: priority='normal' is the default and is omitted.
    """
    parts = []
    if project:
        parts.append(f'project:{project}')
    if task:
        parts.append(f'task:{task}')
    if priority and priority in VALID_PRIORITIES and priority != 'normal':
        parts.append(f'priority:{priority}')
    if note:
        parts.append(note)

    if not parts:
        return ''

    return '[' + ']['.join(parts) + ']'


# --- Storage ---

DEFAULT_TAGS = {
    'recent_projects': ['cgmclaw', 'normanctl', 'norman-world', 'paddock-ghost'],
    'recent_tasks': ['debug', 'build', 'plan', 'idea', 'review'],
    'default_priority': 'normal',
    'auto_dictionary': ['Juliet', 'Norah', 'Ezra', 'Liam'],
}


def load_tags(path: Optional[str] = None) -> dict:
    """Load tags from JSON storage file."""
    path = path or DEFAULT_STORAGE_PATH
    if not os.path.exists(path):
        return DEFAULT_TAGS.copy()
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_tags(tags: dict, path: Optional[str] = None) -> None:
    """Save tags to JSON storage file."""
    path = path or DEFAULT_STORAGE_PATH
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(tags, f, indent=2, ensure_ascii=False)


# --- Recent-list management ---

def add_recent_project(tags: dict, project: str) -> dict:
    """Add project to recent list (most recent first, max 10)."""
    recent = tags.get('recent_projects', [])
    if project in recent:
        recent.remove(project)
    recent.insert(0, project)
    tags['recent_projects'] = recent[:10]
    return tags


def add_recent_task(tags: dict, task: str) -> dict:
    """Add task to recent list (most recent first, max 10)."""
    recent = tags.get('recent_tasks', [])
    if task in recent:
        recent.remove(task)
    recent.insert(0, task)
    tags['recent_tasks'] = recent[:10]
    return tags


# --- Context tag state (runtime) ---

class TagContext:
    """
    Runtime tag state for the current keyboard session.

    Tracks the currently active tag (project, task, priority, note)
    that will be prepended to all transcribed text until changed.
    """

    def __init__(self, tags: Optional[dict] = None):
        self.tags = tags or DEFAULT_TAGS.copy()
        self.current_project: Optional[str] = None
        self.current_task: Optional[str] = None
        self.current_priority: str = 'normal'
        self.current_note: Optional[str] = None

    def set_project(self, project: Optional[str]) -> None:
        self.current_project = project
        if project:
            self.tags = add_recent_project(self.tags, project)

    def set_task(self, task: Optional[str]) -> None:
        self.current_task = task
        if task:
            self.tags = add_recent_task(self.tags, task)

    def set_priority(self, priority: str) -> None:
        if priority in VALID_PRIORITIES:
            self.current_priority = priority

    def set_note(self, note: Optional[str]) -> None:
        self.current_note = note

    def get_current_tags(self) -> dict[str, str]:
        """Get dict of current active tags."""
        result = {}
        if self.current_project:
            result['project'] = self.current_project
        if self.current_task:
            result['task'] = self.current_task
        if self.current_priority != 'normal':
            result['priority'] = self.current_priority
        if self.current_note:
            result[self.current_note] = ''
        return result

    def get_tag_string(self) -> str:
        """Get the current tag string for prepending."""
        tags = self.get_current_tags()
        if not tags:
            return ''
        return build_tag_string(
            project=self.current_project,
            task=self.current_task,
            priority=self.current_priority,
            note=self.current_note
        )


if __name__ == '__main__':
    # Demo
    ctx = TagContext()
    ctx.set_project('cgmclaw')
    ctx.set_task('debug')
    print(f"Tag string: {ctx.get_tag_string()!r}")
    print(f"Tags dict: {ctx.get_current_tags()}")

    text = "the OAuth flow is broken"
    tagged = prepend_tags(text, ctx.get_current_tags())
    print(f"Tagged: {tagged!r}")

    # Parse demo
    parsed = parse_tags("[project:cgmclaw][task:debug] the OAuth flow is broken")
    print(f"Parsed: {parsed}")
