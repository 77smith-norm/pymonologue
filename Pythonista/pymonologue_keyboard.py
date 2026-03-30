"""
pymonologue_keyboard.py — Main entry point for PyMonologue custom keyboard.

Phase 1 keeps the device-only unknowns as smoke tests. The UI is complete,
but the voice pipeline stops at a placeholder transcript until Russell verifies:
- SFSpeechRecognizer via objc_util in keyboard context
- sound.Recorder in keyboard context
- keyboard.insert_text() in target apps
"""

from pathlib import Path
import sys

import auto_dictionary
import context_tags
import keyboard
import speech_recognizer
import text_normalizer
import ui

_THIS_DIR = Path(__file__).resolve().parent
_UI_DIR = _THIS_DIR / 'ui'
if str(_UI_DIR) not in sys.path:
    sys.path.insert(0, str(_UI_DIR))

import keyboard_style
from punctuation_row import PunctuationRow
from slash_menu import SlashMenuView
from tag_selector import TagSelectorView
from voice_button import VoiceButton

VOICE_PLACEHOLDER = 'voice recording smoke test pending'

_tag_context = context_tags.TagContext()
_is_recording = False
_keyboard_view = None


class PyMonologueKeyboardView(ui.View):
    def __init__(self):
        super().__init__(frame=(0, 0, 320, keyboard_style.KEYBOARD_HEIGHT))
        self.flex = 'WH'
        self.background_color = keyboard_style.DARK_BG
        self.name = 'PyMonologue'
        self.active_overlay = None

        self.tags_button = self._make_button('TAGS', _on_tags_button_tap)
        self.slash_button = self._make_button('/', _on_slash_button_tap)
        self.voice_button = VoiceButton(action=_on_voice_button_tap)
        self.punctuation_row = PunctuationRow()
        self.abc_button = self._make_button('ABC', self._switch_to_abc)
        self.space_button = self._make_button('M', self._insert_space)
        self.return_button = self._make_button('return', self._insert_return)

        for subview in [
            self.tags_button,
            self.slash_button,
            self.voice_button,
            self.punctuation_row,
            self.abc_button,
            self.space_button,
            self.return_button,
        ]:
            self.add_subview(subview)

    def layout(self):
        width = self.width or 320
        height = self.height or keyboard_style.KEYBOARD_HEIGHT
        padding = 12
        top_height = 34
        bottom_height = 44

        self.tags_button.frame = (padding, 10, 70, top_height)
        self.slash_button.frame = (self.tags_button.x + self.tags_button.width + 8, 10, 32, top_height)

        punctuation_width = min(210, width * 0.52)
        self.punctuation_row.frame = (width - padding - punctuation_width, 10, punctuation_width, top_height)

        voice_width = min(width - (padding * 2), 248)
        voice_height = min(124, max(96, height - 120))
        self.voice_button.frame = ((width - voice_width) / 2.0, 58, voice_width, voice_height)

        bottom_y = height - bottom_height - 12
        self.abc_button.frame = (padding, bottom_y, 64, bottom_height)
        self.return_button.frame = (width - padding - 82, bottom_y, 82, bottom_height)
        space_x = self.abc_button.x + self.abc_button.width + 10
        space_width = self.return_button.x - 10 - space_x
        self.space_button.frame = (space_x, bottom_y, space_width, bottom_height)

        if self.active_overlay is not None:
            self.active_overlay.frame = self.bounds

    def show_overlay(self, overlay):
        if self.active_overlay is not None:
            self.active_overlay.remove_from_superview()
        self.active_overlay = overlay
        overlay.frame = self.bounds
        overlay.flex = 'WH'
        self.add_subview(overlay)
        self.bring_to_front(overlay)

    def clear_overlay(self):
        self.active_overlay = None

    def _make_button(self, title, action):
        button = ui.Button(title=title)
        button.background_color = keyboard_style.DARK_BG_3
        button.tint_color = keyboard_style.FG_WHITE
        button.corner_radius = keyboard_style.BUTTON_RADIUS
        button.font = (keyboard_style.FONT_BOLD, keyboard_style.FONT_SIZE_SMALL)
        button.action = action
        return button

    def _switch_to_abc(self, sender):
        if hasattr(keyboard, 'set_view'):
            keyboard.set_view(None)

    def _insert_space(self, sender):
        _insert_text(' ')

    def _insert_return(self, sender):
        _insert_text('\n')


# --- Voice button callbacks ---

def _on_voice_button_tap(view):
    global _is_recording

    if not _is_recording:
        _start_recording()
    else:
        _stop_and_transcribe()


def _start_recording():
    global _is_recording
    _is_recording = True
    if _keyboard_view is not None:
        _keyboard_view.voice_button.set_recording(True)


def _stop_and_transcribe():
    global _is_recording
    _is_recording = False
    if _keyboard_view is not None:
        _keyboard_view.voice_button.set_recording(False)

    raw_text = VOICE_PLACEHOLDER
    cleaned = text_normalizer.normalize(raw_text)
    auto_dictionary.process_transcription(cleaned)
    final_text = context_tags.prepend_tags(cleaned, _tag_context.get_current_tags())
    _insert_text(final_text)


# --- Tag selector callbacks ---

def _on_tags_button_tap(sender):
    if _keyboard_view is None:
        return

    selector = TagSelectorView(_tag_context, on_dismiss=_keyboard_view.clear_overlay)
    _keyboard_view.show_overlay(selector)


# --- Slash command callbacks ---

def _on_slash_button_tap(sender):
    if _keyboard_view is None:
        return

    menu = SlashMenuView(on_dismiss=_keyboard_view.clear_overlay)
    _keyboard_view.show_overlay(menu)


# --- UI Setup ---

def _insert_text(text):
    if hasattr(keyboard, 'play_input_click'):
        keyboard.play_input_click()
    keyboard.insert_text(text)


def create_keyboard_view():
    global _keyboard_view
    _keyboard_view = PyMonologueKeyboardView()
    return _keyboard_view


# --- Module entry point ---

def main():
    v = create_keyboard_view()
    keyboard.set_view(v, mode='expanded')


if __name__ == '__main__':
    print('PyMonologue Keyboard')
    print('=' * 40)
    print('This script is a Pythonista custom keyboard.')
    print('To use it:')
    print('1. Open Pythonista -> Settings -> Keyboards')
    print('2. Add the Pythonista keyboard')
    print('3. Enable Full Access')
    print('4. Set this script as the keyboard script')
    print('5. In any app, switch to PyMonologue keyboard')
    print()
    print('Phase 1 status: UI complete, smoke tests pending on device.')
    print('Run the smoke tests in SPEC.md and docs/TESTING.md on iPhone 11 Pro Max.')
