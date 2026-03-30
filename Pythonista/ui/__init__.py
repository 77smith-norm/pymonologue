"""
ui/ — PyMonologue keyboard UI components.

Each module contains a ui.View subclass for a specific keyboard element.
"""

from .keyboard_style import TEAL, DARK_BG, DARK_FG, FONT_SIZE_LARGE, FONT_SIZE_SMALL

# Re-export for convenience
__all__ = [
    'TEAL',
    'DARK_BG',
    'DARK_FG',
    'FONT_SIZE_LARGE',
    'FONT_SIZE_SMALL',
]
