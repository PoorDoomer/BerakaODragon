# Json2RPGDesu Story Writing Guide ✨

## Table of Contents
- [Introduction](#introduction)
- [Story Structure](#story-structure)
- [Scene Components](#scene-components)
- [Choice Types](#choice-types)
- [Effects and Status](#effects-and-status)
- [Best Practices](#best-practices)

## Introduction

Json2RPGDesu is a kawaii text-based RPG engine that allows you to create interactive stories with multiple paths, combat encounters, and voting systems. Stories are written in JSON format and can include various types of interactions and effects.

## Story Structure

A basic story consists of connected scenes. Each scene must have:
- A unique scene ID
- A description
- One or more choices

Example structure:
```json
{
  "start": {
    "description": {
      "text": "You wake up in a magical forest. The air sparkles with fairy dust.",
      "color": "cyan"
    },
    "choices": [
      {
        "text": "Follow the glowing path",
        "next_scene": "fairy_path"
      }
    ]
  }
}
```

## Scene Components

### Description
- `text`: The main narrative text shown to players
- `color`: Text color (options: black, red, green, yellow, blue, magenta, cyan, white)

### Player References
Use placeholders to reference players:
- `{current_player}`: Currently active player
- `{player1}`, `{player2}`, etc.: Specific players

Example:
```json
{
  "description": {
    "text": "{current_player} discovers a mysterious scroll.",
    "color": "yellow"
  }
}
```

## Choice Types

### 1. Basic Choice
Simple navigation between scenes:
```json
{
  "text": "Enter the cave",
  "next_scene": "dark_cave"
}
```

### 2. Combat Choice
Initiates a battle sequence:
```json
{
  "text": "Fight the dragon",
  "combat": {
    "name": "Ancient Dragon",
    "health": 100,
    "attack": 15,
    "defense": 10
  },
  "success": "dragon_defeated",
  "failure": "game_over"
}
```

### 3. Voting Choice
Group decision making:
```json
{
  "text": "The group must decide...",
  "voting_system": {
    "options": [
      {
        "text": "Go left",
        "scene": "left_path"
      },
      {
        "text": "Go right",
        "scene": "right_path"
      }
    ],
    "tie_breaker": "random"
  }
}
```

## Effects and Status

You can add effects to choices that impact player stats:

```json
{
  "text": "Drink the potion",
  "next_scene": "continue_adventure",
  "effect": {
    "heal": 20,
    "buff_attack": 5,
    "buff_defense": 3
  }
}
```

Available effects:
- `heal`: Restore HP
- `damage`: Deal damage
- `buff_attack`: Increase attack
- `buff_defense`: Increase defense

## Best Practices

1. **Story Flow**
   - Start with an engaging introduction
   - Provide clear consequences for choices
   - Include multiple paths to maintain replayability

2. **Writing Style**
   - Keep descriptions concise but vivid
   - Use consistent tone throughout
   - Include kawaii elements for theme consistency

3. **Balance**
   - Mix different choice types
   - Balance combat difficulty
   - Ensure all paths are meaningful

4. **Testing**
   - Test all paths
   - Verify combat balance
   - Check for dead ends

## Example Mini-Story

```json
{
  "start": {
    "description": {
      "text": "Welcome to the Magical Academy! {current_player}, you're about to begin your first day as a student.",
      "color": "cyan"
    },
    "choices": [
      {
        "text": "Head to the Wand Selection ceremony",
        "next_scene": "wand_selection"
      }
    ]
  },
  "wand_selection": {
    "description": {
      "text": "Three wands lie before you, each glowing with different colored auras.",
      "color": "magenta"
    },
    "choices": [
      {
        "text": "Choose the red wand (Attack boost)",
        "next_scene": "class_start",
        "effect": {
          "buff_attack": 5
        }
      },
      {
        "text": "Choose the blue wand (Defense boost)",
        "next_scene": "class_start",
        "effect": {
          "buff_defense": 5
        }
      }
    ]
  }
}
```

Remember to save your story as `story.json` in the same directory as the game files! Happy story writing! (◕‿◕✿)