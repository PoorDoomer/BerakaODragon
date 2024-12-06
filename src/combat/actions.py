"""
Combat actions module containing different combat moves and abilities.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from ..core.player import Player

class CombatAction(ABC):
    """Base class for all combat actions."""
    
    @abstractmethod
    def execute(self, source: Any, target: Any) -> Tuple[int, str]:
        """
        Execute the action.
        
        Args:
            source: The entity performing the action
            target: The target of the action
            
        Returns:
            Tuple[int, str]: Damage/healing done and message
        """
        pass

class Attack(CombatAction):
    """Basic attack action."""
    
    def execute(self, source: Player, target: Dict) -> Tuple[int, str]:
        """
        Execute an attack.
        
        Args:
            source (Player): The attacking player
            target (Dict): The target enemy stats
            
        Returns:
            Tuple[int, str]: Damage done and result message
        """
        roll = source.roll_dice(20)
        if roll >= 10:  # Hit threshold
            damage = max(0, source.stats.attack + source.roll_dice(6) - target['defense'])
            return damage, f"{source.name} hits for {damage} damage!"
        return 0, f"{source.name} missed!"

class Defend(CombatAction):
    """Defensive stance action."""
    
    def execute(self, source: Player, target: Dict) -> Tuple[int, str]:
        """
        Take defensive stance.
        
        Args:
            source (Player): The defending player
            target (Dict): Unused for this action
            
        Returns:
            Tuple[int, str]: Defense bonus and result message
        """
        defense_bonus = 5
        source.stats.defense += defense_bonus
        return defense_bonus, f"{source.name} takes a defensive stance (+{defense_bonus} defense)!"

class Heal(CombatAction):
    """Healing action."""
    
    def execute(self, source: Player, target: Dict) -> Tuple[int, str]:
        """
        Perform healing.
        
        Args:
            source (Player): The player to heal
            target (Dict): Unused for this action
            
        Returns:
            Tuple[int, str]: Amount healed and result message
        """
        heal_amount = 15
        actual_heal = source.heal(heal_amount)
        return actual_heal, f"{source.name} heals for {actual_heal} HP!"

class Special(CombatAction):
    """Special attack action."""
    
    def execute(self, source: Player, target: Dict) -> Tuple[int, str]:
        """
        Execute special attack.
        
        Args:
            source (Player): The attacking player
            target (Dict): The target enemy stats
            
        Returns:
            Tuple[int, str]: Damage done and result message
        """
        damage = max(0, source.stats.attack + 10 - target['defense'])
        return damage, f"{source.name} unleashes a special attack for {damage} damage!"

# Action registry for easy access
ACTIONS = {
    'attack': Attack(),
    'defend': Defend(),
    'heal': Heal(),
    'special': Special()
} 