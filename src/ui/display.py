"""
Display module for rendering game content.
"""

import shutil
from typing import List, Dict, Optional
from ..core.player import Player
from .colors import color_manager
from .animations import clear_screen

class DisplayManager:
    """Manages game display and rendering."""
    
    def __init__(self):
        """Initialize display manager."""
        self.terminal_width = shutil.get_terminal_size().columns
        self.terminal_height = shutil.get_terminal_size().lines

    def create_box(self, content: str, width: Optional[int] = None, style: str = 'single') -> str:
        """
        Create a bordered box around content.
        
        Args:
            content (str): Content to put in box
            width (Optional[int]): Box width (default: auto)
            style (str): Border style ('single', 'double', 'rounded')
            
        Returns:
            str: Formatted box
        """
        borders = {
            'single': {'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘', 'h': '─', 'v': '│'},
            'double': {'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝', 'h': '═', 'v': '║'},
            'rounded': {'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯', 'h': '─', 'v': '│'}
        }
        
        border = borders.get(style, borders['single'])
        width = width or min(self.terminal_width - 4, max(len(line) for line in content.split('\n')) + 4)
        
        # Create top border
        box = [f"{border['tl']}{border['h'] * (width-2)}{border['tr']}"]
        
        # Add content lines
        for line in content.split('\n'):
            padding = width - 2 - len(line)
            box.append(f"{border['v']} {line}{' ' * padding} {border['v']}")
            
        # Add bottom border
        box.append(f"{border['bl']}{border['h'] * (width-2)}{border['br']}")
        
        return '\n'.join(box)

    def create_health_bar(self, current: int, maximum: int, width: int = 20) -> str:
        """
        Create a visual health bar.
        
        Args:
            current (int): Current health
            maximum (int): Maximum health
            width (int): Bar width
            
        Returns:
            str: Formatted health bar
        """
        filled = int((current / maximum) * width)
        bar = color_manager.theme_color('success', '♥' * filled)
        bar += color_manager.theme_color('error', '♡' * (width - filled))
        return f"[{bar}] {current}/{maximum} HP"

    def create_status_box(self, player: Player) -> str:
        """
        Create a status box for a player.
        
        Args:
            player (Player): Player to display status for
            
        Returns:
            str: Formatted status box
        """
        health_bar = self.create_health_bar(player.stats.health, player.stats.max_health)
        status_effects = ', '.join(player.status_effects) if player.status_effects else 'None'
        
        content = [
            color_manager.theme_color('title', player.name),
            health_bar,
            f"{color_manager.theme_color('info', 'Attack:')} {player.stats.attack} | "
            f"{color_manager.theme_color('info', 'Defense:')} {player.stats.defense}",
            f"{color_manager.theme_color('info', 'Status:')} {status_effects}"
        ]
        
        return self.create_box('\n'.join(content), style='rounded')

    def display_combat_log(self, messages: List[str], max_lines: int = 5):
        """
        Display combat log messages.
        
        Args:
            messages (List[str]): Messages to display
            max_lines (int): Maximum number of lines to show
        """
        title = color_manager.theme_color('title', "✿~ Combat Log ~✿")
        print(f"\n{title}")
        
        for msg in messages[-max_lines:]:
            print(msg)
            
        print(color_manager.theme_color('title', '~' * 20))

    def display_scene(self, scene: Dict):
        """
        Display a scene.
        
        Args:
            scene (Dict): Scene data to display
        """
        clear_screen()
        
        # Display title
        if 'title' in scene:
            title = self.create_box(
                color_manager.theme_color('title', scene['title']),
                style='double'
            )
            print(title + '\n')
        
        # Display description
        if 'description' in scene:
            desc = scene['description']
            if isinstance(desc, dict):
                text = desc.get('text', '')
                color = desc.get('color', 'text')
                print(color_manager.theme_color(color, text) + '\n')
            else:
                print(color_manager.theme_color('text', desc) + '\n')
        
        # Display choices
        if 'choices' in scene and scene['choices']:
            print(color_manager.theme_color('info', "\nAvailable Choices:"))
            for i, choice in enumerate(scene['choices'], 1):
                choice_text = choice.get('text', '')
                print(f"{color_manager.theme_color('warning', str(i))}. {choice_text}")

    def display_title_screen(self):
        """Display game title screen."""
        clear_screen()
        title_art = f"""
{color_manager.theme_color('title', '╔══════════════════════════════════════════════════════════╗')}
{color_manager.theme_color('title', '║                                                          ║')}
{color_manager.theme_color('title', '║         (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧  ')}{color_manager.theme_color('highlight', 'Json2RPGDesu')}{color_manager.theme_color('title', '   ✧ﾟ･: *ヽ(◕ヮ◕ヽ)    ║')}
{color_manager.theme_color('title', '║                                                          ║')}
{color_manager.theme_color('title', '║     ')}{color_manager.theme_color('info', 'A Kawaii Interactive Anime-Inspired Adventure!')}{color_manager.theme_color('title', '    ║')}
{color_manager.theme_color('title', '║                                                          ║')}
{color_manager.theme_color('title', '╚══════════════════════════════════════════════════════════╝')}
"""
        print(title_art)

    def display_game_over(self, victory: bool = False):
        """
        Display game over screen.
        
        Args:
            victory (bool): Whether the player won
        """
        clear_screen()
        if victory:
            message = "＼(^o^)／ Victory! ＼(^o^)／"
            color = 'success'
        else:
            message = "(╥﹏╥) Game Over (╥﹏╥)"
            color = 'error'
            
        box = self.create_box(
            color_manager.theme_color(color, message),
            style='double'
        )
        print('\n' * (self.terminal_height // 3))
        print(box)

# Create default display manager instance
display_manager = DisplayManager() 