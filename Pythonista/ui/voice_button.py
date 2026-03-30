import ui

import keyboard_style


class VoiceButton(ui.View):
    def __init__(self, action=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action = action
        self.is_recording = False
        self.flex = 'WH'
        self.background_color = keyboard_style.DARK_BG_2
        self.corner_radius = keyboard_style.VOICE_BUTTON_RADIUS
        self.tint_color = keyboard_style.TEAL

        self.button = ui.Button()
        self.button.flex = 'WH'
        self.button.background_color = keyboard_style.TEAL
        self.button.tint_color = keyboard_style.FG_WHITE
        self.button.corner_radius = keyboard_style.VOICE_BUTTON_RADIUS
        self.button.font = (keyboard_style.FONT_BOLD, keyboard_style.FONT_SIZE_LARGE)
        self.button.title = '🎤 TAP TO TALK'
        self.button.action = self._did_tap
        self.add_subview(self.button)

    def layout(self):
        self.button.frame = self.bounds.inset(4, 4)

    def set_recording(self, recording):
        self.is_recording = recording
        self.tint_color = keyboard_style.RECORDING_RED if recording else keyboard_style.TEAL
        self.button.background_color = self.tint_color
        self.button.title = '■ RECORDING...' if recording else '🎤 TAP TO TALK'
        if recording:
            self._pulse_out()
        else:
            self.button.transform = ui.Transform.identity()

    def _did_tap(self, sender):
        if callable(self.action):
            self.action(self)

    def _pulse_out(self):
        if not self.is_recording:
            self.button.transform = ui.Transform.identity()
            return

        ui.animate(
            lambda: setattr(self.button, 'transform', ui.Transform.scale(1.03, 1.03)),
            duration=keyboard_style.PULSE_INTERVAL / 2.0,
            completion=self._pulse_in,
        )

    def _pulse_in(self):
        if not self.is_recording:
            self.button.transform = ui.Transform.identity()
            return

        ui.animate(
            lambda: setattr(self.button, 'transform', ui.Transform.identity()),
            duration=keyboard_style.PULSE_INTERVAL / 2.0,
            completion=self._pulse_out,
        )
