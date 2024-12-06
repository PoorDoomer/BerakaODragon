"""
Combat manager module for handling combat encounters.
"""

from typing import Dict, List, Tuple, Optional
from ..core.player import Player
from .actions import ACTIONS, CombatAction
from .effects import EffectManager, Effect

class CombatManager:
    """Manages combat encounters between players and enemies."""
    
    def __init__(self):
        self.combat_log: List[str] = []
        self.effect_manager = EffectManager()
        self.current_turn = 0
        self.is_combat_active = False

    def start_combat(self, players: List[Player], enemy: Dict) -> None:
        """
        Initialize a combat encounter.
        
        Args:
            players (List[Player]): List of players in combat
            enemy (Dict): Enemy stats and data
        """
        self.players = players
        self.enemy = enemy.copy()  # Copy to avoid modifying original
        self.combat_log = []
        self.current_turn = 0
        self.is_combat_active = True
        self.log_message(f"Combat started against {enemy['name']}!")

    def handle_player_turn(self, player: Player, action_name: str) -> Tuple[bool, str]:
        """
        Process a player's turn.
        
        Args:
            player (Player): Player taking action
            action_name (str): Name of the action to take
            
        Returns:
            Tuple[bool, str]: Success status and result message
        """
        if not self.is_combat_active:
            return False, "Combat is not active"
            
        if action_name not in ACTIONS:
            return False, f"Invalid action: {action_name}"
            
        action = ACTIONS[action_name]
        damage, message = action.execute(player, self.enemy)
        
        self.log_message(message)
        
        if action_name == "attack" or action_name == "special":
            self.enemy["health"] = max(0, self.enemy["health"] - damage)
            if self.enemy["health"] <= 0:
                self.end_combat(True)
                return True, "Victory!"
                
        return True, message

    def handle_enemy_turn(self) -> Tuple[bool, str]:
        """
        Process the enemy's turn.
        
        Returns:
            Tuple[bool, str]: Success status and result message
        """
        if not self.is_combat_active:
            return False, "Combat is not active"
            
        # Select random living player as target
        living_players = [p for p in self.players if p.is_alive]
        if not living_players:
            self.end_combat(False)
            return True, "Game Over - All players defeated!"
            
        from random import choice
        target = choice(living_players)
        
        # Enemy attack roll
        from random import randint
        roll = randint(1, 20)
        
        if roll >= 10:  # Hit threshold
            damage = max(0, self.enemy["attack"] + randint(1, 6) - target.stats.defense)
            target.take_damage(damage)
            message = f"{self.enemy['name']} hits {target.name} for {damage} damage!"
            
            if not target.is_alive:
                message += f"\n{target.name} has fallen!"
                if not any(p.is_alive for p in self.players):
                    self.end_combat(False)
                    return True, "Game Over - All players defeated!"
        else:
            message = f"{self.enemy['name']} missed {target.name}!"
            
        self.log_message(message)
        return True, message

    def process_effects(self) -> List[str]:
        """
        Process all active effects.
        
        Returns:
            List[str]: Messages from effect applications
        """
        messages = self.effect_manager.process_effects()
        for message in messages:
            self.log_message(message)
        return messages

    def end_combat(self, victory: bool) -> None:
        """
        End the combat encounter.
        
        Args:
            victory (bool): Whether players won
        """
        self.is_combat_active = False
        message = "Victory!" if victory else "Defeat..."
        self.log_message(message)

    def log_message(self, message: str) -> None:
        """
        Add a message to the combat log.
        
        Args:
            message (str): Message to log
        """
        self.combat_log.append(message)

    def get_combat_state(self) -> Dict:
        """
        Get current combat state.
        
        Returns:
            Dict: Current combat state information
        """
        return {
            "is_active": self.is_combat_active,
            "current_turn": self.current_turn,
            "enemy": self.enemy if self.is_combat_active else None,
            "combat_log": self.combat_log[-5:],  # Last 5 messages
            "player_states": [
                {
                    "name": player.name,
                    "health": player.stats.health,
                    "max_health": player.stats.max_health,
                    "is_alive": player.is_alive,
                    "effects": [
                        {
                            "name": effect.name,
                            "duration": effect.duration,
                            "description": effect.description
                        }
                        for effect in self.effect_manager.get_effects(player)
                    ]
                }
                for player in self.players
            ] if self.is_combat_active else []
        }

    def add_effect(self, target: Player, effect: Effect) -> None:
        """
        Add an effect to a target.
        
        Args:
            target (Player): Target to receive effect
            effect (Effect): Effect to apply
        """
        message = self.effect_manager.add_effect(target, effect)
        self.log_message(message) 