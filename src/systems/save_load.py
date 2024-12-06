"""
Save/Load system module for game state persistence.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from ..core.player import Player, PlayerStats, Inventory

class SaveLoadError(Exception):
    """Base class for save/load errors."""
    pass

class SaveManager:
    """Manages saving and loading game states."""
    
    def __init__(self, save_dir: str = "saves"):
        """
        Initialize save manager.
        
        Args:
            save_dir (str): Directory for save files
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

    def serialize_player(self, player: Player) -> Dict:
        """
        Convert player object to serializable dict.
        
        Args:
            player (Player): Player to serialize
            
        Returns:
            Dict: Serialized player data
        """
        return {
            "name": player.name,
            "stats": {
                "health": player.stats.health,
                "max_health": player.stats.max_health,
                "attack": player.stats.attack,
                "defense": player.stats.defense
            },
            "inventory": {
                "items": player.inventory.items
            },
            "is_alive": player.is_alive,
            "status_effects": player.status_effects
        }

    def deserialize_player(self, data: Dict) -> Player:
        """
        Create player object from serialized data.
        
        Args:
            data (Dict): Serialized player data
            
        Returns:
            Player: Reconstructed player object
        """
        player = Player(data["name"])
        
        # Restore stats
        stats = data["stats"]
        player.stats = PlayerStats(
            health=stats["health"],
            max_health=stats["max_health"],
            attack=stats["attack"],
            defense=stats["defense"]
        )
        
        # Restore inventory
        player.inventory = Inventory(data["inventory"]["items"])
        
        # Restore state
        player.is_alive = data["is_alive"]
        player.status_effects = data["status_effects"]
        
        return player

    def save_game(self, 
                 players: List[Player],
                 current_scene: str,
                 story_data: Dict,
                 save_name: Optional[str] = None) -> str:
        """
        Save current game state.
        
        Args:
            players (List[Player]): List of players
            current_scene (str): Current scene ID
            story_data (Dict): Current story data
            save_name (Optional[str]): Name for save file
            
        Returns:
            str: Path to save file
            
        Raises:
            SaveLoadError: If save fails
        """
        try:
            # Create save data
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "players": [self.serialize_player(p) for p in players],
                "current_scene": current_scene,
                "story_data": story_data,
                "version": "1.0.0"  # Add version for future compatibility
            }
            
            # Generate save name if not provided
            if not save_name:
                save_name = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            elif not save_name.endswith('.json'):
                save_name += '.json'
            
            # Save to file
            save_path = self.save_dir / save_name
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
                
            return str(save_path)
            
        except Exception as e:
            raise SaveLoadError(f"Failed to save game: {str(e)}")

    def load_game(self, save_file: str) -> Dict:
        """
        Load game state from file.
        
        Args:
            save_file (str): Path to save file
            
        Returns:
            Dict: Loaded game state
            
        Raises:
            SaveLoadError: If load fails
        """
        try:
            save_path = self.save_dir / save_file
            if not save_path.exists():
                raise SaveLoadError(f"Save file not found: {save_file}")
                
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            # Version check for future compatibility
            if save_data.get("version", "1.0.0") > "1.0.0":
                raise SaveLoadError("Save file from newer version not supported")
                
            # Reconstruct players
            save_data["players"] = [
                self.deserialize_player(p_data)
                for p_data in save_data["players"]
            ]
            
            return save_data
            
        except Exception as e:
            raise SaveLoadError(f"Failed to load game: {str(e)}")

    def list_saves(self) -> List[Dict]:
        """
        Get list of available save files.
        
        Returns:
            List[Dict]: Save file information
        """
        saves = []
        for save_file in self.save_dir.glob("*.json"):
            try:
                with open(save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                saves.append({
                    "filename": save_file.name,
                    "timestamp": save_data.get("timestamp", "Unknown"),
                    "players": [p["name"] for p in save_data.get("players", [])],
                    "scene": save_data.get("current_scene", "Unknown")
                })
            except:
                continue  # Skip invalid save files
        return sorted(saves, key=lambda x: x["timestamp"], reverse=True)

    def delete_save(self, save_file: str) -> bool:
        """
        Delete a save file.
        
        Args:
            save_file (str): Save file to delete
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            save_path = self.save_dir / save_file
            if save_path.exists():
                save_path.unlink()
                return True
        except:
            pass
        return False

    def auto_save(self, 
                 players: List[Player],
                 current_scene: str,
                 story_data: Dict) -> Optional[str]:
        """
        Create automatic save.
        
        Args:
            players (List[Player]): List of players
            current_scene (str): Current scene ID
            story_data (Dict): Current story data
            
        Returns:
            Optional[str]: Path to save file if successful
        """
        try:
            save_name = "autosave.json"
            return self.save_game(players, current_scene, story_data, save_name)
        except:
            return None  # Fail silently for auto-save

# Create default save manager instance
save_manager = SaveManager() 