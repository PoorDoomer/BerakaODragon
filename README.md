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

## 🚀 Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Json2RPGDesu.git
cd Json2RPGDesu
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the game**
```bash
python test.py
```

## 📋 Requirements

- Python 3.6+
- colorama
- Other dependencies listed in `requirements.txt`

## 🎮 How to Play

1. Launch the game
2. Enter player names (supports multiple players)
3. Navigate through the story by making choices
4. Engage in combat and make group decisions
5. Enjoy multiple endings based on your choices!

## 📝 Creating Stories

Stories are written in JSON format. Check out our [Story Writing Guide](story_guide.md) for detailed instructions on creating your own adventures!

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

Want to contribute? Great! Here are some ways you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request


## 🙏 Acknowledgments

- Inspired by classic text-based RPGs
- Built with love for the anime and kawaii community
- Special thanks to all contributors!

## 📞 Contact

- GitHub: [@PoorDoomer](https://github.com/PoorDoomer)
- Twitter: [@Khayef1](https://twitter.com/Khayef1)

---

Made with ❤️ and lots of ✨ magic ✨ 