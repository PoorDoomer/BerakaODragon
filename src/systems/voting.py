"""
Voting system module for handling group decisions.
"""

from typing import List, Dict, Tuple, Optional
from ..core.player import Player
from ..ui.display import display_manager
from ..ui.colors import color_manager

class VotingSystem:
    """Manages group voting and decision making."""
    
    def __init__(self):
        """Initialize voting system."""
        self.votes: Dict[str, str] = {}  # player_name: choice_id
        self.current_vote: Optional[Dict] = None

    def start_vote(self, options: List[Dict], vote_type: str = "majority") -> None:
        """
        Start a new vote.
        
        Args:
            options (List[Dict]): List of voting options
            vote_type (str): Type of voting ("majority" or "unanimous")
        """
        self.current_vote = {
            "options": options,
            "type": vote_type,
            "votes": {},
            "status": "active"
        }
        self.votes.clear()

    def cast_vote(self, player: Player, choice_index: int) -> str:
        """
        Record a player's vote.
        
        Args:
            player (Player): Player casting the vote
            choice_index (int): Index of chosen option
            
        Returns:
            str: Status message
        """
        if not self.current_vote or self.current_vote["status"] != "active":
            return "No active vote"
            
        if not 0 <= choice_index < len(self.current_vote["options"]):
            return "Invalid choice"
            
        self.votes[player.name] = choice_index
        return f"{player.name} has voted!"

    def check_result(self, total_players: int) -> Tuple[bool, Optional[Dict]]:
        """
        Check if voting is complete and get result.
        
        Args:
            total_players (int): Total number of players
            
        Returns:
            Tuple[bool, Optional[Dict]]: (Is complete, Winning option)
        """
        if not self.current_vote:
            return False, None
            
        # Count votes
        vote_counts = {}
        for choice_index in self.votes.values():
            vote_counts[choice_index] = vote_counts.get(choice_index, 0) + 1

        # Check if everyone has voted
        if len(self.votes) < total_players:
            return False, None

        if self.current_vote["type"] == "unanimous":
            # Check for unanimous decision
            if len(vote_counts) == 1 and list(vote_counts.values())[0] == total_players:
                winning_index = list(vote_counts.keys())[0]
                return True, self.current_vote["options"][winning_index]
            return True, None  # Vote failed
            
        else:  # majority
            # Find option with most votes
            max_votes = max(vote_counts.values())
            winners = [idx for idx, count in vote_counts.items() if count == max_votes]
            
            # Handle tie
            if len(winners) == 1:
                return True, self.current_vote["options"][winners[0]]
            else:
                # In case of tie, choose first option
                return True, self.current_vote["options"][winners[0]]

    def display_vote_status(self, players: List[Player]) -> None:
        """
        Display current voting status.
        
        Args:
            players (List[Player]): List of all players
        """
        if not self.current_vote:
            return
            
        # Display vote type
        vote_type = self.current_vote["type"].capitalize()
        print(color_manager.theme_color('title', f"\n{vote_type} Vote in Progress"))
        
        # Display options
        print(color_manager.theme_color('info', "\nOptions:"))
        for i, option in enumerate(self.current_vote["options"]):
            print(f"{i+1}. {option.get('text', '')}")
            
        # Display who has voted
        print(color_manager.theme_color('info', "\nVotes Cast:"))
        for player in players:
            if player.name in self.votes:
                status = color_manager.theme_color('success', "✓ Voted")
            else:
                status = color_manager.theme_color('error', "✗ Not Voted")
            print(f"{player.name}: {status}")

    def end_vote(self) -> None:
        """End current vote."""
        if self.current_vote:
            self.current_vote["status"] = "completed"
        self.votes.clear()

    def get_vote_summary(self) -> Dict:
        """
        Get summary of voting results.
        
        Returns:
            Dict: Vote summary information
        """
        if not self.current_vote:
            return {}
            
        vote_counts = {}
        for choice_index in self.votes.values():
            vote_counts[choice_index] = vote_counts.get(choice_index, 0) + 1
            
        return {
            "type": self.current_vote["type"],
            "total_votes": len(self.votes),
            "vote_counts": vote_counts,
            "status": self.current_vote["status"]
        }

# Create default voting system instance
voting_system = VotingSystem() 