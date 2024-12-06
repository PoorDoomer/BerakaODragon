"""
UI module containing display and animation components.
"""

from .display import DisplayManager, display_manager
from .animations import (
    Animation,
    AnimationFrame,
    LoadingAnimation,
    CombatAnimation,
    ProgressAnimation,
    clear_screen,
    loading_screen,
    transition_effect
)
from .colors import ColorManager, ColorScheme, color_manager, colorize, theme_color

__all__ = [
    'DisplayManager',
    'display_manager',
    'Animation',
    'AnimationFrame',
    'LoadingAnimation',
    'CombatAnimation',
    'ProgressAnimation',
    'ColorManager',
    'ColorScheme',
    'color_manager',
    'colorize',
    'theme_color',
    'clear_screen',
    'loading_screen',
    'transition_effect',
] 