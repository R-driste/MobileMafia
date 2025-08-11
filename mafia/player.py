class Player():
    def __init__(self, name: str):
        self.name = name
        self.role = "unassigned"
        self.alive = True
        self.id = 0
        self.vote_target = None  # Who this player voted for
        self.votes_received = 0  # How many votes this player received
        self.has_voted = False   # Whether this player has voted this round
        
    def __repr__(self):
        return f"{self.name} ({self.role}) - {'Alive' if self.alive else 'Dead'}"
        
    def assign_role(self, role: str):
        self.role = role
        
    #kraken functions
    def kill(self, player):
        if self.role == "Kraken":
            player.alive = False
    
    # Voting functions
    def vote(self, target_player):
        """Vote for a player to eliminate"""
        if self.alive and not self.has_voted:
            self.vote_target = target_player
            self.has_voted = True
            return True
        return False
    
    def clear_vote(self):
        """Clear the player's vote for the next round"""
        self.vote_target = None
        self.has_voted = False
        self.votes_received = 0
    
    def receive_vote(self):
        """Increment vote count when someone votes for this player"""
        self.votes_received += 1
    
    def get_vote_info(self):
        """Get current voting information for this player"""
        return {
            "name": self.name,
            "alive": self.alive,
            "role": self.role,
            "votes_received": self.votes_received,
            "has_voted": self.has_voted,
            "vote_target": self.vote_target.name if self.vote_target else None
        }

class VotingResults:
    """Class to track and display voting results"""
    def __init__(self):
        self.votes = {}  # player_name -> vote_target_name
        self.vote_counts = {}  # player_name -> number_of_votes_received
        self.total_votes_cast = 0
        self.round_number = 0
        
    def add_vote(self, voter_name: str, target_name: str):
        """Record a vote from voter to target"""
        self.votes[voter_name] = target_name
        self.total_votes_cast += 1
        
        # Update vote count for target
        if target_name in self.vote_counts:
            self.vote_counts[target_name] += 1
        else:
            self.vote_counts[target_name] = 1
    
    def get_vote_summary(self):
        """Get a summary of all votes cast"""
        return {
            "total_votes": self.total_votes_cast,
            "vote_breakdown": self.vote_counts.copy(),
            "round": self.round_number
        }
    
    def get_elimination_candidate(self):
        """Get the player with the most votes (to be eliminated)"""
        if not self.vote_counts:
            return None
            
        max_votes = max(self.vote_counts.values())
        candidates = [name for name, votes in self.vote_counts.items() if votes == max_votes]
        
        if len(candidates) == 1:
            return candidates[0]  # Clear winner
        else:
            return candidates  # Tie - return list of tied players
    
    def display_results(self):
        """Format voting results for display"""
        if not self.vote_counts:
            return "No votes cast yet"
            
        result_lines = [f"Voting Results (Round {self.round_number})"]
        result_lines.append(f"Total votes: {self.total_votes_cast}")
        result_lines.append("")
        
        # Sort by vote count (highest first)
        sorted_votes = sorted(self.vote_counts.items(), key=lambda x: x[1], reverse=True)
        
        for player_name, vote_count in sorted_votes:
            result_lines.append(f"{player_name}: {vote_count} votes")
        
        # Show elimination candidate
        candidate = self.get_elimination_candidate()
        if isinstance(candidate, list):
            result_lines.append(f"\nTIE: {', '.join(candidate)}")
        elif candidate:
            result_lines.append(f"\nEliminated: {candidate}")
            
        return "\n".join(result_lines)
    
    def reset_round(self):
        """Reset for a new voting round"""
        self.votes.clear()
        self.vote_counts.clear()
        self.total_votes_cast = 0
        self.round_number += 1
    