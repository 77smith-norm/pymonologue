import ui

import keyboard_style

try:
    import keyboard
except ImportError:
    keyboard = None


class PunctuationRow(ui.View):
    def __init__(self, symbols=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.symbols = list(symbols or ('.', ',', '?', '!', "'"))
        self.flex = 'W'
        self.background_color = 'clear'
        self.buttons = []

        for symbol in self.symbols:
            button = ui.Button(title=symbol)
            button.background_color = keyboard_style.DARK_BG_3
            button.tint_color = keyboard_style.FG_WHITE
            button.corner_radius = keyboard_style.BUTTON_RADIUS
            button.font = (keyboard_style.FONT_BOLD, keyboard_style.FONT_SIZE_MEDIUM)
            button.action = self._insert_symbol
            self.buttons.append(button)
            self.add_subview(button)

    def layout(self):
        if not self.buttons:
            return

        gap = 6
        width = max(0, self.width - (gap * (len(self.buttons) - 1))) / len(self.buttons)
        for index, button in enumerate(self.buttons):
            x = index * (width + gap)
            button.frame = (x, 0, width, self.height)

    def _insert_symbol(self, sender):
        if keyboard is not None:
            if hasattr(keyboard, 'play_input_click'):
                keyboard.play_input_click()
            keyboard.insert_text(sender.title)
