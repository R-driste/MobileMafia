from player import Player
import badge

#three screens, host, game dets, lobby
class App(badge.BaseApp):
    def on_open(self) -> None:
        self.personal_player = Player(badge.contacts.my_contact().name)
        self.screens = ["host", "dets", "lobby"]
        self.last_time = badge.time.monotonic()
        self.current_screen = "host"
        self.active_players = []
        self.stage = "unstarted"
        self.stages = ["waiting", "night", "day", "voting"]

    def add_player(self, player: Player) -> None:
        self.active_players.append(player)
        self.logger.info(f"Added player: {player}")

    def render_screen(self) -> None:
        badge.display.fill(1)
        self.screens[self.current_screen]() #calls correct render
        badge.display.show()

    #main welcome screen
    def on_packet(self, packet: badge.radio.Packet, in_foreground: bool) -> None:
        if packet.app_number != YOUR_APP_NUMBER:
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

    def render_welcome(self) -> None:
        badge.display.nice_text("Welcome to\nKraken!", 0, 0, font=32, color=0)
        badge.display.nice_text("Press Top Left to\nstart a game", 0, 64, font=24, color=0)
        badge.display.nice_text("Press Top Right to\join a game", 0, 64, font=24, color=0)

    #host screen
    def render_host(self) -> None:
        badge.display.nice_text("Hosting Game ###!", 0, 0, font=32, color=0)
        badge.display.nice_text(f"# Players Joined: {len(self.active_players)}", 0, 64, font=24, color=0)
        badge.display.nice_text("LIST", 0, 64, font=24, color=0)
        y_offset = 50
        for player in self.active_players:
            badge.display.nice_text(player.name, 0, y_offset, font=24, color=0)

    #get players to join
    def render_join(self) -> None:
        badge.display.nice_text("Welcome to\nKraken!", 0, 0, font=32, color=0)
        badge.display.nice_text("Press Top Left to\nstart a game", 0, 64, font=24, color=0)
    
    #render game details
    def render_dets(self) -> None:
        if self.personal_player.role == "unassigned":
            badge.display.nice_text("Error. You have not\nbeen assigned\na role yet.", 0, 0, font=32, color=0)
        elif self.personal_player.role == "Kraken":
            badge.display.nice_text("You are a\nKraken member!", 0, 0, font=32, color=0)
        elif self.personal_player.role == "Villager":
            badge.display.nice_text("You are a\nVillager!", 0, 0, font=32, color=0)
        elif self.personal_player.role == "cop":
            badge.display.nice_text("You are a\nCop!", 0, 0, font=32, color=0)
        else:
            badge.display.nice_text("Something went wrong with your role!", 0, 0, font=32, color=0)

        badge.display.nice_text("Game Details", 0, 0, font=32, color=0)
        badge.display.nice_text(f"Role: {self.personal_player.role}", 0, 0, font=32, color=0)
        badge.display.nice_text("Player Statuses:", 0, 64, font=24, color=0)
        y_offset = 100
        for player in self.active_players:
            badge.display.nice_text(player.name, 0, y_offset, font=24, color=0)
            y_offset += 24

    #get game lobby
    def render_lobby(self) -> None:
        if self.stage == "unstarted":
            badge.display.nice_text("Waiting for\nhost to start\nthe game...", 0, 0, font=32, color=0)
        else:
            badge.display.nice_text(f"Game in\nprogress, currently in {self.stage}", 0, 0, font=32, color=0)
            if self.stage == "night":
                badge.display.nice_text("Night phase, please wait...", 0, 64, font=24, color=0)
            elif self.stage == "day":
                badge.display.nice_text("Daytime phase, go socialize!", 0, 64, font=24, color=0)
            elif self.stage == "voting":
                badge.display.nice_text("Daytime phase, go socialize!", 0, 64, font=24, color=0)
        badge.display.nice_text("")

    def cast_vote(self, voter_name: str, voted_name: str) -> None:
        old_vote = self.votes.get(voter_name)
        if old_vote:
            self.vote_counts[old_vote] = self.vote_counts.get(old_vote, 1) - 1
            if self.vote_counts[old_vote] <= 0:
                del self.vote_counts[old_vote]

        # Register new vote
        self.votes[voter_name] = voted_name
        self.vote_counts[voted_name] = self.vote_counts.get(voted_name, 0) + 1
        self.logger.info(f"{voter_name} voted for {voted_name}")
    
    def render_vote_screen(self) -> None:
        badge.display.fill(1)
        badge.display.nice_text("Voting Phase", 0, 0, font=32, color=0)
        if len(self.active_players) == 0:
            badge.display.nice_text("No players to vote for.", 0, 64, font=24, color=0)
            badge.display.show()
            return

        # Highlight currently selected player
        selected = self.active_players[self.voting_player_index].name
        badge.display.nice_text(f"Vote for:", 0, 50, font=24, color=0)
        badge.display.nice_text(selected, 0, 80, font=32, color=0)
        badge.display.nice_text("Use Left/Right to select", 0, 130, font=18, color=0)
        badge.display.nice_text("Press B to vote", 0, 150, font=18, color=0)
        badge.display.show()



    def loop(self) -> None:
        pass
        if badge.input.get_button("BTN_A") and not self.is_voting:
            self.is_voting = True
            self.voting_player_index = 0
            self.render_vote_screen()
            time.sleep(0.3)

        if self.is_voting:
            if badge.input.get_button("BTN_LEFT"):
                self.voting_player_index = (self.voting_player_index - 1) % len(self.active_players)
                self.render_vote_screen()
                time.sleep(0.2)

            elif badge.input.get_button("BTN_RIGHT"):
                self.voting_player_index = (self.voting_player_index + 1) % len(self.active_players)
                self.render_vote_screen()
                time.sleep(0.2)

            elif badge.input.get_button("BTN_B"):
                voted_player = self.active_players[self.voting_player_index]
                self.cast_vote(self.personal_player.name, voted_player.name)
                self.is_voting = False
                self.render_screen()
                time.sleep(0.3)
        