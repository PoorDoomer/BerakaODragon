import json
import random
from typing import List, Dict
import os
import time
import pygame
from pygame import gfxdraw
import pickle

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init()

# Set up the display
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fantasy RPG Adventure")

# Enhanced colors
COLORS = {
    'black': pygame.Color(16, 16, 23),
    'white': pygame.Color(255, 255, 255),
    'red': pygame.Color(220, 48, 48),
    'green': pygame.Color(34, 197, 94),
    'yellow': pygame.Color(234, 179, 8),
    'blue': pygame.Color(59, 130, 246),
    'purple': pygame.Color(168, 85, 247),
    'gray': pygame.Color(107, 114, 128),
    'dark_overlay': pygame.Color(0, 0, 0, 128)
}

# Load fonts with fallbacks
def load_font(name, size):
    try:
        return pygame.font.Font(f"fonts/{name}.ttf", size)
    except:
        return pygame.font.SysFont('arial', size)

FONTS = {
    'title': load_font('medieval', 48),
    'heading': load_font('medieval', 32),
    'text': load_font('arial', 18),
    'combat': load_font('arial', 24)
}

# Game clock
clock = pygame.time.Clock()

# Load sound effects and music
sound_effects = {
    'attack': pygame.mixer.Sound('sounds/attack.wav'),
    'defend': pygame.mixer.Sound('sounds/defend.wav'),
    'level_up': pygame.mixer.Sound('sounds/level_up.wav'),
    'item_use': pygame.mixer.Sound('sounds/item_use.wav'),
    'skill_use': pygame.mixer.Sound('sounds/skill_use.wav'),
    'enemy_attack': pygame.mixer.Sound('sounds/enemy_attack.wav')
}

# Background music
pygame.mixer.music.load('sounds/background_music.mp3')
pygame.mixer.music.play(-1)  # Loop indefinitely

# UI Elements
class UIElement:
    @staticmethod
    def draw_fancy_rect(surface, rect, color, border_radius=10, border_color=None, border_width=2):
        if color:
            pygame.draw.rect(surface, color, rect, border_radius=border_radius)
        if border_color:
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius=border_radius)

    @staticmethod
    def draw_gradient_rect(surface, rect, start_color, end_color, vertical=True):
        """Draw a rectangle with a gradient fill"""
        if vertical:
            for i in range(rect.height):
                factor = i / rect.height
                color = pygame.Color(
                    int(start_color.r + (end_color.r - start_color.r) * factor),
                    int(start_color.g + (end_color.g - start_color.g) * factor),
                    int(start_color.b + (end_color.b - start_color.b) * factor)
                )
                pygame.draw.line(surface, color, (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))
        else:
            for i in range(rect.width):
                factor = i / rect.width
                color = pygame.Color(
                    int(start_color.r + (end_color.r - start_color.r) * factor),
                    int(start_color.g + (end_color.g - start_color.g) * factor),
                    int(start_color.b + (end_color.b - start_color.b) * factor)
                )
                pygame.draw.line(surface, color, (rect.x + i, rect.y), (rect.x + i, rect.y + rect.height))

# Health Bar UI
class HealthBar(UIElement):
    def __init__(self, max_health: int, width: int = 200, height: int = 20):
        self.max_health = max_health
        self.width = width
        self.height = height
        
    def draw(self, surface, x: int, y: int, current_health: int):
        # Background
        bg_rect = pygame.Rect(x, y, self.width, self.height)
        self.draw_fancy_rect(surface, bg_rect, COLORS['gray'], border_radius=5)
        
        # Health bar
        health_ratio = current_health / self.max_health
        health_width = int(self.width * health_ratio)
        if health_width > 0:
            health_rect = pygame.Rect(x, y, health_width, self.height)
            if health_ratio > 0.5:
                start_color = COLORS['green']
            elif health_ratio > 0.25:
                start_color = COLORS['yellow']
            else:
                start_color = COLORS['red']
            end_color = pygame.Color(start_color.r, start_color.g, start_color.b, 150)
            self.draw_gradient_rect(surface, health_rect, start_color, end_color)
        
        # Border
        self.draw_fancy_rect(surface, bg_rect, None, border_radius=5, 
                           border_color=COLORS['white'], border_width=2)
        
        # Health text
        health_text = f"{current_health}/{self.max_health}"
        text_surface = FONTS['text'].render(health_text, True, COLORS['white'])
        text_rect = text_surface.get_rect(center=(x + self.width/2, y + self.height/2))
        surface.blit(text_surface, text_rect)

# Combat UI
class CombatUI(UIElement):
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.combat_log = []
        self.max_log_entries = 5
        
    def draw_combat_state(self, surface, enemy, players):
        # Draw background
        background_rect = pygame.Rect(0, 0, self.width, self.height)
        self.draw_gradient_rect(surface, background_rect, 
                              COLORS['black'], 
                              pygame.Color(45, 45, 60))
        
        # Draw enemy section
        enemy_section = pygame.Rect(self.width//2, 50, self.width//2 - 50, 200)
        self.draw_fancy_rect(surface, enemy_section, 
                           pygame.Color(60, 30, 30), 
                           border_radius=15,
                           border_color=COLORS['red'])
        
        # Enemy name and health
        enemy_name = FONTS['heading'].render(enemy.name, True, COLORS['red'])
        surface.blit(enemy_name, (self.width//2 + 20, 70))
        health_bar = HealthBar(enemy.max_health, width=300)
        health_bar.draw(surface, self.width//2 + 20, 120, enemy.health)
        
        # Enemy status effects
        self.draw_status_effects(surface, enemy, self.width//2 + 20, 160)
        
        # Draw players section
        player_y = 50
        for player in players:
            player_section = pygame.Rect(50, player_y, self.width//2 - 100, 150)
            self.draw_fancy_rect(surface, player_section,
                               pygame.Color(30, 40, 60),
                               border_radius=15,
                               border_color=COLORS['blue'])
            
            # Player name and health
            player_name = FONTS['heading'].render(f"{player.name} (Lv.{player.level})", True, COLORS['blue'])
            surface.blit(player_name, (70, player_y + 20))
            health_bar = HealthBar(player.max_health, width=250)
            health_bar.draw(surface, 70, player_y + 70, player.health)
            
            # Player status effects
            self.draw_status_effects(surface, player, 70, player_y + 120)
            
            player_y += 170
        
        # Draw combat log
        log_section = pygame.Rect(50, self.height - 200, self.width - 100, 150)
        self.draw_fancy_rect(surface, log_section,
                           pygame.Color(40, 40, 40, 200),
                           border_radius=15,
                           border_color=COLORS['white'])
        
        log_y = self.height - 180
        for msg in self.combat_log[-self.max_log_entries:]:
            log_text = FONTS['combat'].render(msg, True, COLORS['white'])
            surface.blit(log_text, (70, log_y))
            log_y += 30
    
    def draw_status_effects(self, surface, combatant, x: int, y: int):
        icon_x = x
        icon_y = y
        for effect in combatant.status_effects:
            if effect.icon:
                surface.blit(effect.icon, (icon_x, icon_y))
                icon_x += effect.icon.get_width() + 5
    
    def draw_action_menu(self, surface, actions, selected_index):
        menu_rect = pygame.Rect(50, self.height - 300, self.width - 100, 200)
        self.draw_fancy_rect(surface, menu_rect, pygame.Color(50, 50, 70), border_radius=15)
        
        # Draw action options
        option_y = menu_rect.y + 20
        for idx, action in enumerate(actions):
            color = COLORS['white'] if idx != selected_index else COLORS['yellow']
            action_text = FONTS['combat'].render(f"{idx + 1}. {action}", True, color)
            surface.blit(action_text, (menu_rect.x + 20, option_y))
            option_y += 40

# Dialog Box UI
class DialogBox(UIElement):
    def __init__(self):
        self.portrait = None  # Load portrait images as needed
        self.text = ""
        self.visible = False
    
    def draw(self, surface):
        if self.visible:
            dialog_rect = pygame.Rect(50, SCREEN_HEIGHT - 250, SCREEN_WIDTH - 100, 200)
            self.draw_fancy_rect(surface, dialog_rect, pygame.Color(50, 50, 70, 200), border_radius=15)
            if self.portrait:
                surface.blit(self.portrait, (dialog_rect.x + 20, dialog_rect.y + 20))
            # Render text with wrapping
            self.draw_wrapped_text(surface, self.text, dialog_rect.x + 150, dialog_rect.y + 20, dialog_rect.width - 170)
    
    def draw_wrapped_text(self, surface, text, x, y, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + word + ' '
            if FONTS['text'].size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + ' '
        if current_line:
            lines.append(current_line)
        for idx, line in enumerate(lines):
            text_surface = FONTS['text'].render(line, True, COLORS['white'])
            surface.blit(text_surface, (x, y + idx * 30))

# Equipment Class
class Equipment:
    def __init__(self, name: str, attack_bonus: int = 0, defense_bonus: int = 0):
        self.name = name
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus

# Status Effect Class
class StatusEffect:
    def __init__(self, name: str, duration: int, effect_type: str, value: int, icon_path: str = None):
        self.name = name
        self.duration = duration
        self.effect_type = effect_type
        self.value = value
        self.icon = pygame.image.load(icon_path) if icon_path else None

    def apply(self, combatant):
        if self.effect_type == 'poison':
            damage = self.value
            combatant.take_damage(damage)
            return f"{combatant.name} takes {damage} poison damage!"
        elif self.effect_type == 'burn':
            damage = self.value
            combatant.take_damage(damage)
            return f"{combatant.name} takes {damage} burn damage!"
        # Add more effects as needed
        return ""

# Player Class
class Player:
    def __init__(self, name: str):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.base_attack = 10
        self.base_defense = 10
        self.is_alive = True
        self.status_effects: List[StatusEffect] = []
        self.equipment: List[Equipment] = []
        self.skills = ['Fireball', 'Heal']  # Example skills
        self.items = ['Health Potion', 'Mana Potion']
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100

    @property
    def attack(self):
        total_attack = self.base_attack + sum(e.attack_bonus for e in self.equipment)
        return total_attack

    @property
    def defense(self):
        total_defense = self.base_defense + sum(e.defense_bonus for e in self.equipment)
        return total_defense

    def roll_initiative(self):
        return random.randint(1, 20) + self.attack

    def roll_dice(self, sides: int = 20) -> int:
        return random.randint(1, sides)

    def take_damage(self, damage: int):
        actual_damage = max(0, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        self.is_alive = self.health > 0
        return actual_damage

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def apply_status_effect(self, effect: StatusEffect):
        self.status_effects.append(effect)

    def update_status_effects(self):
        messages = []
        for effect in self.status_effects[:]:
            msg = effect.apply(self)
            if msg:
                messages.append(msg)
            effect.duration -= 1
            if effect.duration <= 0:
                self.status_effects.remove(effect)
        return messages

    def gain_experience(self, amount: int):
        self.experience += amount
        while self.experience >= self.experience_to_next_level:
            self.experience -= self.experience_to_next_level
            self.level_up()

    def level_up(self):
        self.level += 1
        self.base_attack += 2
        self.base_defense += 2
        self.max_health += 20
        self.health = self.max_health  # Restore health upon leveling up
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        sound_effects['level_up'].play()
        self.combat_ui.combat_log.append(f"{self.name} leveled up to Level {self.level}!")

# Enemy Class
class Enemy:
    def __init__(self, name: str, health: int, attack: int, defense: int):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.status_effects: List[StatusEffect] = []
        self.icon = None  # Load enemy images as needed

    def take_damage(self, damage: int):
        actual_damage = max(0, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        return actual_damage

    def apply_status_effect(self, effect: StatusEffect):
        self.status_effects.append(effect)

    def update_status_effects(self):
        messages = []
        for effect in self.status_effects[:]:
            msg = effect.apply(self)
            if msg:
                messages.append(msg)
            effect.duration -= 1
            if effect.duration <= 0:
                self.status_effects.remove(effect)
        return messages

    def roll_initiative(self):
        return random.randint(1, 20) + self.attack

# Game Class
class Game:
    def __init__(self):
        self.players: List[Player] = []
        self.story_data = {}
        self.current_scene = "start"
        self.combat_ui = CombatUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.dialog_box = DialogBox()
        self.background_image = None

    def load_story(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.story_data = json.load(file)
        except FileNotFoundError:
            print(f"Story file {filename} not found!")
            return False
        return True

    def initialize_players(self):
        num_players = int(input("Enter the number of players: "))
        for i in range(num_players):
            name = input(f"Enter name for Player {i+1}: ").strip()
            self.players.append(Player(name))

    def display_scene(self):
        scene = self.story_data.get(self.current_scene, {})
        background_image_path = scene.get("background_image", None)
        if background_image_path:
            self.background_image = pygame.image.load(background_image_path)
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.background_image = None

        running = True
        choice_hover = -1
        
        while running:
            if self.background_image:
                screen.blit(self.background_image, (0, 0))
            else:
                screen.fill(COLORS['black'])
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_game()
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if choice_hover != -1:
                        self.make_choice(choice_hover)
                        running = False
            
            # Display scene title
            title = scene.get("title", "Scene")
            title_surface = FONTS['title'].render(title, True, COLORS['yellow'])
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 50))
            screen.blit(title_surface, title_rect)
            
            # Display description in a fancy box
            description = scene.get("description", {}).get("text", "")
            desc_rect = pygame.Rect(50, 120, SCREEN_WIDTH - 100, 200)
            UIElement.draw_fancy_rect(screen, desc_rect,
                                    pygame.Color(40, 40, 40, 200),
                                    border_radius=15,
                                    border_color=COLORS['white'])
            
            # Wrap and render description text
            words = description.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                text = ' '.join(current_line)
                if FONTS['text'].size(text)[0] > SCREEN_WIDTH - 150:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            text_y = 140
            for line in lines:
                text_surface = FONTS['text'].render(line, True, COLORS['white'])
                screen.blit(text_surface, (70, text_y))
                text_y += 30
            
            # Display choices
            choices = scene.get("choices", [])
            choice_y = 350
            choice_hover = -1
            
            for idx, choice in enumerate(choices):
                choice_rect = pygame.Rect(SCREEN_WIDTH//4, choice_y, SCREEN_WIDTH//2, 60)
                
                # Check for hover
                if choice_rect.collidepoint(mouse_pos):
                    choice_hover = idx
                    color = pygame.Color(60, 60, 80)
                else:
                    color = pygame.Color(40, 40, 60)
                
                UIElement.draw_fancy_rect(screen, choice_rect,
                                        color,
                                        border_radius=10,
                                        border_color=COLORS['white'])
                
                text = choice.get('text', '')
                choice_text = FONTS['text'].render(text, True, COLORS['white'])
                text_rect = choice_text.get_rect(center=choice_rect.center)
                screen.blit(choice_text, text_rect)
                
                choice_y += 80
            
            pygame.display.flip()
            clock.tick(60)

    def handle_combat(self, enemy_stats: Dict):
        # Create enemy and initialize combat
        enemy = Enemy(
            name=enemy_stats.get("name", "Enemy"),
            health=enemy_stats.get("health", 50),
            attack=enemy_stats.get("attack", 8),
            defense=enemy_stats.get("defense", 5)
        )
        
        combatants = self.players + [enemy]
        initiative_order = sorted(
            combatants,
            key=lambda x: x.roll_initiative(),
            reverse=True
        )
        
        running = True
        while running:
            screen.fill(COLORS['black'])
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_game()
                    pygame.quit()
                    exit()
            
            # Update status effects and combat state
            for combatant in combatants:
                if isinstance(combatant, Player) and combatant.is_alive:
                    messages = combatant.update_status_effects()
                    self.combat_ui.combat_log.extend(messages)
                elif isinstance(combatant, Enemy):
                    messages = combatant.update_status_effects()
                    self.combat_ui.combat_log.extend(messages)
            
            # Check combat end conditions
            if not enemy.health > 0 or not any(p.is_alive for p in self.players):
                running = False
                continue
            
            # Process combat turns
            for combatant in initiative_order:
                if isinstance(combatant, Player) and combatant.is_alive:
                    self.player_turn(combatant, enemy)
                elif isinstance(combatant, Enemy):
                    self.enemy_turn(enemy, self.players)
                
                if not enemy.health > 0 or not any(p.is_alive for p in self.players):
                    running = False
                    break
            
            # Draw combat UI
            self.combat_ui.draw_combat_state(screen, enemy, self.players)
            pygame.display.flip()
            clock.tick(60)
            time.sleep(1)  # Pause between turns
        
        # Grant experience if enemy defeated
        if enemy.health <= 0:
            exp_reward = enemy_stats.get("experience", 50)
            for player in self.players:
                if player.is_alive:
                    player.gain_experience(exp_reward)
        
        return enemy.health <= 0

    def player_turn(self, player: Player, enemy: Enemy):
        actions = ['Attack', 'Defend', 'Skills', 'Items']
        selected_index = 0
        action_selected = False

        while not action_selected:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(actions)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(actions)
                    elif event.key == pygame.K_RETURN:
                        action_selected = True
                elif event.type == pygame.QUIT:
                    self.save_game()
                    pygame.quit()
                    exit()

            # Drawing code
            self.combat_ui.draw_combat_state(screen, enemy, self.players)
            self.combat_ui.draw_action_menu(screen, actions, selected_index)
            pygame.display.flip()
            clock.tick(60)

        # Handle selected action
        selected_action = actions[selected_index]
        if selected_action == 'Attack':
            damage = player.attack + random.randint(1, 6)
            actual_damage = enemy.take_damage(damage)
            self.combat_ui.combat_log.append(f"{player.name} attacks for {actual_damage} damage!")
            sound_effects['attack'].play()
            # Critical hit effect
            if random.random() < 0.1:
                burn = StatusEffect('Burn', duration=3, effect_type='burn', value=5, icon_path='icons/burn.png')
                enemy.apply_status_effect(burn)
                self.combat_ui.combat_log.append(f"Critical! {enemy.name} is burning!")
        elif selected_action == 'Defend':
            player.base_defense += 5
            self.combat_ui.combat_log.append(f"{player.name} is defending!")
            sound_effects['defend'].play()
        elif selected_action == 'Skills':
            self.use_skill(player, enemy)
        elif selected_action == 'Items':
            self.use_item(player)

    def use_skill(self, player: Player, enemy: Enemy):
        selected_index = 0
        skill_selected = False
        skills = player.skills

        while not skill_selected:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(skills)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(skills)
                    elif event.key == pygame.K_RETURN:
                        skill_selected = True
                elif event.type == pygame.QUIT:
                    self.save_game()
                    pygame.quit()
                    exit()

            # Drawing code
            self.combat_ui.draw_combat_state(screen, enemy, self.players)
            # Draw skills menu
            self.combat_ui.draw_action_menu(screen, skills, selected_index)
            pygame.display.flip()
            clock.tick(60)

        # Handle selected skill
        selected_skill = skills[selected_index]
        if selected_skill == 'Fireball':
            damage = player.attack + random.randint(10, 20)
            actual_damage = enemy.take_damage(damage)
            self.combat_ui.combat_log.append(f"{player.name} casts Fireball for {actual_damage} damage!")
            sound_effects['skill_use'].play()
            burn = StatusEffect('Burn', duration=3, effect_type='burn', value=5, icon_path='icons/burn.png')
            enemy.apply_status_effect(burn)
            self.combat_ui.combat_log.append(f"{enemy.name} is burning!")
        elif selected_skill == 'Heal':
            heal_amount = random.randint(15, 25)
            player.heal(heal_amount)
            self.combat_ui.combat_log.append(f"{player.name} heals for {heal_amount} HP!")
            sound_effects['skill_use'].play()

    def use_item(self, player: Player):
        selected_index = 0
        item_selected = False
        items = player.items

        if not items:
            self.combat_ui.combat_log.append("No items available!")
            return

        while not item_selected:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(items)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(items)
                    elif event.key == pygame.K_RETURN:
                        item_selected = True
                elif event.type == pygame.QUIT:
                    self.save_game()
                    pygame.quit()
                    exit()

            # Drawing code
            self.combat_ui.draw_combat_state(screen, enemy, self.players)
            # Draw items menu
            self.combat_ui.draw_action_menu(screen, items, selected_index)
            pygame.display.flip()
            clock.tick(60)

        # Handle selected item
        selected_item = items[selected_index]
        if selected_item == 'Health Potion':
            heal_amount = 50
            player.heal(heal_amount)
            self.combat_ui.combat_log.append(f"{player.name} uses a Health Potion and recovers {heal_amount} HP!")
            sound_effects['item_use'].play()
            player.items.remove('Health Potion')
        elif selected_item == 'Mana Potion':
            # Implement mana system if needed
            self.combat_ui.combat_log.append(f"{player.name} uses a Mana Potion!")
            sound_effects['item_use'].play()
            player.items.remove('Mana Potion')

    def enemy_turn(self, enemy: Enemy, players: List[Player]):
        target = random.choice([p for p in players if p.is_alive])
        damage = enemy.attack + random.randint(1, 6)
        actual_damage = target.take_damage(damage)
        self.combat_ui.combat_log.append(f"{enemy.name} strikes {target.name} for {actual_damage} damage!")
        sound_effects['enemy_attack'].play()

    def make_choice(self, choice_index: int) -> bool:
        scene = self.story_data.get(self.current_scene, {})
        choices = scene.get("choices", [])

        if not (0 <= choice_index < len(choices)):
            return False

        choice = choices[choice_index]

        # Handle combat if specified
        if "combat" in choice:
            enemy_stats = choice["combat"]
            success = self.handle_combat(enemy_stats)
            self.current_scene = choice["success"] if success else choice["failure"]
        else:
            self.current_scene = choice.get("next_scene", "end")

        return True

    def save_game(self, filename='savegame.pkl'):
        game_state = {
            'players': self.players,
            'current_scene': self.current_scene,
            'story_data': self.story_data,
            # Include any other necessary state data
        }
        with open(filename, 'wb') as f:
            pickle.dump(game_state, f)
        print("Game saved successfully.")

    def load_game(self, filename='savegame.pkl'):
        try:
            with open(filename, 'rb') as f:
                game_state = pickle.load(f)
            self.players = game_state['players']
            self.current_scene = game_state['current_scene']
            self.story_data = game_state['story_data']
            print("Game loaded successfully.")
        except FileNotFoundError:
            print("Save file not found.")

    def run(self):
        self.initialize_players()
        if not self.load_story('story.json'):
            return

        while self.current_scene != "end" and any(p.is_alive for p in self.players):
            self.display_scene()

        if not any(p.is_alive for p in self.players):
            print(f"\nGame Over - All players have fallen!")
        else:
            print(f"\nCongratulations - You've completed the adventure!")

