"""
Combat effects module for handling status effects and buffs.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from ..core.player import Player

@dataclass
class Effect:
    """Base class for status effects."""
    name: str
    duration: int
    strength: int
    description: str

    def apply(self, target: Player) -> str:
        """Apply the effect to the target."""
        pass

    def tick(self) -> bool:
        """
        Progress the effect duration.
        
        Returns:
            bool: True if effect is still active, False if expired
        """
        self.duration -= 1
        return self.duration > 0

@dataclass
class BuffEffect(Effect):
    """Temporary stat boost effect."""
    stat: str

    def apply(self, target: Player) -> str:
        """
        Apply buff to target's stats.
        
        Args:
            target (Player): Player to buff
            
        Returns:
            str: Effect application message
        """
        if self.stat == "attack":
            target.stats.attack += self.strength
            return f"{target.name} gains {self.strength} attack!"
        elif self.stat == "defense":
            target.stats.defense += self.strength
            return f"{target.name} gains {self.strength} defense!"
        return "No effect"

@dataclass
class DotEffect(Effect):
    """Damage over time effect."""
    
    def apply(self, target: Player) -> str:
        """
        Apply damage to target.
        
        Args:
            target (Player): Player to damage
            
        Returns:
            str: Effect application message
        """
        damage = target.take_damage(self.strength)
        return f"{target.name} takes {damage} damage from {self.name}!"

@dataclass
class HotEffect(Effect):
    """Healing over time effect."""
    
    def apply(self, target: Player) -> str:
        """
        Apply healing to target.
        
        Args:
            target (Player): Player to heal
            
        Returns:
            str: Effect application message
        """
        healing = target.heal(self.strength)
        return f"{target.name} heals {healing} HP from {self.name}!"

class EffectManager:
    """Manages active effects on entities."""
    
    def __init__(self):
        self.active_effects: Dict[Player, List[Effect]] = {}

    def add_effect(self, target: Player, effect: Effect) -> str:
        """
        Add a new effect to a target.
        
        Args:
            target (Player): Target to receive effect
            effect (Effect): Effect to apply
            
        Returns:
            str: Effect application message
        """
        if target not in self.active_effects:
            self.active_effects[target] = []
        
        # Check for existing effect of same type
        for existing in self.active_effects[target]:
            if isinstance(existing, type(effect)):
                existing.duration = max(existing.duration, effect.duration)
                existing.strength = max(existing.strength, effect.strength)
                return f"Extended {effect.name} on {target.name}!"
        
        self.active_effects[target].append(effect)
        return effect.apply(target)

    def process_effects(self) -> List[str]:
        """
        Process all active effects.
        
        Returns:
            List[str]: Messages from effect applications
        """
        messages = []
        for target, effects in self.active_effects.items():
            # Process each effect and collect messages
            for effect in effects[:]:  # Copy list to allow removal during iteration
                messages.append(effect.apply(target))
                if not effect.tick():
                    effects.remove(effect)
                    messages.append(f"{effect.name} wears off from {target.name}!")
        
        # Clean up empty effect lists
        self.active_effects = {k: v for k, v in self.active_effects.items() if v}
        return messages

    def get_effects(self, target: Player) -> List[Effect]:
        """Get all active effects on a target."""
        return self.active_effects.get(target, []) 