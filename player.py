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
    