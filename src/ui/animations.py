"""
Animations module for terminal-based visual effects.
"""

import sys
import time
from typing import List, Optional
import shutil
from .colors import color_manager

class AnimationFrame:
    """Represents a single frame in an animation."""
    
    def __init__(self, content: str, duration: float = 0.2):
        """
        Initialize animation frame.
        
        Args:
            content (str): Frame content
            duration (float): Frame duration in seconds
        """
        self.content = content
        self.duration = duration

class Animation:
    """Base class for terminal animations."""
    
    def __init__(self, frames: List[AnimationFrame]):
        """
        Initialize animation.
        
        Args:
            frames (List[AnimationFrame]): List of animation frames
        """
        self.frames = frames
        self.terminal_width = shutil.get_terminal_size().columns

    def play(self, loops: int = 1):
        """
        Play the animation.
        
        Args:
            loops (int): Number of times to loop (default: 1)
        """
        for _ in range(loops):
            for frame in self.frames:
                sys.stdout.write('\r' + ' ' * self.terminal_width)  # Clear line
                sys.stdout.write('\r' + frame.content)
                sys.stdout.flush()
                time.sleep(frame.duration)
        sys.stdout.write('\r' + ' ' * self.terminal_width + '\r')  # Clear final frame
        sys.stdout.flush()

class LoadingAnimation(Animation):
    """Loading animation with kawaii emoticons."""
    
    def __init__(self, text: str = "Loading", duration: float = 2.0):
        """
        Initialize loading animation.
        
        Args:
            text (str): Loading text
            duration (float): Total animation duration
        """
        emoticons = ["(o˘◡˘o)", "(✿◠‿◠)", "(｡･ω･｡)", "(uwu)", "(^•ω•^)", "(⌒‿⌒)"]
        frame_duration = duration / (len(emoticons) * 2)  # Each emoticon appears twice
        
        frames = []
        for emoticon in emoticons:
            colored_text = color_manager.theme_color('info', f"{emoticon} {text}...")
            frames.append(AnimationFrame(colored_text, frame_duration))
            
        super().__init__(frames)

class CombatAnimation:
    """Combat action animations."""
    
    @staticmethod
    def attack(attacker: str, defender: str, damage: int):
        """
        Create and play attack animation.
        
        Args:
            attacker (str): Attacker name
            defender (str): Defender name
            damage (int): Damage dealt
        """
        frames = [
            AnimationFrame(
                color_manager.theme_color('text', f"{attacker} (ﾉ*ΦωΦ)ﾉ✧ {defender}"),
                0.15
            ),
            AnimationFrame(
                color_manager.theme_color('warning', f"{attacker} ~(>_<~) {defender}"),
                0.15
            ),
            AnimationFrame(
                color_manager.theme_color('error', f"{attacker} ≧◉ᴥ◉≦ {defender}"),
                0.15
            ),
        ]
        
        animation = Animation(frames)
        animation.play()
        
        if damage > 0:
            print(color_manager.theme_color('error', f"Nyah! -{damage} HP!"))
        else:
            print(color_manager.theme_color('info', "UwU... Miss!"))

class ProgressAnimation:
    """Progress bar animation."""
    
    def __init__(self, total: int, width: int = 30):
        """
        Initialize progress bar.
        
        Args:
            total (int): Total steps
            width (int): Bar width in characters
        """
        self.total = total
        self.width = width
        self.current = 0

    def update(self, current: int):
        """
        Update progress bar.
        
        Args:
            current (int): Current progress
        """
        self.current = current
        percentage = (current / self.total) * 100
        filled = int((current / self.total) * self.width)
        
        bar = color_manager.theme_color('success', '✿' * filled)
        bar += color_manager.theme_color('text', '·' * (self.width - filled))
        print(f"\rProgress: [{bar}] {percentage:.1f}%", end='')
        sys.stdout.flush()

    def finish(self):
        """Complete the progress bar."""
        print()  # New line after progress bar

def clear_screen():
    """Clear the terminal screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_screen(text: str = "Loading", duration: float = 2.0):
    """
    Show a loading screen.
    
    Args:
        text (str): Loading text
        duration (float): Duration in seconds
    """
    animation = LoadingAnimation(text, duration)
    animation.play()

def transition_effect(effect: str = "fade"):
    """
    Show a screen transition effect.
    
    Args:
        effect (str): Effect type ('fade', 'slide', etc.)
    """
    if effect == "fade":
        chars = ["░", "▒", "▓", "█"]
        for char in chars + list(reversed(chars)):
            sys.stdout.write('\r' + char * shutil.get_terminal_size().columns)
            sys.stdout.flush()
            time.sleep(0.05)
        clear_screen() 