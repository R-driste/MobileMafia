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
        self.vote_counts = {}  
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

#MAIN

import badge

#three screens, host, game dets, lobby
class App(badge.BaseApp):
    def on_open(self) -> None:
        self.personal_player = Player(badge.contacts.my_contact().name)
        self.screens = ["host", "dets", "lobby"]
        self.last_time = badge.time.monotonic()
        self.current_screen = 0  # Changed to index-based
        self.active_players = []
        self.stage = "unstarted"
        self.stages = ["waiting", "night", "day", "voting"]

    def add_player(self, player: Player) -> None:
        self.active_players.append(player)
        self.logger.info(f"Added player: {player}")

    def render_screen(self) -> None:
        badge.display.fill(1)
        # Call the correct render method based on current_screen index
        if self.current_screen == 0:
            self.render_host()
        elif self.current_screen == 1:
            self.render_dets()
        elif self.current_screen == 2:
            self.render_lobby()
        badge.display.show()

    # Button handlers according to Shipwrecked PCB App API
    def on_button_press(self, button: badge.Button) -> None:
        """Handle button presses for navigation and game actions"""
        if button == badge.Button.SW3:  # Home button
            self.on_home_press()
        elif button == badge.Button.SW12:  # Right button
            self.on_right_press()
        elif button == badge.Button.SW4:  # Select button
            self.on_select_press()

    def on_home_press(self) -> None:
        """SW3 - Home button: Return to main menu or start new game"""
        if self.current_screen != 0:
            self.current_screen = 0
            self.stage = "unstarted"
            self.active_players = []
            self.logger.info("Returned to home screen")
        else:
            # If already on home, start hosting a new game
            self.start_hosting()

    def on_right_press(self) -> None:
        """SW12 - Right button: Navigate to next screen or next action"""
        if self.current_screen < len(self.screens) - 1:
            self.current_screen += 1
            self.logger.info(f"Navigated to screen {self.current_screen}")
        else:
            # Wrap around to first screen
            self.current_screen = 0
            self.logger.info("Wrapped to first screen")

    def on_select_press(self) -> None:
        """SW4 - Select button: Confirm action or select option"""
        if self.current_screen == 0:  # Host screen
            if self.stage == "unstarted":
                self.start_game()
            else:
                self.pause_game()
        elif self.current_screen == 1:  # Details screen
            self.refresh_game_details()
        elif self.current_screen == 2:  # Lobby screen
            self.ready_up()

    def start_hosting(self) -> None:
        """Start hosting a new game"""
        self.stage = "waiting"
        self.active_players = [self.personal_player]  # Add self to active players
        self.logger.info("Started hosting new game")

    def start_game(self) -> None:
        """Start the game when host presses select"""
        if len(self.active_players) >= 3:  # Minimum players to start
            self.stage = "night"
            self.assign_roles()
            self.logger.info("Game started!")
        else:
            self.logger.info("Need at least 3 players to start")

    def pause_game(self) -> None:
        """Pause the current game"""
        if self.stage != "unstarted":
            self.stage = "paused"
            self.logger.info("Game paused")

    def refresh_game_details(self) -> None:
        """Refresh game details when on details screen"""
        self.logger.info("Refreshed game details")

    def ready_up(self) -> None:
        """Mark player as ready in lobby"""
        if self.stage == "waiting":
            self.logger.info("Player marked as ready")

    def assign_roles(self) -> None:
        """Assign roles to players at game start"""
        import random
        roles = ["Kraken", "Kraken", "Villager", "Villager", "cop"]
        random.shuffle(roles)
        
        for i, player in enumerate(self.active_players):
            if i < len(roles):
                player.assign_role(roles[i])
            else:
                player.assign_role("Villager")
        
        self.logger.info("Roles assigned to players")

    #main welcome screen
    def on_packet(self, packet: badge.radio.Packet, in_foreground: bool) -> None:
        if packet.app_number != 0:  # Fixed: Use actual app number from manifest
            return
        try:
            data_str = packet.data.decode("utf-8")
            self.logger.info(f"Received packet: {data_str} from {packet.source}")
            if data_str.startswith("JOIN_REQ:"):
                name = data_str[len("JOIN_REQ:"):].strip()
                self.handle_join_request(name, packet.source)

            elif data_str.startswith("JOIN_ACK:"):
                self.handle_join_ack(data_str[len("JOIN_ACK:"):].strip())

        except Exception as e:
            self.logger.error(f"Error decoding packet: {e}")

    def handle_join_request(self, name: str, source) -> None:
        """Handle join request from another player"""
        new_player = Player(name)
        new_player.id = source
        self.add_player(new_player)
        # Send join acknowledgment
        ack_data = f"JOIN_ACK:{name}".encode("utf-8")
        badge.radio.send(ack_data, destination=source)

    def handle_join_ack(self, data: str) -> None:
        """Handle join acknowledgment"""
        self.logger.info(f"Join acknowledged: {data}")

    def render_welcome(self) -> None:
        badge.display.nice_text("Welcome to\nMafia!", 0, 0, font=24, color=0)
        badge.display.nice_text("Press Home to\nstart hosting", 0, 64, font=24, color=0)
        badge.display.nice_text("Press Right to\nnavigate", 0, 88, font=24, color=0)

    #host screen
    def render_host(self) -> None:
        badge.display.nice_text("Hosting Game!", 0, 0, font=32, color=0)
        badge.display.nice_text(f"Players: {len(self.active_players)}", 0, 32, font=24, color=0)
        badge.display.nice_text("Press SW4 to start", 0, 64, font=18, color=0)
        badge.display.nice_text("Press SW11 for details", 0, 88, font=18, color=0)
        
        y_offset = 120
        for player in self.active_players:
            badge.display.nice_text(f"• {player.name}", 0, y_offset, font=16, color=0)
            y_offset += 20

    #get players to join
    def render_join(self) -> None:
        badge.display.nice_text("Welcome to\nMafia!", 0, 0, font=32, color=0)
        badge.display.nice_text("Press SW4 to\nstart hosting", 0, 64, font=24, color=0)
    
    #render game details
    def render_dets(self) -> None:
        badge.display.nice_text("Game Details", 0, 0, font=32, color=0)
        
        if self.personal_player.role == "unassigned":
            badge.display.nice_text("Role: Not assigned", 0, 32, font=24, color=0)
        else:
            badge.display.nice_text(f"Role: {self.personal_player.role}", 0, 32, font=24, color=0)
        
        badge.display.nice_text(f"Stage: {self.stage}", 0, 56, font=24, color=0)
        badge.display.nice_text(f"Players: {len(self.active_players)}", 0, 80, font=24, color=0)
        badge.display.nice_text("Press Right for lobby", 0, 104, font=24, color=0)

    #get game lobby
    def render_lobby(self) -> None:
        if self.stage == "unstarted":
            badge.display.nice_text("Waiting for\nhost to start\nthe game...", 0, 0, font=32, color=0)
        elif self.stage == "waiting":
            badge.display.nice_text("Waiting for\nplayers to\njoin...", 0, 0, font=32, color=0)
        elif self.stage == "night":
            badge.display.nice_text("Night phase", 0, 0, font=32, color=0)
            badge.display.nice_text("Please wait...", 0, 32, font=24, color=0)
        elif self.stage == "day":
            badge.display.nice_text("Day phase", 0, 0, font=32, color=0)
            badge.display.nice_text("Discuss and vote!", 0, 32, font=24, color=0)
        elif self.stage == "voting":
            badge.display.nice_text("Voting phase", 0, 0, font=32, color=0)
            badge.display.nice_text("Choose who to eliminate", 0, 32, font=24, color=0)
        else:
            badge.display.nice_text(f"Game status:\n{self.stage}", 0, 0, font=32, color=0)
        
        badge.display.nice_text("Press Home to return", 0, 64, font=24, color=0)

    def loop(self) -> None:
        """Main game loop - called every frame"""
        current_time = badge.time.monotonic()
        
        # Update game state based on time if needed
        if current_time - self.last_time > 1.0:  # Every second
            self.last_time = current_time
            # Add any periodic game logic here
        
        # Render the current screen. Should only happen if update.
        if badge.input.get_button(badge.input.Buttons.SW4):
            self.on_select_press()
        if badge.input.get_button(badge.input.Buttons.SW11):
            self.render_dets()
        else:
            self.render_screen()

        