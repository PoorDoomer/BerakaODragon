# Json2RPGDesu Refactoring Guide 🔧

## Proposed Directory Structure

```
json2rpgdesu/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── game.py           # Main game logic
│   │   ├── player.py         # Player class
│   │   └── story_loader.py   # Story loading and validation
│   ├── combat/
│   │   ├── __init__.py
│   │   ├── combat_manager.py # Combat system
│   │   ├── actions.py        # Combat actions
│   │   └── effects.py        # Status effects
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── display.py        # Display functions
│   │   ├── animations.py     # Animation system
│   │   └── colors.py         # Color configurations
│   ├── systems/
│   │   ├── __init__.py
│   │   ├── voting.py         # Voting system
│   │   ├── save_load.py      # Save/Load system
│   │   └── progress.py       # Progress tracking
│   └── utils/
│       ├── __init__.py
│       ├── exceptions.py     # Custom exceptions
│       └── helpers.py        # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_combat.py
│   ├── test_story.py
│   └── test_player.py
├── examples/
│   ├── stories/
│   │   └── demo_story.json
│   └── custom_game.py
└── main.py                   # New entry point
```

## Module Breakdown

### 1. Core Module (`src/core/`)

#### game.py
```python
from typing import List, Dict
from .player import Player
from .story_loader import StoryLoader

class Game:
    def __init__(self):
        self.story_loader = StoryLoader()
        self.players: List[Player] = []
        self.current_scene: str = "start"
    
    def run(self):
        """Main game loop"""
        pass
```

#### player.py
```python
class Player:
    def __init__(self, name: str):
        self.name = name
        self.stats = PlayerStats()
        self.inventory = Inventory()
    
    def apply_effect(self, effect: Dict):
        """Handle status effects"""
        pass
```

#### story_loader.py
```python
class StoryLoader:
    def __init__(self):
        self.schema = self._load_schema()
    
    def load_story(self, filename: str) -> Dict:
        """Load and validate story file"""
        pass
```

### 2. Combat Module (`src/combat/`)

#### combat_manager.py
```python
from typing import Dict
from ..core.player import Player

class CombatManager:
    def __init__(self):
        self.combat_log = []
    
    def handle_combat(self, players: List[Player], enemy: Dict):
        """Main combat loop"""
        pass
```

#### actions.py
```python
class CombatAction:
    def execute(self, source, target):
        """Execute combat action"""
        pass

class Attack(CombatAction):
    def execute(self, source, target):
        """Handle attack action"""
        pass
```

### 3. UI Module (`src/ui/`)

#### display.py
```python
class DisplayManager:
    def __init__(self):
        self.terminal_width = self._get_terminal_width()
    
    def display_scene(self, scene: Dict):
        """Render scene"""
        pass
    
    def create_status_box(self, player: 'Player') -> str:
        """Create player status display"""
        pass
```

#### animations.py
```python
class AnimationSystem:
    def animate_attack(self, attacker: str, defender: str, damage: int):
        """Handle attack animation"""
        pass
    
    def loading_animation(self, text: str = "Loading", duration: int = 2):
        """Display loading animation"""
        pass
```

### 4. Systems Module (`src/systems/`)

#### voting.py
```python
class VotingSystem:
    def handle_vote(self, players: List[Player], options: List[Dict]):
        """Process group voting"""
        pass
```

#### save_load.py
```python
class SaveManager:
    def save_game(self, game_state: Dict, filename: str):
        """Save game state"""
        pass
    
    def load_game(self, filename: str) -> Dict:
        """Load game state"""
        pass
```

## Main Entry Point (main.py)

```python
from src.core.game import Game
from src.utils.exceptions import GameError

def main():
    try:
        game = Game()
        game.run()
    except GameError as e:
        print(f"Game Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    main()
```

## Migration Steps

1. **Create Directory Structure**
   ```bash
   mkdir -p src/{core,combat,ui,systems,utils} tests examples/stories
   ```

2. **Move Core Components**
   - Extract Player class to `player.py`
   - Move game logic to `game.py`
   - Create story loading system in `story_loader.py`

3. **Separate Combat System**
   - Move combat logic to `combat_manager.py`
   - Create action classes in `actions.py`
   - Extract effect system to `effects.py`

4. **Isolate UI Components**
   - Move display functions to `display.py`
   - Extract animations to `animations.py`
   - Create color system in `colors.py`

5. **Create Support Systems**
   - Implement voting system in `voting.py`
   - Create save/load system in `save_load.py`
   - Add progress tracking in `progress.py`

## Benefits of Refactoring

1. **Modularity**
   - Each component is self-contained
   - Easier to maintain and update
   - Better code organization

2. **Testability**
   - Isolated components are easier to test
   - Clear dependencies
   - Mock objects for testing

3. **Scalability**
   - Easy to add new features
   - Clear extension points
   - Better performance management

4. **Maintainability**
   - Clear code structure
   - Reduced complexity
   - Better documentation

## Example Usage

```python
# Creating a custom game
from json2rpgdesu.core.game import Game
from json2rpgdesu.combat.actions import CustomAction
from json2rpgdesu.ui.display import DisplayManager

class CustomGame(Game):
    def __init__(self):
        super().__init__()
        self.display = DisplayManager()
        
    def add_custom_action(self, action: CustomAction):
        """Add custom combat action"""
        pass
```

## Testing Structure

```python
# test_combat.py
import unittest
from src.combat.combat_manager import CombatManager

class TestCombat(unittest.TestCase):
    def setUp(self):
        self.combat = CombatManager()
    
    def test_damage_calculation(self):
        """Test combat damage calculation"""
        pass
```

## Future Considerations

1. **Plugin System**
   - Create plugin architecture
   - Allow custom actions/effects
   - Support modding

2. **Event System**
   - Implement event dispatcher
   - Add hooks for custom behavior
   - Support event logging

3. **Configuration System**
   - External config files
   - Runtime configuration
   - Environment variables

4. **Performance Optimization**
   - Caching system
   - Lazy loading
   - Resource management

## Implementation Timeline

1. **Phase 1: Core Refactoring**
   - Create basic structure
   - Move core components
   - Basic testing

2. **Phase 2: System Separation**
   - Split combat system
   - Create UI module
   - Add basic tests

3. **Phase 3: Enhancement**
   - Add new features
   - Improve testing
   - Documentation

4. **Phase 4: Optimization**
   - Performance tuning
   - Code cleanup
   - Final testing 