"""
Core module containing the main game components.
"""

from .player import Player, PlayerStats, Inventory
from .story_loader import StoryLoader, StoryValidationError

__all__ = [
    'Player',
    'PlayerStats',
    'Inventory',
    'StoryLoader',
    'StoryValidationError',
] 