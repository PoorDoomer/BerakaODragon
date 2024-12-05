"""
Json2RPGDesu - A Kawaii Text-Based RPG Engine

This module implements a text-based RPG engine with a kawaii (cute) Japanese aesthetic.
It supports multiple players, combat, voting systems, and branching storylines loaded from JSON files.

Key Features:
- Colorful text-based UI with kawaii emoticons and styling
- Turn-based combat system with multiple actions
- Multi-player support with voting mechanics
- Story branching based on player choices
- Progress tracking and status displays
- Save/load functionality (planned)

Classes:
    Player: Represents a player character with stats and abilities
    Game: Main game engine that handles story progression and game mechanics

Dependencies:
    - colorama: For colored terminal output
    - json: For loading story files
    - random: For dice rolls and random selections
    - typing: For type hints
    - os: For screen clearing
    - time: For animations and delays
    - shutil: For terminal size detection
    - sys: For system operations
"""

import json
import random
from typing import List, Dict
import os
import time
from colorama import Fore, Style, init
import shutil
from time import sleep
import sys

# Initialize colorama
init(autoreset=True)


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def create_health_bar(current: int, maximum: int, width: int = 20) -> str:
    """
    Create a visual health bar with customizable width.
    
    Args:
        current: Current health value
        maximum: Maximum health value
        width: Width of the health bar in characters
        
    Returns:
        str: A formatted health bar string with hearts
    """
    # Using a more kawaii style for the health bar
    # Filled hearts for filled HP and hollow hearts for missing HP
    hearts_filled = int((current / maximum) * width)
    bar = f"[{Fore.MAGENTA}{'♥' * hearts_filled}{Fore.WHITE}{'♡' * (width - hearts_filled)}{Style.RESET_ALL}]"
    return f"{bar} {current}/{maximum} HP"


def create_status_box(player: 'Player') -> str:
    """
    Create a formatted status box displaying player information.
    
    Args:
        player: Player object containing stats to display
        
    Returns:
        str: A formatted string containing the player's status in a decorative box
    """
    terminal_width = shutil.get_terminal_size().columns
    box_width = min(terminal_width - 4, 50)

    health_bar = create_health_bar(player.health, player.max_health)
    status_effects = ', '.join(player.status_effects) if player.status_effects else 'None'
    
    # Add some kawaii borders and spacing
    box = [
        f"┏{'━' * box_width}┓",
        f"┃ {Fore.CYAN}{player.name:<{box_width-2}}{Style.RESET_ALL} ┃",
        f"┃ {health_bar:<{box_width-2}} ┃",
        f"┃ {Fore.YELLOW}Attack:{Style.RESET_ALL} {player.attack} | {Fore.GREEN}Defense:{Style.RESET_ALL} {player.defense:<{box_width-20}} ┃",
        f"┃ {Fore.MAGENTA}Status:{Style.RESET_ALL} {status_effects:<{box_width-10}} ┃",
        f"┗{'━' * box_width}┛"
    ]
    return '\n'.join(box)


def display_combat_log(messages: List[str], max_lines: int = 5):
    """
    Display a scrolling combat log with the most recent messages.
    
    Args:
        messages: List of combat messages to display
        max_lines: Maximum number of lines to show at once
    """
    # Use a more kawaii title and subtle pastel color
    print(f"\n{Fore.MAGENTA}✿~ Combat Log ~✿{Style.RESET_ALL}")
    for msg in messages[-max_lines:]:
        print(msg)
    print(f"{Fore.MAGENTA}{'~' * 20}{Style.RESET_ALL}\n")


def animate_attack(attacker: str, defender: str, damage: int):
    """
    Create a kawaii animation for attack sequences.
    
    Args:
        attacker: Name of the attacking character
        defender: Name of the defending character
        damage: Amount of damage dealt
    """
    # Replace the swords with more anime style emoticons
    # Let's make a small transition animation: (ﾉ*ФωФ)ﾉ✧ => ~(>_<~)
    frames = [
        f"{Fore.CYAN}{attacker}{Style.RESET_ALL} (ﾉ*ΦωΦ)ﾉ✧ {Fore.YELLOW}{defender}{Style.RESET_ALL}",
        f"{Fore.CYAN}{attacker}{Style.RESET_ALL}  ~(>_<~) {Fore.YELLOW}{defender}{Style.RESET_ALL}",
        f"{Fore.CYAN}{attacker}{Style.RESET_ALL}   ≧◉ᴥ◉≦ {Fore.YELLOW}{defender}{Style.RESET_ALL}",
    ]

    for frame in frames:
        clear_screen()
        print(frame)
        time.sleep(0.15)

    if damage > 0:
        print(f"{Fore.RED}Nyah! -{damage} HP!{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}UwU... Miss!{Style.RESET_ALL}")
    time.sleep(0.5)


def loading_animation(text="Loading", duration=2):
    """
    Display a cute loading animation with customizable text and duration.
    
    Args:
        text: Text to display during loading
        duration: Duration of the animation in seconds
    """
    chars = ["(o˘◡˘o)", "(✿◠‿◠)", "(｡･ω･｡)", "(uwu)", "(^•ω•^)", "(⌒‿⌒)"]
    delay = 0.2
    steps = int(duration / delay)

    for i in range(steps):
        char = chars[i % len(chars)]
        sys.stdout.write(f'\r{char} {Fore.MAGENTA}{text}...{Style.RESET_ALL} ')
        sys.stdout.flush()
        sleep(delay)
    sys.stdout.write('\r' + ' ' * (len(text) + 40) + '\r')
    sys.stdout.flush()


def display_title_screen():
    """Display the game's title screen with decorative ASCII art."""
    clear_screen()
    # Adding a pastel gradient-like feel is tricky in terminal,
    # but we can rely on ASCII art and pastel colors.
    title_art = f"""
{Fore.MAGENTA}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧  {Fore.CYAN}Json2RPGDesu{Fore.MAGENTA}   ✧ﾟ･: *ヽ(◕ヮ◕ヽ)    ║
║                                                          ║
║     {Fore.YELLOW}A Kawaii Interactive Anime-Inspired Adventure!{Fore.MAGENTA}    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
    print(title_art)


class Player:
    """
    Represents a player character in the game.
    
    Attributes:
        name (str): Player's name
        health (int): Current health points
        max_health (int): Maximum health points
        attack (int): Attack power
        defense (int): Defense power
        is_alive (bool): Whether the player is alive
        status_effects (List[str]): Active status effects
    """

    def __init__(self, name: str):
        """
        Initialize a new player.
        
        Args:
            name: The player's name
        """
        self.name = name
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.defense = 10
        self.is_alive = True
        self.status_effects = []

    def roll_dice(self, sides: int = 20) -> int:
        """
        Roll a dice with specified number of sides.
        
        Args:
            sides: Number of sides on the dice
            
        Returns:
            int: Random number between 1 and sides
        """
        return random.randint(1, sides)

    def take_damage(self, damage: int):
        """
        Apply damage to the player, accounting for defense.
        
        Args:
            damage: Amount of damage to apply
            
        Returns:
            int: Actual damage dealt after defense
        """
        actual_damage = max(0, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        self.is_alive = self.health > 0
        return actual_damage

    def heal(self, amount: int):
        """
        Heal the player for a specified amount.
        
        Args:
            amount: Amount of health to restore
        """
        self.health = min(self.max_health, self.health + amount)
        print(f"{Fore.GREEN}{self.name} drinks a magical potion and heals for {amount} HP! (✿◠‿◠){Style.RESET_ALL}")

    def apply_effect(self, effect: Dict):
        """
        Apply various effects to the player.
        
        Args:
            effect: Dictionary containing effect types and values
        """
        if "heal" in effect:
            self.heal(effect["heal"])
        if "buff_attack" in effect:
            self.attack += effect["buff_attack"]
            print(f"{Fore.YELLOW}{self.name}'s attack increased by {effect['buff_attack']}! (•̀ᴗ•́)و✧{Style.RESET_ALL}")
        if "buff_defense" in effect:
            self.defense += effect["buff_defense"]
            print(f"{Fore.BLUE}{self.name}'s defense increased by {effect['buff_defense']}! ᕙ(⇀‸↼‶)ᕗ{Style.RESET_ALL}")
        if "damage" in effect:
            damage = self.take_damage(effect["damage"])
            print(f"{Fore.RED}{self.name} took {damage} damage! ( >﹏< ){Style.RESET_ALL}")


class Game:
    """
    Main game engine class that handles game mechanics and story progression.
    
    Attributes:
        players (List[Player]): List of active players
        current_scene (str): ID of the current scene
        story_data (Dict): Loaded story data from JSON
        current_player_index (int): Index of the current player
        colors (Dict): Color mapping for text display
        combat_log (List[str]): List of combat messages
        terminal_width (int): Width of the terminal
        total_scenes (int): Total number of scenes in the story
        scenes_visited (set): Set of visited scene IDs
        hotkeys (Dict): Mapping of hotkeys to actions
    """

    def __init__(self):
        """Initialize a new game instance."""
        self.players: List[Player] = []
        self.current_scene = "start"
        self.story_data = {}
        self.current_player_index = 0
        self.colors = {}
        self.combat_log = []
        self.terminal_width = shutil.get_terminal_size().columns
        self.total_scenes = 0
        self.scenes_visited = set()
        self.hotkeys = {
            'a': 'attack',
            'd': 'defend',
            'h': 'heal',
            's': 'special'
        }

    def calculate_progress(self):
        """
        Calculate the player's progress through the game.
        
        Returns:
            float: Percentage of scenes visited
        """
        if not self.total_scenes:
            self.total_scenes = len([k for k in self.story_data.keys() if k != 'config'])
        progress = (len(self.scenes_visited) / self.total_scenes) * 100
        return min(100, progress)

    def display_progress_bar(self):
        """Display a kawaii-styled progress bar showing game completion."""
        progress = self.calculate_progress()
        width = 30
        filled = int((progress / 100) * width)
        # Use pastel flowers for progress filling
        bar = f"[{Fore.GREEN}{'✿' * filled}{Fore.WHITE}{'·' * (width - filled)}{Style.RESET_ALL}]"
        print(f"\nProgress: {bar} {progress:.1f}%")

    def display_main_menu(self):
        """
        Display the main menu and handle user input.
        
        Returns:
            bool: True if a new game should start, False otherwise
        """
        while True:
            display_title_screen()
            print(f"\n{Fore.CYAN}(⁀ᗢ⁀) {Style.RESET_ALL}Main Menu{Fore.CYAN} (⁀ᗢ⁀){Style.RESET_ALL}\n")
            menu_options = [
                (1, "New Game", "Start a new kawaii adventure!"),
                (2, "Load Game", "Load your previous journey (Coming Soon)"),
                (3, "Settings", "Tweak those kawaii settings (Coming Soon)"),
                (4, "Credits", "See who made this adorable adventure!"),
                (5, "Exit", "Goodbye! (｡•́︿•̀｡)")
            ]

            for num, title, desc in menu_options:
                print(f"\n{Fore.YELLOW}{num}.{Style.RESET_ALL} {Fore.MAGENTA}{title}{Style.RESET_ALL}")
                print(f"   {Fore.CYAN}{desc}{Style.RESET_ALL}")

            try:
                choice = input(f"\n{Fore.YELLOW}Enter your choice (1-5):{Style.RESET_ALL} ")
                if choice == "1":
                    loading_animation("Starting kawaii new game")
                    return self.start_new_game()
                elif choice == "2":
                    print("\n(；・∀・) Save/Load feature coming soon!")
                    input("Press Enter to continue...")
                elif choice == "3":
                    print("\n(｡╯︵╰｡) Settings feature coming soon!")
                    input("Press Enter to continue...")
                elif choice == "4":
                    self.display_credits()
                elif choice == "5":
                    print("\n(｡•́︿•̀｡) Thanks for playing!")
                    sys.exit()
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number!{Style.RESET_ALL}")
                sleep(1)

    def display_credits(self):
        """Display game credits with a cute style."""
        clear_screen()
        credits = f"""
{Fore.MAGENTA}╔══════════════════════════════════╗
║          {Fore.YELLOW}(✿◠‿◠) CREDITS (◠‿◠✿){Fore.MAGENTA}       ║
╠══════════════════════════════════╣
║                                  ║
║  {Fore.WHITE}Game Design & Development{Fore.MAGENTA}      ║
║    {Fore.YELLOW}Your Name Here{Fore.MAGENTA}                ║
║                                  ║
║  {Fore.WHITE}Story & Writing{Fore.MAGENTA}                ║
║    {Fore.YELLOW}Your Name Here{Fore.MAGENTA}                ║
║                                  ║
║  {Fore.WHITE}Special Thanks{Fore.MAGENTA}                 ║
║   {Fore.YELLOW}The Python Community{Fore.MAGENTA}          ║
║                                  ║
╚══════════════════════════════════╝{Style.RESET_ALL}

(｡◕‿◕｡) Arigatou Gozaimasu for playing!
"""
        print(credits)
        input("\nPress Enter to return to the main menu...")

    def start_new_game(self):
        """
        Initialize and start a new game.
        
        Returns:
            bool: True if game started successfully, False otherwise
        """
        if not self.load_story('story.json'):
            print(f"{Fore.RED}(>_<) Failed to load story file!{Style.RESET_ALL}")
            input("Press Enter to return to main menu...")
            return False
        self.initialize_players()
        return True

    def load_story(self, filename: str):
        """
        Load story data from a JSON file.
        
        Args:
            filename: Path to the story JSON file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.story_data = json.load(file)
                colors_config = self.story_data.get('config', {}).get('colors', {})
                self.colors = {}
                for key, value in colors_config.items():
                    self.colors[key] = self.get_color_code(value)
        except FileNotFoundError:
            print(f"(；′⌒`) Story file {filename} not found!")
            return False
        return True

    def get_color_code(self, color_name: str) -> str:
        """
        Convert color name to colorama color code.
        
        Args:
            color_name: Name of the color
            
        Returns:
            str: Colorama color code
        """
        color_mapping = {
            'black': Fore.BLACK,
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE,
            'reset': Style.RESET_ALL
        }
        return color_mapping.get(color_name.lower(), Fore.RESET)

    def initialize_players(self):
        """Initialize player characters for a new game."""
        num_players = 4  # Adjust the number of players as needed
        print("\n(◕‿◕) Let's name our brave heroes!")
        for i in range(num_players):
            while True:
                name = input(f"Enter name for Player {i+1}: ").strip()
                if name and not any(p.name == name for p in self.players):
                    self.players.append(Player(name))
                    print(f"{Fore.GREEN}Yay! {name} is ready for adventure! (★^O^★){Style.RESET_ALL}")
                    break
                print("(¬_¬) Please enter a unique, non-empty name...")

    def display_scene(self):
        """Display the current scene with description and available choices."""
        clear_screen()
        scene = self.story_data.get(self.current_scene, {})

        # Display title with a fancy border
        title = scene.get("title", "Current Scene")
        print(f"\n{Fore.CYAN}{'=' * 15} {title} {'=' * 15}{Style.RESET_ALL}\n")

        # Display description with text wrapping and preserving line breaks
        description = scene.get("description", {})
        if isinstance(description, dict):
            text = description.get("text", "")
            color_name = description.get("color", "")
            color_code = self.colors.get(color_name, Fore.RESET)
            text = self.replace_placeholders(text)

            paragraphs = text.split('\n')
            for paragraph in paragraphs:
                if paragraph.strip() == '':
                    print('')
                    continue

                words = paragraph.split()
                lines = []
                current_line = []
                current_length = 0

                for word in words:
                    word_length = len(word.encode('utf-8'))
                    if current_length + word_length + 1 <= self.terminal_width:
                        current_line.append(word)
                        current_length += word_length + 1
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = word_length

                if current_line:
                    lines.append(' '.join(current_line))

                for line in lines:
                    print(f"{color_code}{line}{Style.RESET_ALL}")
        else:
            print(description)

        # Display player status
        if self.players:
            print("\n(✿ ♥‿♥) === Party Status === (♥‿♥ ✿)")
            for player in self.players:
                print(create_status_box(player))

        # Display choices
        if "choices" in scene and scene["choices"]:
            print(f"\n{Fore.GREEN}Available Choices:{Style.RESET_ALL}")
            for i, choice in enumerate(scene["choices"], 1):
                choice_text = self.replace_placeholders(choice['text'])
                print(f"{Fore.YELLOW}{i}.{Style.RESET_ALL} {choice_text}")

    def replace_placeholders(self, text: str) -> str:
        """
        Replace placeholders in text with actual player names.
        
        Args:
            text: Text containing placeholders
            
        Returns:
            str: Text with placeholders replaced
        """
        placeholder_dict = {
            'current_player': self.players[self.current_player_index].name if self.players else '',
            'player1': self.players[0].name if len(self.players) > 0 else '',
            'player2': self.players[1].name if len(self.players) > 1 else '',
            'player3': self.players[2].name if len(self.players) > 2 else '',
            'player4': self.players[3].name if len(self.players) > 3 else '',
        }
        for placeholder, value in placeholder_dict.items():
            text = text.replace(f'{{{placeholder}}}', value)
        return text

    def handle_combat(self, enemy_stats: Dict):
        """
        Handle combat encounters between players and enemies.
        
        Args:
            enemy_stats: Dictionary containing enemy statistics
            
        Returns:
            bool: True if players won, False if they lost
        """
        clear_screen()
        enemy_health = enemy_stats.get("health", 50)
        enemy_max_health = enemy_health
        enemy_attack = enemy_stats.get("attack", 8)
        enemy_defense = enemy_stats.get("defense", 5)
        enemy_name = enemy_stats.get("name", "Enemy")
        enemy_color = self.colors.get(enemy_stats.get("color", ""), Fore.RESET)

        print(f"\n{Fore.RED}(ง •̀ω•́)ง⚔ Combat Started! (ง •̀ω•́)ง{Style.RESET_ALL}")
        self.combat_log = []

        while enemy_health > 0 and any(p.is_alive for p in self.players):
            clear_screen()

            # Display enemy status
            print(f"\n{enemy_color}{enemy_name}{Style.RESET_ALL}")
            print(create_health_bar(enemy_health, enemy_max_health))

            # Display all players' status
            print("\n(✿｡✿) === Party Status === (✿｡✿)")
            for player in self.players:
                print(f"{create_status_box(player)}")

            # Display combat log
            if self.combat_log:
                display_combat_log(self.combat_log)

            current_player = self.players[self.current_player_index]
            if current_player.is_alive:
                print(f"\n{Fore.CYAN}(｡>﹏<｡){current_player.name}'s turn!{Style.RESET_ALL}")
                action = self.get_player_action(current_player)

                if action == 'attack':
                    roll = current_player.roll_dice(20)
                    if roll >= 10:
                        damage = max(0, current_player.attack + current_player.roll_dice(6) - enemy_defense)
                        enemy_health = max(0, enemy_health - damage)
                        animate_attack(current_player.name, enemy_name, damage)
                        self.combat_log.append(f"{Fore.GREEN}{current_player.name} hits for {damage} damage!{Style.RESET_ALL}")
                    else:
                        animate_attack(current_player.name, enemy_name, 0)
                        self.combat_log.append(f"{Fore.YELLOW}{current_player.name} missed!{Style.RESET_ALL}")

                elif action == 'defend':
                    current_player.defense += 5  # Temporary defense buff
                    print(f"{Fore.BLUE}{current_player.name} is defending and gains +5 defense for this turn! (｀・ω・´){Style.RESET_ALL}")
                    self.combat_log.append(f"{current_player.name} is defending.")
                elif action == 'heal':
                    current_player.heal(15)
                    self.combat_log.append(f"{current_player.name} heals for 15 HP!")
                elif action == 'special':
                    print(f"{Fore.MAGENTA}{current_player.name} uses a special ability! ✨(=^･ω･^=)✨{Style.RESET_ALL}")
                    damage = max(0, current_player.attack + 10 - enemy_defense)
                    enemy_health = max(0, enemy_health - damage)
                    self.combat_log.append(f"{current_player.name} unleashes a special attack for {damage} damage!")
                    time.sleep(1)

                time.sleep(1)  # Pause for effect

                if enemy_health <= 0:
                    print(f"{enemy_color}{enemy_name} defeated! (❁´◡`❁){Style.RESET_ALL}")
                    return True

                # Enemy's turn to attack the current player
                enemy_roll = random.randint(1, 20)
                if enemy_roll >= 10:
                    damage = max(0, enemy_attack + random.randint(1, 6) - current_player.defense)
                    current_player.take_damage(damage)
                    animate_attack(enemy_name, current_player.name, damage)
                    self.combat_log.append(f"{enemy_name} hits {current_player.name} for {damage} damage!")
                    if not current_player.is_alive:
                        print(f"{Fore.RED}(╥﹏╥) {current_player.name} has fallen!{Style.RESET_ALL}")
                        self.combat_log.append(f"{current_player.name} has fallen!")
                else:
                    print(f"{enemy_name} missed! (✧ω✧)")
                    self.combat_log.append(f"{enemy_name} missed!")

                # Reset temporary defense buff if player was defending
                if action == 'defend':
                    current_player.defense -= 5

                time.sleep(1)  # Pause for effect

            self.current_player_index = (self.current_player_index + 1) % len(self.players)

        return any(p.is_alive for p in self.players)

    def get_player_action(self, player: Player):
        """
        Get player action with hotkey support in a kawaii style.
        
        Args:
            player: Player making the action
            
        Returns:
            str: Selected action
        """
        actions = [
            ('Attack (A)', '⚔ Launch a daring strike!'),
            ('Defend (D)', '🛡️ Brace yourself for impact!'),
            ('Heal (H)', '💊 Take a soothing potion!'),
            ('Special (S)', '✨ Unleash your hidden power!')
        ]

        print(f"\n{Fore.CYAN}Choose your action, {player.name}:{Style.RESET_ALL}")
        for action, description in actions:
            print(f"{Fore.YELLOW}{action}{Style.RESET_ALL} - {description}")

        while True:
            choice = input(f"\n{player.name}, what will you do? (Enter letter or full command): ").lower().strip()
            if choice in self.hotkeys:
                return self.hotkeys[choice]
            valid_actions = ['attack', 'defend', 'heal', 'special']
            if choice in valid_actions:
                return choice
            print(f"{Fore.RED}(｡•́︿•̀｡) Invalid choice! Use hotkeys (A/D/H/S) or type full command.{Style.RESET_ALL}")

    def handle_voting(self, voting_system: Dict):
        """
        Handle group voting sequences.
        
        Args:
            voting_system: Dictionary containing voting options and rules
        """
        print("\n(„• ᴗ •„) A vote is required among players.")
        options = voting_system.get("options", [])
        tie_breaker = voting_system.get("tie_breaker", "random")
        votes = {}

        for idx, option in enumerate(options, 1):
            option_text = self.replace_placeholders(option['text'])
            print(f"{Fore.YELLOW}{idx}.{Style.RESET_ALL} {option_text}")

        for player in self.players:
            while True:
                try:
                    choice = int(input(f"{player.name}, please vote (enter number): ")) - 1
                    if 0 <= choice < len(options):
                        votes[player.name] = choice
                        break
                    else:
                        print(f"{Fore.RED}(>_<) Invalid choice! Try again.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}(>_<) Please enter a valid number!{Style.RESET_ALL}")

        vote_counts = {}
        for vote in votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1

        max_votes = max(vote_counts.values())
        winners = [idx for idx, count in vote_counts.items() if count == max_votes]

        if len(winners) == 1:
            winning_option_index = winners[0]
        else:
            if tie_breaker == "random":
                winning_option_index = random.choice(winners)
            else:
                winning_option_index = winners[0]

        winning_option = options[winning_option_index]
        winning_text = self.replace_placeholders(winning_option['text'])
        print(f"\n(✿◕‿◕) The group has decided to: {winning_text}")

        if 'effect' in winning_option:
            effect = winning_option['effect']
            for player in self.players:
                player.apply_effect(effect)

        self.current_scene = winning_option.get('scene', 'end')

    def handle_requires_vote(self, requires_vote: Dict):
        min_players = requires_vote.get('min_players', len(self.players))
        timeout = requires_vote.get('timeout', None)
        success_scene = requires_vote.get('success_scene', 'end')
        failure_scene = requires_vote.get('failure_scene', 'end')

        print(f"\n(｡•̀ᴗ-)✧ A group decision is needed. At least {min_players} players must agree.")

        votes = {}
        for player in self.players:
            while True:
                choice = input(f"{player.name}, do you agree? (yes/no): ").strip().lower()
                if choice in ['yes', 'no']:
                    votes[player.name] = choice == 'yes'
                    break
                else:
                    print("(；￣Д￣) Please enter 'yes' or 'no'.")

        agree_count = sum(votes.values())

        if agree_count >= min_players:
            print(f"\n(｡•̀ᴗ-)✧ Decision successful! Moving on!")
            self.current_scene = success_scene
        else:
            print(f"\n(╯︵╰,) Not enough agreement. Alternate path chosen.")
            self.current_scene = failure_scene

    def make_choice(self, choice_index: int) -> bool:
        scene = self.story_data.get(self.current_scene, {})
        choices = scene.get("choices", [])

        if not (0 <= choice_index < len(choices)):
            return False

        choice = choices[choice_index]
        current_player = self.players[self.current_player_index]

        # Handle different choice types
        if "combat" in choice:
            success = self.handle_combat(choice["combat"])
            self.current_scene = choice["success"] if success else choice["failure"]
        elif "voting_system" in choice:
            self.handle_voting(choice["voting_system"])
            return True
        elif "requires_vote" in choice:
            self.handle_requires_vote(choice["requires_vote"])
            return True
        else:
            self.current_scene = choice.get("next_scene", "end")

        if "effect" in choice:
            effect = choice["effect"]
            current_player.apply_effect(effect)

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return True

    def run(self):
        """Main game loop."""
        while True:
            if not self.display_main_menu():
                continue

            while self.current_scene != "end" and any(p.is_alive for p in self.players):
                self.display_scene()
                self.display_progress_bar()
                scene = self.story_data.get(self.current_scene, {})
                self.scenes_visited.add(self.current_scene)
                choices = scene.get("choices", [])

                if not choices:
                    self.current_scene = 'end'
                    continue

                choice = choices[0]
                if "voting_system" in choice:
                    self.handle_voting(choice["voting_system"])
                elif "requires_vote" in choice:
                    self.handle_requires_vote(choice["requires_vote"])
                else:
                    current_player = self.players[self.current_player_index]
                    print(f"\n(◕‿◕) {current_player.name}'s turn to decide!")
                    for i, choice in enumerate(choices, 1):
                        choice_text = self.replace_placeholders(choice['text'])
                        print(f"{Fore.YELLOW}{i}.{Style.RESET_ALL} {choice_text}")
                    
                    valid_choice = False
                    while not valid_choice:
                        try:
                            choice_index = int(input(f"{current_player.name}, make your choice (enter number): ")) - 1
                            valid_choice = self.make_choice(choice_index)
                            if not valid_choice:
                                print(f"{Fore.RED}(>_<) Invalid choice! Try again.{Style.RESET_ALL}")
                        except ValueError:
                            print(f"{Fore.RED}(>_<) Please enter a valid number!{Style.RESET_ALL}")

            if not any(p.is_alive for p in self.players):
                print(f"\n{Fore.RED}(╥﹏╥) Game Over - All players have fallen!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}(*^ω^*) Congratulations - You've completed the adventure!{Style.RESET_ALL}")
            
            input("\nPress Enter to return to the main menu...")
            self.reset_game_state()

    def reset_game_state(self):
        """Reset the game state for a new game."""
        self.players = []
        self.current_scene = "start"
        self.current_player_index = 0
        self.combat_log = []
        self.scenes_visited.clear()

    def save_game(self):
        """Save the current game state to a file (Coming Soon)."""
        # Placeholder for save functionality
        # This could serialize the self.players, self.current_scene, and other state
        # to a JSON file so that the player can resume their adventure.
        # For now, just a placeholder message.
        print("\n(☆▽☆) Save feature coming soon! You’ll be able to save your journey and return later!")

    def load_game(self):
        """Load the game state from a file (Coming Soon)."""
        # Placeholder for load functionality
        # This would load the JSON data and restore the game state.
        # For now, just a placeholder message.
        print("\n(´｡• ᵕ •｡`) ♡ Load feature coming soon! Soon you can pick up where you left off!")

    def view_settings(self):
        """Adjust game settings (Coming Soon)."""
        # Here you might add volume settings, difficulty adjustments, or color schemes.
        # For now, just a placeholder.
        print("\n(ฅ•ω•ฅ) Settings feature is on its way! Soon you can customize your kawaii adventure!")

    def exit_game(self):
        """Exit the game gracefully."""
        # Display a farewell message and exit
        print("\n(｡•́︿•̀｡) So sad to see you go! Arigatou for playing! Mata ne!")
        sys.exit()



