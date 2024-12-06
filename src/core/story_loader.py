"""
Story loading and validation module.
"""

import json
from typing import Dict, Any
from pathlib import Path

class StoryValidationError(Exception):
    """Raised when story validation fails."""
    pass

class StoryLoader:
    """
    Handles loading and validating story files.
    """
    
    def __init__(self):
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict:
        """Load the story schema definition."""
        return {
            "type": "object",
            "required": ["scenes"],
            "properties": {
                "scenes": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z0-9_-]+$": {
                            "type": "object",
                            "required": ["description", "choices"],
                            "properties": {
                                "description": {
                                    "type": "object",
                                    "required": ["text"],
                                    "properties": {
                                        "text": {"type": "string"},
                                        "color": {"type": "string"}
                                    }
                                },
                                "choices": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": ["text"],
                                        "properties": {
                                            "text": {"type": "string"},
                                            "type": {"type": "string"},
                                            "next_scene": {"type": "string"},
                                            "combat": {"type": "object"},
                                            "voting_system": {"type": "object"},
                                            "effect": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    def validate_story(self, story_data: Dict) -> None:
        """
        Validate story data against schema.
        
        Args:
            story_data (Dict): Story data to validate
            
        Raises:
            StoryValidationError: If validation fails
        """
        # Basic structure validation
        if not isinstance(story_data, dict):
            raise StoryValidationError("Story data must be a dictionary")
        
        if "scenes" not in story_data:
            raise StoryValidationError("Story must contain 'scenes' object")
            
        if "start" not in story_data["scenes"]:
            raise StoryValidationError("Story must contain 'start' scene")
        
        # Validate each scene
        for scene_id, scene in story_data["scenes"].items():
            self._validate_scene(scene_id, scene, story_data["scenes"])

    def _validate_scene(self, scene_id: str, scene: Dict, all_scenes: Dict) -> None:
        """
        Validate individual scene data.
        
        Args:
            scene_id (str): ID of the scene
            scene (Dict): Scene data to validate
            all_scenes (Dict): All scenes for reference validation
            
        Raises:
            StoryValidationError: If validation fails
        """
        if "description" not in scene:
            raise StoryValidationError(f"Scene '{scene_id}' must contain 'description'")
            
        if "text" not in scene["description"]:
            raise StoryValidationError(f"Scene '{scene_id}' description must contain 'text'")
            
        if "choices" not in scene:
            raise StoryValidationError(f"Scene '{scene_id}' must contain 'choices'")
            
        # Validate choices
        for choice in scene["choices"]:
            if "text" not in choice:
                raise StoryValidationError(f"Choice in scene '{scene_id}' must contain 'text'")
                
            if "next_scene" in choice and choice["next_scene"] not in all_scenes:
                raise StoryValidationError(
                    f"Choice in scene '{scene_id}' references non-existent scene '{choice['next_scene']}'"
                )

    def load_story(self, filename: str) -> Dict[str, Any]:
        """
        Load and validate a story file.
        
        Args:
            filename (str): Path to the story file
            
        Returns:
            Dict[str, Any]: Validated story data
            
        Raises:
            FileNotFoundError: If story file doesn't exist
            StoryValidationError: If story validation fails
            json.JSONDecodeError: If JSON parsing fails
        """
        story_path = Path(filename)
        if not story_path.exists():
            raise FileNotFoundError(f"Story file not found: {filename}")
            
        with open(story_path, 'r', encoding='utf-8') as file:
            try:
                story_data = json.load(file)
            except json.JSONDecodeError as e:
                raise StoryValidationError(f"Invalid JSON in story file: {e}")
                
        self.validate_story(story_data)
        return story_data

    def get_scene(self, story_data: Dict, scene_id: str) -> Dict:
        """
        Get a specific scene from the story.
        
        Args:
            story_data (Dict): Story data
            scene_id (str): ID of the scene to get
            
        Returns:
            Dict: Scene data
            
        Raises:
            KeyError: If scene doesn't exist
        """
        if scene_id not in story_data["scenes"]:
            raise KeyError(f"Scene '{scene_id}' not found in story")
        return story_data["scenes"][scene_id] 