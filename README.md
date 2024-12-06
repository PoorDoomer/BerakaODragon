# Json2RPGDesu 🎮✨

A kawaii text-based RPG engine written in Python that lets you create and play interactive stories with multiple paths, combat encounters, and group decision-making mechanics.

![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)

## ✨ Features

- 🎭 **Interactive Storytelling**: Create branching narratives with multiple paths and endings
- ⚔️ **Turn-Based Combat**: Engage in strategic battles with customizable enemies
- 🤝 **Multiplayer Support**: Play with friends in a shared story experience
- 🗳️ **Voting System**: Make group decisions that affect the story
- 🎨 **Colorful UI**: Enjoy a kawaii-themed terminal interface with pastel colors
- 💝 **Status Effects**: Implement buffs, healing, and other effects
- 📝 **Story Editor**: Create and edit stories using JSON format
- 🔌 **Plugin System**: Extend the game with custom plugins
- 🎯 **Event System**: Hook into game events for custom behavior

## 🚀 Documentation

- [Story Writing Guide](story_guide.md) - Comprehensive guide for creating adventures
- [Story Guidelines](Story_Guidelines.md) - Best practices and formatting rules
- [Technical Documentation](technical_docs.md) - Detailed system architecture and development guide
- [Refactoring Guide](refactoring_guide.md) - Code structure and organization guide

## 🛠️ Setup & Installation

1. **Requirements**
   - Python 3.6+
   - pip package manager
   - virtualenv (recommended)

2. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Json2RPGDesu.git
   cd Json2RPGDesu
   ```

3. **Create and activate virtual environment (recommended)**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix/MacOS
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Install development dependencies (for contributing)**
   ```bash
   pip install -r requirements-dev.txt
   ```

## 🎮 Running the Game

1. **Start the game**
   ```bash
   python -m src.game
   ```

2. **Command line options**
   ```bash
   python -m src.game --multiplayer  # Enable multiplayer mode
   python -m src.game --debug        # Enable debug logging
   python -m src.game --story path/to/story.json  # Load custom story
   ```

## 🧪 Testing

1. **Run all tests**
   ```bash
   pytest
   ```

2. **Run specific test modules**
   ```bash
   pytest tests/test_game.py
   pytest tests/test_combat/
   ```

3. **Run with coverage**
   ```bash
   pytest --cov=src tests/
   ```

## 📝 Plugin System

The game includes a powerful plugin system that allows you to extend functionality:

### Creating a Plugin

1. Create a new directory in `plugins/` for your plugin
2. Create a `plugin.py` file with your plugin implementation:

```python
Basic story structure:
```json
{
  "start": {
    "description": {
      "text": "Your adventure begins here!",
      "color": "cyan"
    },
    "choices": [
      {
        "text": "Begin your journey",
        "next_scene": "first_choice"
      }
    ]
  }
}
```

## 🎯 Features in Detail

### Combat System
- Turn-based battles
- Strategic choices (Attack, Defend, Heal, Special)
- Status effects and buffs
- Health bar visualization

### Multiplayer Features
- Multiple player support
- Turn rotation system
- Group voting mechanics
- Shared adventure experience

### UI Features
- Colorful terminal interface
- ASCII art decorations
- Animated effects
- Progress tracking

## 🛠️ Development

1. **Project Structure**
   ```
   Json2RPGDesu/
   ├── src/
   │   ├── core/         # Core game mechanics
   │   ├── combat/       # Combat system
   │   ├── ui/           # User interface
   │   ├── systems/      # Game systems
   │   └── game.py       # Main game loop
   ├── tests/            # Test files
   ├── stories/          # Story JSON files
   └── docs/             # Documentation
   ```

2. **Contributing**
   - Fork the repository
   - Create feature branch (`git checkout -b feature/amazing-feature`)
   - Write tests for new features
   - Ensure all tests pass
   - Update documentation
   - Submit pull request

3. **Code Style**
   - Follow PEP 8
   - Use type hints
   - Write docstrings
   - Keep functions focused and small

## 🙏 Acknowledgments

- Inspired by classic text-based RPGs
- Built with love for the anime and kawaii community
- Special thanks to all contributors!

## 📞 Contact

- GitHub: [@PoorDoomer](https://github.com/PoorDoomer)
- Twitter: [@Khayef1](https://twitter.com/Khayef1)

---

Made with ❤️ and lots of ✨ magic ✨