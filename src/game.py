"""
Main game module that implements the core game loop and ties together all components.
"""

import asyncio
import logging
from typing import Optional
import argparse

from .core import Player, StoryLoader
from .combat import CombatManager
from .ui import Display, Colors, Animations
from .systems import (
    voting_system, 
    save_manager,
    event_dispatcher,
    plugin_manager,
    CombatEvent,
    StoryEvent
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Game:
    def __init__(self):
        self.player = Player()
        self.story_loader = StoryLoader()
        self.combat_manager = CombatManager()
        self.display = Display()
        
        # Initialize game state
        self.current_scene = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize game systems and load plugins."""
        logger.info("Initializing game systems...")
        
        # Load and initialize plugins
        await plugin_manager.load_all_plugins()
        
        logger.info("Game systems initialized")
        
    async def start(self):
        """Start the game loop."""
        await self.initialize()
        self.is_running = True
        
        # Load or create new game
        if save_manager.has_save():
            if await self.display.prompt_yes_no("Load saved game?"):
                save_manager.load_game(self.player)
        
        if not self.current_scene:
            self.current_scene = self.story_loader.get_starting_scene()
            
            # Dispatch game start event
            await event_dispatcher.dispatch(
                StoryEvent(
                    name="game_start",
                    scene_id=self.current_scene["id"],
                    context={"new_game": True}
                )
            )
        
        await self.game_loop()
        
    async def game_loop(self):
        """Main game loop."""
        while self.is_running:
            # Display current scene
            await self.display.show_scene(self.current_scene)
            
            # Get available choices
            choices = self.story_loader.get_choices(self.current_scene)
            
            # Handle combat if present
            if self.combat_manager.is_combat_scene(self.current_scene):
                await self.handle_combat()
                continue
                
            # Get player choice (with voting if multiplayer)
            choice = await self.get_player_choice(choices)
            
            # Dispatch choice event
            choice_event = StoryEvent(
                name="story_choice",
                scene_id=self.current_scene["id"],
                choice_made=choice,
                context={"choices": choices}
            )
            await event_dispatcher.dispatch(choice_event)
            
            if not choice_event.cancelled:
                # Process choice and get next scene
                self.current_scene = self.story_loader.process_choice(choice)
                
                # Save game after each choice
                save_manager.save_game(self.player)
                
                # Check for game over
                if self.story_loader.is_ending(self.current_scene):
                    await self.handle_ending()
                    break
                
    async def get_player_choice(self, choices):
        """Get player choice, using voting system if multiplayer."""
        if voting_system.is_multiplayer():
            return await voting_system.get_voted_choice(choices)
        return await self.display.get_choice(choices)
        
    async def handle_combat(self):
        """Handle combat encounters."""
        # Dispatch combat start event
        combat_event = CombatEvent(
            name="combat_start",
            attacker="player",
            defender=self.current_scene.get("enemy", "unknown"),
            context=self.current_scene
        )
        await event_dispatcher.dispatch(combat_event)
        
        if not combat_event.cancelled:
            result = await self.combat_manager.run_combat(
                self.player,
                self.current_scene,
                self.display
            )
            
            # Dispatch combat end event
            await event_dispatcher.dispatch(
                CombatEvent(
                    name="combat_end",
                    attacker="player",
                    defender=self.current_scene.get("enemy", "unknown"),
                    context={"winner": "player" if result.player_survived else "enemy"}
                )
            )
            
            if not result.player_survived:
                await self.handle_game_over()
            self.current_scene = result.next_scene
        
    async def handle_ending(self):
        """Handle reaching an ending."""
        await event_dispatcher.dispatch(
            StoryEvent(
                name="game_end",
                scene_id=self.current_scene["id"],
                context={"ending_type": self.current_scene.get("ending_type", "unknown")}
            )
        )
        
        await self.display.show_ending(self.current_scene)
        self.is_running = False
        
    async def handle_game_over(self):
        """Handle player death / game over."""
        await event_dispatcher.dispatch(
            StoryEvent(
                name="game_over",
                scene_id=self.current_scene["id"],
                context={"cause": "death"}
            )
        )
        
        await self.display.show_game_over()
        if await self.display.prompt_yes_no("Load last save?"):
            save_manager.load_game(self.player)
        else:
            self.is_running = False

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Json2RPGDesu - A kawaii text-based RPG")
    parser.add_argument("--multiplayer", action="store_true", help="Enable multiplayer mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--story", type=str, help="Path to custom story file")
    return parser.parse_args()

def main():
    """Entry point for the game."""
    args = parse_args()
    
    # Configure logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set up game configuration
    if args.multiplayer:
        voting_system.enable_multiplayer()
    
    if args.story:
        StoryLoader.set_story_path(args.story)
    
    # Start the game
    game = Game()
    asyncio.run(game.start())

if __name__ == "__main__":
    main() 