import json
import random
from typing import List, Dict
import os
import time
from colorama import Fore, Style, init
import shutil

# Initialize colorama
init(autoreset=True)


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def create_health_bar(current: int, maximum: int, width: int = 20) -> str:
    """Create a visual health bar with customizable width."""
    filled = int((current / maximum) * width)
    bar = f"[{Fore.RED}{'█' * filled}{Fore.WHITE}{'░' * (width - filled)}{Style.RESET_ALL}]"
    return f"{bar} {current}/{maximum} HP"


def create_status_box(player: 'Player') -> str:
    """Create a formatted status box for a player."""
    terminal_width = shutil.get_terminal_size().columns
    box_width = min(terminal_width - 4, 50)

    health_bar = create_health_bar(player.health, player.max_health)
    status_effects = ', '.join(player.status_effects) if player.status_effects else 'None'

    box = [
        f"┌{'─' * box_width}┐",
        f"│ {player.name:<{box_width-2}} │",
        f"│ {health_bar:<{box_width-2}} │",
        f"│ Attack: {player.attack} | Defense: {player.defense:<{box_width-20}} │",
        f"│ Status: {status_effects:<{box_width-10}} │",
        f"└{'─' * box_width}┘"
    ]
    return '\n'.join(box)


def display_combat_log(messages: List[str], max_lines: int = 5):
    """Display a scrolling combat log with the most recent messages."""
    print(f"\n{Fore.YELLOW}══ Combat Log ══{Style.RESET_ALL}")
    for msg in messages[-max_lines:]:
        print(msg)
    print(f"{Fore.YELLOW}{'═' * 20}{Style.RESET_ALL}\n")


def animate_attack(attacker: str, defender: str, damage: int):
    """Create a simple animation for attacks."""
    frames = [
        f"{attacker} ⚔️  {defender}",
        f"{attacker}  ⚔️ {defender}",
        f"{attacker}   ⚔️{defender}",
    ]

    for frame in frames:
        clear_screen()
        print(frame)
        time.sleep(0.1)

    if damage > 0:
        print(f"{Fore.RED}-{damage} HP!{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}Miss!{Style.RESET_ALL}")
    time.sleep(0.5)


class Player:
    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.defense = 10
        self.is_alive = True
        self.status_effects = []  # For tracking temporary effects

    def roll_dice(self, sides: int = 20) -> int:
        return random.randint(1, sides)

    def take_damage(self, damage: int):
        actual_damage = max(0, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        self.is_alive = self.health > 0
        return actual_damage

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
        print(f"{self.name} heals for {amount} HP!")

    def apply_effect(self, effect: Dict):
        if "heal" in effect:
            self.heal(effect["heal"])
        if "buff_attack" in effect:
            self.attack += effect["buff_attack"]
            print(f"{self.name}'s attack increased by {effect['buff_attack']}!")
        if "buff_defense" in effect:
            self.defense += effect["buff_defense"]
            print(f"{self.name}'s defense increased by {effect['buff_defense']}!")
        if "damage" in effect:
            damage = self.take_damage(effect["damage"])
            print(f"{self.name} took {damage} damage!")


class Game:
    def __init__(self):
        self.players: List[Player] = []
        self.current_scene = "start"
        self.story_data = {}
        self.current_player_index = 0
        self.colors = {}
        self.combat_log = []
        self.terminal_width = shutil.get_terminal_size().columns

    def load_story(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.story_data = json.load(file)
                colors_config = self.story_data.get('config', {}).get('colors', {})
                self.colors = {}
                for key, value in colors_config.items():
                    self.colors[key] = self.get_color_code(value)
        except FileNotFoundError:
            print(f"Story file {filename} not found!")
            return False
        return True

    def get_color_code(self, color_name: str) -> str:
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
        num_players = 4  # Adjust the number of players as needed
        for i in range(num_players):
            while True:
                name = input(f"Enter name for Player {i+1}: ").strip()
                if name and not any(p.name == name for p in self.players):
                    self.players.append(Player(name))
                    break
                print("Please enter a unique, non-empty name.")

    def display_scene(self):
        clear_screen()
        scene = self.story_data.get(self.current_scene, {})

        # Display title
        title = scene.get("title", "Current Scene")
        print(f"\n{Fore.CYAN}{'═' * 20} {title} {'═' * 20}{Style.RESET_ALL}\n")

        # Display description with text wrapping and preserving line breaks
        description = scene.get("description", {})
        if isinstance(description, dict):
            text = description.get("text", "")
            color_name = description.get("color", "")
            color_code = self.colors.get(color_name, Fore.RESET)
            text = self.replace_placeholders(text)

            # Split text into paragraphs based on newline characters
            paragraphs = text.split('\n')

            for paragraph in paragraphs:
                if paragraph.strip() == '':
                    print('')  # Preserve blank lines
                    continue

                # Word wrap each paragraph
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
            print("\n=== Party Status ===")
            for player in self.players:
                print(create_status_box(player))

        # Display choices
        if "choices" in scene and scene["choices"]:
            print(f"\n{Fore.GREEN}Available Choices:{Style.RESET_ALL}")
            for i, choice in enumerate(scene["choices"], 1):
                choice_text = self.replace_placeholders(choice['text'])
                print(f"{Fore.YELLOW}{i}.{Style.RESET_ALL} {choice_text}")

    def replace_placeholders(self, text: str) -> str:
        # Create a placeholder dictionary
        placeholder_dict = {
            'current_player': self.players[self.current_player_index].name if self.players else '',
            'player1': self.players[0].name if len(self.players) > 0 else '',
            'player2': self.players[1].name if len(self.players) > 1 else '',
            'player3': self.players[2].name if len(self.players) > 2 else '',
            'player4': self.players[3].name if len(self.players) > 3 else '',
        }
        # Replace placeholders in the text
        for placeholder, value in placeholder_dict.items():
            text = text.replace(f'{{{placeholder}}}', value)
        return text

    def handle_combat(self, enemy_stats: Dict):
        clear_screen()
        enemy_health = enemy_stats.get("health", 50)
        enemy_max_health = enemy_health
        enemy_attack = enemy_stats.get("attack", 8)
        enemy_defense = enemy_stats.get("defense", 5)
        enemy_name = enemy_stats.get("name", "Enemy")
        enemy_color = self.colors.get(enemy_stats.get("color", ""), Fore.RESET)

        print(f"\n{Fore.RED}⚔ Combat Started! ⚔{Style.RESET_ALL}")
        self.combat_log = []

        while enemy_health > 0 and any(p.is_alive for p in self.players):
            clear_screen()

            # Display enemy status
            print(f"\n{enemy_color}{enemy_name}{Style.RESET_ALL}")
            print(create_health_bar(enemy_health, enemy_max_health))

            # Display all players' status
            print("\n=== Party Status ===")
            for player in self.players:
                print(f"{create_status_box(player)}")

            # Display combat log
            if self.combat_log:
                display_combat_log(self.combat_log)

            current_player = self.players[self.current_player_index]
            if current_player.is_alive:
                print(f"\n{Fore.CYAN}{current_player.name}'s turn!{Style.RESET_ALL}")
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
                    print(f"{current_player.name} is defending and gains +5 defense for this turn!")
                    self.combat_log.append(f"{current_player.name} is defending.")
                elif action == 'heal':
                    current_player.heal(15)
                    self.combat_log.append(f"{current_player.name} heals for 15 HP!")
                elif action == 'special':
                    # Implement special abilities here
                    print(f"{current_player.name} uses a special ability!")
                    damage = max(0, current_player.attack + 10 - enemy_defense)
                    enemy_health = max(0, enemy_health - damage)
                    self.combat_log.append(f"{current_player.name} unleashes a special attack for {damage} damage!")
                    time.sleep(1)

                time.sleep(1)  # Pause for effect

                if enemy_health <= 0:
                    print(f"{enemy_color}{enemy_name} defeated!{Style.RESET_ALL}")
                    return True

                # Enemy's turn to attack the current player
                enemy_roll = random.randint(1, 20)
                if enemy_roll >= 10:
                    damage = max(0, enemy_attack + random.randint(1, 6) - current_player.defense)
                    current_player.take_damage(damage)
                    animate_attack(enemy_name, current_player.name, damage)
                    self.combat_log.append(f"{enemy_name} hits {current_player.name} for {damage} damage!")
                    if not current_player.is_alive:
                        print(f"{current_player.name} has fallen!")
                        self.combat_log.append(f"{current_player.name} has fallen!")
                else:
                    print(f"{enemy_name} missed!")
                    self.combat_log.append(f"{enemy_name} missed!")

                # Reset temporary defense buff if player was defending
                if action == 'defend':
                    current_player.defense -= 5

                time.sleep(1)  # Pause for effect

            # Move to next player
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

        return any(p.is_alive for p in self.players)

    def get_player_action(self, player: Player):
        actions = [
            ('Attack', '⚔️ Launch a basic attack'),
            ('Defend', '🛡️ Raise your defenses'),
            ('Heal', '💊 Restore some health'),
            ('Special Ability', '✨ Use your special power')
        ]

        print(f"\n{Fore.CYAN}Choose your action:{Style.RESET_ALL}")
        for idx, (action, description) in enumerate(actions, 1):
            print(f"{Fore.YELLOW}{idx}.{Style.RESET_ALL} {action} - {description}")

        while True:
            try:
                choice = int(input(f"\n{player.name}, what will you do? (Enter number): ")) - 1
                if 0 <= choice < len(actions):
                    return actions[choice][0].lower()
                else:
                    print(f"{Fore.RED}Invalid choice! Try again.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number!{Style.RESET_ALL}")

    def handle_voting(self, voting_system: Dict):
        print("\nA vote is required among players.")
        options = voting_system.get("options", [])
        tie_breaker = voting_system.get("tie_breaker", "random")
        votes = {}

        # Display options
        for idx, option in enumerate(options, 1):
            option_text = self.replace_placeholders(option['text'])
            print(f"{Fore.YELLOW}{idx}.{Style.RESET_ALL} {option_text}")

        # Collect votes
        for player in self.players:
            while True:
                try:
                    choice = int(input(f"{player.name}, please vote (enter number): ")) - 1
                    if 0 <= choice < len(options):
                        votes[player.name] = choice
                        break
                    else:
                        print(f"{Fore.RED}Invalid choice! Try again.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Please enter a valid number!{Style.RESET_ALL}")

        # Count votes
        vote_counts = {}
        for vote in votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1

        # Determine the winning option(s)
        max_votes = max(vote_counts.values())
        winners = [idx for idx, count in vote_counts.items() if count == max_votes]

        if len(winners) == 1:
            winning_option_index = winners[0]
        else:
            # Handle tie
            if tie_breaker == "random":
                winning_option_index = random.choice(winners)
            else:
                winning_option_index = winners[0]

        winning_option = options[winning_option_index]
        winning_text = self.replace_placeholders(winning_option['text'])
        print(f"\nThe group has decided to: {winning_text}")

        # Handle effect if any
        if 'effect' in winning_option:
            effect = winning_option['effect']
            for player in self.players:
                player.apply_effect(effect)

        # Update current_scene
        self.current_scene = winning_option.get('scene', 'end')

    def handle_requires_vote(self, requires_vote: Dict):
        min_players = requires_vote.get('min_players', len(self.players))
        timeout = requires_vote.get('timeout', None)
        success_scene = requires_vote.get('success_scene', 'end')
        failure_scene = requires_vote.get('failure_scene', 'end')

        print(f"\nA group decision is required. At least {min_players} players must agree.")

        # Collect votes
        votes = {}
        for player in self.players:
            while True:
                choice = input(f"{player.name}, do you agree? (yes/no): ").strip().lower()
                if choice in ['yes', 'no']:
                    votes[player.name] = choice == 'yes'
                    break
                else:
                    print("Please enter 'yes' or 'no'.")

        # Count votes
        agree_count = sum(votes.values())

        if agree_count >= min_players:
            print(f"\nDecision successful! Proceeding to next scene.")
            self.current_scene = success_scene
        else:
            print(f"\nNot enough players agreed. Proceeding to alternative scene.")
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

        # Move to next player for next decision
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return True

    def run(self):
        self.initialize_players()

        if not self.load_story('story.json'):
            return

        while self.current_scene != "end" and any(p.is_alive for p in self.players):
            self.display_scene()
            scene = self.story_data.get(self.current_scene, {})
            choices = scene.get("choices", [])

            if not choices:
                # No choices, end scene
                self.current_scene = 'end'
                continue

            choice = choices[0]
            if "voting_system" in choice:
                self.handle_voting(choice["voting_system"])
            elif "requires_vote" in choice:
                self.handle_requires_vote(choice["requires_vote"])
            else:
                current_player = self.players[self.current_player_index]
                print(f"\n{current_player.name}'s turn to decide!")
                # Display choices
                for i, choice in enumerate(choices, 1):
                    choice_text = self.replace_placeholders(choice['text'])
                    print(f"{Fore.YELLOW}{i}.{Style.RESET_ALL} {choice_text}")
                valid_choice = False
                while not valid_choice:
                    try:
                        choice_index = int(input(f"{current_player.name}, make your choice (enter number): ")) - 1
                        valid_choice = self.make_choice(choice_index)
                        if not valid_choice:
                            print(f"{Fore.RED}Invalid choice! Try again.{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED}Please enter a valid number!{Style.RESET_ALL}")

        if not any(p.is_alive for p in self.players):
            print(f"\n{Fore.RED}Game Over - All players have fallen!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}Congratulations - You've completed the adventure!{Style.RESET_ALL}")


