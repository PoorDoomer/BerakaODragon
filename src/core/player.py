"""
Player module containing the Player class and related components.
"""

from typing import List, Dict
from dataclasses import dataclass

@dataclass
class PlayerStats:
    """Player statistics container"""
    health: int = 100
    max_health: int = 100
    attack: int = 10
    defense: int = 10

@dataclass
class Inventory:
    """Player inventory container"""
    items: List[str] = None

    def __post_init__(self):
        self.items = self.items or []

class Player:
    """
    Represents a player in the game.
    
    Attributes:
        name (str): Player name
        stats (PlayerStats): Player statistics
        inventory (Inventory): Player inventory
        is_alive (bool): Player state
        status_effects (List[str]): Active effects
    """
    
    def __init__(self, name: str):
        self.name = name
        self.stats = PlayerStats()
        self.inventory = Inventory()
        self.is_alive = True
        self.status_effects: List[str] = []

    def roll_dice(self, sides: int = 20) -> int:
        """Generate random number for actions."""
        from random import randint
        return randint(1, sides)

    def take_damage(self, damage: int) -> int:
        """
        Handle damage calculations.
        
        Args:
            damage (int): Amount of damage to take
            
        Returns:
            int: Actual damage taken after defense
        """
        actual_damage = max(0, damage - self.stats.defense)
        self.stats.health = max(0, self.stats.health - actual_damage)
        self.is_alive = self.stats.health > 0
        return actual_damage

    def heal(self, amount: int) -> int:
        """
        Restore health points.
        
        Args:
            amount (int): Amount of health to restore
            
        Returns:
            int: Actual amount healed
        """
        old_health = self.stats.health
        self.stats.health = min(self.stats.max_health, self.stats.health + amount)
        return self.stats.health - old_health

    def apply_effect(self, effect: Dict) -> None:
        """
        Apply status effects to the player.
        
        Args:
            effect (Dict): Effect to apply with type and value
        """
        if "heal" in effect:
            self.heal(effect["heal"])
        if "buff_attack" in effect:
            self.stats.attack += effect["buff_attack"]
        if "buff_defense" in effect:
            self.stats.defense += effect["buff_defense"]
        if "damage" in effect:
            self.take_damage(effect["damage"])

    def __str__(self) -> str:
        """String representation of the player."""
        return f"{self.name} (HP: {self.stats.health}/{self.stats.max_health})" 