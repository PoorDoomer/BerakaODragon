"""
Example plugin demonstrating the plugin system features.
"""

from src.systems.plugins import Plugin, PluginInfo
from src.systems.events import event_handler, EventPriority
from src.combat import CombatEvent

PLUGIN_INFO = PluginInfo(
    name="ExamplePlugin",
    version="1.0.0",
    author="Your Name",
    description="An example plugin demonstrating various features",
    dependencies=[]
)

class Plugin(Plugin):
    """Example plugin implementation."""
    
    async def on_load(self) -> None:
        """Called when plugin is loaded."""
        print(f"Loading {self.info.name}...")
        
    async def on_enable(self) -> None:
        """Called when plugin is enabled."""
        print(f"Enabling {self.info.name}...")
        
    async def on_disable(self) -> None:
        """Called when plugin is disabled."""
        print(f"Disabling {self.info.name}...")
        
    @event_handler("combat_start", priority=EventPriority.HIGH)
    async def on_combat_start(self, event: CombatEvent) -> None:
        """Handle combat start event."""
        print(f"Combat started between {event.attacker} and {event.defender}")
        
        # Example: Modify combat parameters
        if event.attacker == "player":
            event.context["bonus_damage"] = 1.5
            
    @event_handler("combat_end", priority=EventPriority.MONITOR)
    async def on_combat_end(self, event: CombatEvent) -> None:
        """Log combat results."""
        winner = event.context.get("winner")
        print(f"Combat ended. Winner: {winner}")
        
    @event_handler("story_choice", priority=EventPriority.NORMAL)
    async def on_story_choice(self, event: StoryEvent) -> None:
        """Handle story choice event."""
        print(f"Player made choice: {event.choice_made} in scene {event.scene_id}")
        
        # Example: Add custom choice effects
        if event.choice_made == "help_villager":
            event.context["karma"] = event.context.get("karma", 0) + 1 