import ui

import keyboard_style

try:
    import keyboard
except ImportError:
    keyboard = None


class SlashMenuView(ui.View):
    def __init__(self, commands=None, on_dismiss=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = list(commands or ('/new', '/model'))
        self.on_dismiss = on_dismiss
        self.flex = 'WH'
        self.background_color = keyboard_style.OVERLAY_BG

        self.panel = ui.View()
        self.panel.background_color = keyboard_style.PANEL_BG
        self.panel.corner_radius = 14
        self.panel.border_width = 1
        self.panel.border_color = keyboard_style.FG_DARK_GRAY
        self.add_subview(self.panel)

        self.buttons = []
        for command in self.commands:
            button = ui.Button(title=command)
            button.background_color = keyboard_style.DARK_BG_3
            button.tint_color = keyboard_style.FG_WHITE
            button.corner_radius = 10
            button.font = (keyboard_style.FONT_BOLD, keyboard_style.FONT_SIZE_MEDIUM)
            button.action = self._insert_command
            self.buttons.append(button)
            self.panel.add_subview(button)

    def layout(self):
        width = min(max(self.width - 40, 180), 220)
        height = 18 + len(self.buttons) * 42
        self.panel.frame = ((self.width - width) / 2.0, 24, width, height)

        y = 10
        for button in self.buttons:
            button.frame = (10, y, self.panel.width - 20, 32)
            y += 42

    def touch_began(self, touch):
        x, y = touch.location
        inside_panel = (
            self.panel.x <= x <= self.panel.x + self.panel.width and
            self.panel.y <= y <= self.panel.y + self.panel.height
        )
        if not inside_panel:
            self.dismiss()

    def dismiss(self):
        self.remove_from_superview()
        if callable(self.on_dismiss):
            self.on_dismiss()

    def _insert_command(self, sender):
        if keyboard is not None:
            if hasattr(keyboard, 'play_input_click'):
                keyboard.play_input_click()
            keyboard.insert_text(sender.title + ' ')
        self.dismiss()
