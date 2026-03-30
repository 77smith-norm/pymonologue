"""
pymonologue_keyboard.py — PyMonologue custom keyboard for Pythonista.

This script runs resident in the Pythonista keyboard context.
Pythonista loads the module, executes it, and keeps it alive.
keyboard.set_view() MUST be called at load time (not behind __main__).

Reference: https://omz-software.com/pythonista/docs-3.4/py3/ios/keyboard.html
"""

import keyboard
import ui

# ─── Check environment ───────────────────────────────────────────────────────

_is_keyboard_context = keyboard.is_keyboard()

if _is_keyboard_context:
    # Running inside the Pythonista keyboard extension.
    # Build and install the custom UI immediately.
    import sys
    from pathlib import Path

    _THIS_DIR = Path(__file__).resolve().parent
    _UI_DIR = _THIS_DIR / 'ui'
    if str(_UI_DIR) not in sys.path:
        sys.path.insert(0, str(_UI_DIR))

    import sound
    import tempfile

    import auto_dictionary
    import context_tags
    import speech_recognizer
    import text_normalizer
    import keyboard_style
    from punctuation_row import PunctuationRow
    from slash_menu import SlashMenuView
    from tag_selector import TagSelectorView
    from voice_button import VoiceButton

    _tag_context = context_tags.TagContext()
    _is_recording = False
    _current_recorder = None
    _keyboard_view = None

    # ─── View ───────────────────────────────────────────────────────────────

    class PyMonologueKeyboardView(ui.View):
        """Custom keyboard view — replaces QWERTY area in 'expanded' mode."""

        def __init__(self):
            super().__init__(frame=(0, 0, 320, keyboard_style.KEYBOARD_HEIGHT))
            self.flex = 'WH'
            self.background_color = keyboard_style.DARK_BG
            self.name = 'PyMonologue'
            self.active_overlay = None

            # Row 1: TAGS, /, [punctuations]
            self.tags_button = self._make_button('TAGS', self._on_tags_tap)
            self.slash_button = self._make_button('/', self._on_slash_tap)
            self.punctuation_row = PunctuationRow()

            # Center: voice button
            self.voice_button = VoiceButton(action=self._on_voice_tap)

            # Row 3: ABC | SPACE | return
            self.abc_button = self._make_button('ABC', self._on_abc_tap)
            self.space_button = self._make_button('M', self._on_space_tap)
            self.return_button = self._make_button('return', self._on_return_tap)

            for sv in [
                self.tags_button,
                self.slash_button,
                self.punctuation_row,
                self.voice_button,
                self.abc_button,
                self.space_button,
                self.return_button,
            ]:
                self.add_subview(sv)

        # ── Keyboard callbacks (kb_* prefix — called by Pythonista) ─────────

        def kb_should_insert(self, text):
            """Called when QWERTY keys would insert text."""
            return text  # pass through

        def kb_text_changed(self):
            """Called when document text changes."""
            pass

        def kb_should_delete(self):
            """Called when backspace would fire."""
            return True

        # ── Layout ─────────────────────────────────────────────────────────

        def layout(self):
            w = self.width or 320
            h = self.height or keyboard_style.KEYBOARD_HEIGHT
            pad = 12
            row1_h = 34
            row3_h = 44

            # Row 1
            self.tags_button.frame = (pad, 10, 70, row1_h)
            self.slash_button.frame = (self.tags_button.x + self.tags_button.width + 8, 10, 32, row1_h)
            punct_w = min(210, w * 0.52)
            self.punctuation_row.frame = (w - pad - punct_w, 10, punct_w, row1_h)

            # Center: voice button
            voice_w = min(w - pad * 2, 248)
            voice_h = min(124, max(96, h - 120))
            self.voice_button.frame = ((w - voice_w) / 2.0, 58, voice_w, voice_h)

            # Row 3
            row3_y = h - row3_h - 12
            self.abc_button.frame = (pad, row3_y, 64, row3_h)
            self.return_button.frame = (w - pad - 82, row3_y, 82, row3_h)
            space_x = self.abc_button.x + self.abc_button.width + 10
            self.space_button.frame = (space_x, row3_y, self.return_button.x - 10 - space_x, row3_h)

            if self.active_overlay is not None:
                self.active_overlay.frame = self.bounds

        # ── Overlay helpers ─────────────────────────────────────────────────

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

        # ── Button helpers ─────────────────────────────────────────────────

        def _make_button(self, title, action):
            b = ui.Button(title=title)
            b.background_color = keyboard_style.DARK_BG_3
            b.tint_color = keyboard_style.FG_WHITE
            b.corner_radius = keyboard_style.BUTTON_RADIUS
            b.font = (keyboard_style.FONT_BOLD, keyboard_style.FONT_SIZE_SMALL)
            b.action = action
            return b

        # ── Button actions ──────────────────────────────────────────────────

        def _on_voice_tap(self, sender):
            _on_voice_button_tap()

        def _on_tags_tap(self, sender):
            selector = TagSelectorView(_tag_context, on_dismiss=self.clear_overlay)
            self.show_overlay(selector)

        def _on_slash_tap(self, sender):
            menu = SlashMenuView(on_dismiss=self.clear_overlay)
            self.show_overlay(menu)

        def _on_abc_tap(self, sender):
            if hasattr(keyboard, 'set_view'):
                keyboard.set_view(None)

        def _on_space_tap(self, sender):
            _insert_text(' ')

        def _on_return_tap(self, sender):
            _insert_text('\n')

    # ─── Voice pipeline ─────────────────────────────────────────────────────

    def _on_voice_button_tap():
        global _is_recording, _current_recorder

        if not _is_recording:
            _is_recording = True
            audio_path = tempfile.gettempdir() + '/pymonologue_rec.m4a'
            _current_recorder = sound.Recorder(audio_path)
            _current_recorder.record()
            _keyboard_view.voice_button.set_recording(True)
        else:
            _is_recording = False
            _keyboard_view.voice_button.set_recording(False)

            audio_path = tempfile.gettempdir() + '/pymonologue_rec.m4a'
            recognizer = speech_recognizer.SpeechRecognizer()
            raw_text = recognizer.transcribe(audio_path)

            if not raw_text:
                raw_text = '(no speech detected)'

            cleaned = text_normalizer.normalize(raw_text)
            auto_dictionary.process_transcription(cleaned)
            final_text = context_tags.prepend_tags(cleaned, _tag_context.get_current_tags())
            _insert_text(final_text)

    def _insert_text(text):
        if hasattr(keyboard, 'play_input_click'):
            keyboard.play_input_click()
        keyboard.insert_text(text)

    # ─── Install keyboard UI ─────────────────────────────────────────────────

    _keyboard_view = PyMonologueKeyboardView()
    keyboard.set_view(_keyboard_view, mode='expanded')

# ─── Not in keyboard context ────────────────────────────────────────────────
# Running as a normal script (e.g., from the editor).
# Show a setup guide instead.

else:
    print('PyMonologue Keyboard')
    print('=' * 40)
    print('This script is a Pythonista custom keyboard.')
    print()
    print('To use it:')
    print('1. Settings → General → Keyboard → Keyboards')
    print('2. Add New Keyboard → Pythonista')
    print('3. Enable Full Access (required for microphone)')
    print('4. Open Pythonista → Settings → Keyboards')
    print('5. Add this script as a Script Shortcut')
    print('6. In any app, tap the shortcut to activate')
