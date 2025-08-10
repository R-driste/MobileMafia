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
        badge.display.nice_text(f"Role: {}", 0, 0, font=32, color=0)
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

        badge.display.nice_text("")

    def loop(self) -> None:
        pass

#for host to track people
class Player():
    def __init__(self, name: str):
        self.name = name
        self.role = "unassigned"
        self.alive = True
        self.id = 0
    def __repr__(self):
        return f"{self.name} ({self.role}) - {'Alive' if self.alive else 'Dead'}"
    def assign_role(self, role: str):
        self.role = role
    #kraken functions
    def kill(self, player):
        if self.role == "Kraken":
            player.alive = False
    
        