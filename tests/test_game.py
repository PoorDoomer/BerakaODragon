"""
Tests for the game module.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from src.game import Game
from src.core import Player, StoryLoader
from src.combat import CombatManager
from src.ui import Display
from src.systems import voting_system, save_manager

@pytest.fixture
def game():
    return Game()

@pytest.fixture
def mock_display():
    display = Mock(spec=Display)
    # Make async methods return coroutines
    display.show_scene = asyncio.coroutine(lambda x: None)
    display.get_choice = asyncio.coroutine(lambda x: "choice1")
    display.prompt_yes_no = asyncio.coroutine(lambda x: False)
    return display

@pytest.mark.asyncio
async def test_game_initialization(game):
    """Test game object initialization."""
    assert isinstance(game.player, Player)
    assert isinstance(game.story_loader, StoryLoader)
    assert isinstance(game.combat_manager, CombatManager)
    assert isinstance(game.display, Display)
    assert game.current_scene is None
    assert game.is_running is False

@pytest.mark.asyncio
async def test_game_start_new_game(game, mock_display):
    """Test starting a new game."""
    game.display = mock_display
    
    # Mock save manager to have no save
    with patch.object(save_manager, 'has_save', return_value=False):
        # Mock story loader to return a starting scene
        mock_scene = {"id": "start", "text": "Start scene"}
        with patch.object(game.story_loader, 'get_starting_scene', return_value=mock_scene):
            # Stop the game after one loop
            async def mock_game_loop():
                game.is_running = False
            game.game_loop = mock_game_loop
            
            await game.start()
            
            assert game.current_scene == mock_scene

@pytest.mark.asyncio
async def test_get_player_choice_single_player(game, mock_display):
    """Test getting player choice in single player mode."""
    game.display = mock_display
    choices = ["choice1", "choice2"]
    
    # Mock voting system to return single player mode
    with patch.object(voting_system, 'is_multiplayer', return_value=False):
        choice = await game.get_player_choice(choices)
        assert choice == "choice1"
        game.display.get_choice.assert_called_once_with(choices)

@pytest.mark.asyncio
async def test_handle_ending(game, mock_display):
    """Test handling game ending."""
    game.display = mock_display
    game.is_running = True
    mock_scene = {"id": "ending", "text": "Ending scene"}
    
    await game.handle_ending()
    
    assert not game.is_running
    game.display.show_ending.assert_called_once_with(mock_scene) 