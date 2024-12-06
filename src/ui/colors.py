"""
Colors module for managing terminal colors and styles.
"""

from colorama import Fore, Back, Style
from typing import Dict, Optional

class ColorScheme:
    """Color scheme configuration."""
    
    # Default color mappings
    COLORS = {
        'black': Fore.BLACK,
        'red': Fore.RED,
        'green': Fore.GREEN,
        'yellow': Fore.YELLOW,
        'blue': Fore.BLUE,
        'magenta': Fore.MAGENTA,
        'cyan': Fore.CYAN,
        'white': Fore.WHITE,
    }
    
    # Theme configurations
    THEMES = {
        'default': {
            'text': Fore.WHITE,
            'title': Fore.CYAN,
            'success': Fore.GREEN,
            'error': Fore.RED,
            'warning': Fore.YELLOW,
            'info': Fore.BLUE,
            'highlight': Fore.MAGENTA,
        },
        'kawaii': {
            'text': Fore.WHITE,
            'title': Fore.MAGENTA,
            'success': Fore.GREEN,
            'error': Fore.RED,
            'warning': Fore.YELLOW,
            'info': Fore.CYAN,
            'highlight': Fore.MAGENTA,
        }
    }

class ColorManager:
    """Manages color application and themes."""
    
    def __init__(self, theme: str = 'kawaii'):
        """
        Initialize color manager.
        
        Args:
            theme (str): Theme name to use
        """
        self.theme = theme
        self.current_theme = ColorScheme.THEMES[theme]

    def colorize(self, text: str, color: str, style: Optional[str] = None) -> str:
        """
        Apply color to text.
        
        Args:
            text (str): Text to colorize
            color (str): Color name to apply
            style (Optional[str]): Style to apply (e.g., 'bold', 'dim')
            
        Returns:
            str: Colorized text
        """
        color_code = ColorScheme.COLORS.get(color, '')
        style_code = ''
        
        if style == 'bold':
            style_code = Style.BRIGHT
        elif style == 'dim':
            style_code = Style.DIM
            
        return f"{color_code}{style_code}{text}{Style.RESET_ALL}"

    def theme_color(self, category: str, text: str) -> str:
        """
        Apply theme color to text.
        
        Args:
            category (str): Color category from theme
            text (str): Text to colorize
            
        Returns:
            str: Themed text
        """
        color = self.current_theme.get(category, Fore.WHITE)
        return f"{color}{text}{Style.RESET_ALL}"

    def create_gradient(self, text: str, colors: list) -> str:
        """
        Create a gradient effect across text.
        
        Args:
            text (str): Text to apply gradient to
            colors (list): List of color names to use
            
        Returns:
            str: Text with gradient effect
        """
        if not colors:
            return text
            
        segments = len(colors)
        chars_per_segment = max(1, len(text) // segments)
        result = ""
        
        for i, char in enumerate(text):
            color_index = min(i // chars_per_segment, len(colors) - 1)
            color = ColorScheme.COLORS.get(colors[color_index], '')
            result += f"{color}{char}"
            
        return result + Style.RESET_ALL

    @staticmethod
    def get_available_colors() -> Dict[str, str]:
        """Get dictionary of available colors."""
        return ColorScheme.COLORS.copy()

    @staticmethod
    def get_available_themes() -> Dict[str, Dict[str, str]]:
        """Get dictionary of available themes."""
        return ColorScheme.THEMES.copy()

# Create default color manager instance
color_manager = ColorManager()

# Convenience functions
def colorize(text: str, color: str, style: Optional[str] = None) -> str:
    """Convenience function to colorize text."""
    return color_manager.colorize(text, color, style)

def theme_color(category: str, text: str) -> str:
    """Convenience function to apply theme color."""
    return color_manager.theme_color(category, text) 