"""
Event system module providing event dispatching and handling capabilities.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set

# Configure logging
logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """Event handler priority levels."""
    LOWEST = auto()
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    HIGHEST = auto()
    MONITOR = auto()  # For monitoring/logging only, no modifications

@dataclass
class Event:
    """Base event class that all game events inherit from."""
    name: str
    cancelled: bool = False
    handled: bool = False
    
    def cancel(self) -> None:
        """Cancel the event."""
        self.cancelled = True

@dataclass
class GameEvent(Event):
    """Game-related events with additional context."""
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CombatEvent(GameEvent):
    """Combat-related events."""
    attacker: Optional[str] = None
    defender: Optional[str] = None
    damage: float = 0.0

@dataclass
class StoryEvent(GameEvent):
    """Story-related events."""
    scene_id: str = ""
    choice_made: Optional[str] = None

EventHandler = Callable[[Event], Awaitable[None]]

class EventDispatcher:
    """
    Handles registration and dispatching of event handlers.
    Supports async event handlers and priority levels.
    """
    
    def __init__(self):
        self._handlers: Dict[str, Dict[EventPriority, Set[EventHandler]]] = {}
        self._disabled_handlers: Set[EventHandler] = set()
        
    def register(self, event_name: str, handler: EventHandler, 
                priority: EventPriority = EventPriority.NORMAL) -> None:
        """Register an event handler with priority."""
        if event_name not in self._handlers:
            self._handlers[event_name] = {p: set() for p in EventPriority}
        
        self._handlers[event_name][priority].add(handler)
        logger.debug(f"Registered handler {handler.__name__} for event {event_name} "
                    f"with priority {priority.name}")
        
    def unregister(self, event_name: str, handler: EventHandler) -> None:
        """Unregister an event handler."""
        if event_name in self._handlers:
            for priority in EventPriority:
                self._handlers[event_name][priority].discard(handler)
                
        logger.debug(f"Unregistered handler {handler.__name__} from event {event_name}")
        
    def disable_handler(self, handler: EventHandler) -> None:
        """Temporarily disable an event handler."""
        self._disabled_handlers.add(handler)
        
    def enable_handler(self, handler: EventHandler) -> None:
        """Re-enable a disabled event handler."""
        self._disabled_handlers.discard(handler)
        
    async def dispatch(self, event: Event) -> None:
        """
        Dispatch an event to all registered handlers in priority order.
        Handlers are called asynchronously but in sequence to maintain priority order.
        """
        if event.name not in self._handlers:
            return
            
        logger.debug(f"Dispatching event {event.name}")
        
        # Call handlers in priority order
        for priority in EventPriority:
            if event.cancelled and priority != EventPriority.MONITOR:
                continue
                
            handlers = self._handlers[event.name][priority]
            for handler in handlers:
                if handler in self._disabled_handlers:
                    continue
                    
                try:
                    await handler(event)
                    event.handled = True
                except Exception as e:
                    logger.error(f"Error in event handler {handler.__name__}: {e}")
                    
        logger.debug(f"Finished dispatching event {event.name} "
                    f"(cancelled={event.cancelled}, handled={event.handled})")

# Global event dispatcher instance
event_dispatcher = EventDispatcher()

# Example event handler decorator
def event_handler(event_name: str, priority: EventPriority = EventPriority.NORMAL):
    """Decorator to register event handlers."""
    def decorator(func: EventHandler) -> EventHandler:
        event_dispatcher.register(event_name, func, priority)
        return func
    return decorator 