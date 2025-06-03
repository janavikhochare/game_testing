class GameState:
    def __init__(self, grid):
        self.grid = grid
        self.current_turn = 1
        self.current_player = "player"  # "player" or "ai"
        self.player_resources = 100
        self.ai_resources = 100
        self.selected_unit = None
        self.game_over = False
        self.winner = None
        print(f"Game started - Turn {self.current_turn}: {self.current_player}'s turn")
    
    def update(self):
        # Update game state logic here
        pass
    
    def next_turn(self):
        self.current_turn += 1
        self.current_player = "ai" if self.current_player == "player" else "player"
        self.selected_unit = None
        print(f"Turn {self.current_turn}: {self.current_player}'s turn")
        
        # Add resources at the start of each turn
        if self.current_player == "player":
            self.player_resources += 10
            # Add resources from captured nodes
            for resource in self.grid.resources:
                if resource.owner == "player":
                    self.player_resources += resource.value
                    print(f"Player collected {resource.value} resources from a node")
            # Auto-select player's unit at the start of player's turn
            player_units = [unit for unit in self.grid.units if unit.owner == "player"]
            if player_units:
                self.select_unit(player_units[0])
                self.grid.calculate_valid_moves(player_units[0])
        else:
            self.ai_resources += 10
            # Add resources from captured nodes
            for resource in self.grid.resources:
                if resource.owner == "ai":
                    self.ai_resources += resource.value
                    print(f"AI collected {resource.value} resources from a node")
    
    def select_unit(self, unit):
        if unit and unit.owner == self.current_player:
            self.selected_unit = unit
            print(f"Selected {unit.__class__.__name__} for {self.current_player}")
            # Reset valid moves when selecting a new unit
            self.grid.valid_moves = []
            return True
        return False
    
    def can_afford_unit(self, unit_type, is_player=True):
        costs = {
            "Corvette": 30,
            "Mech": 50,
            "Dreadnought": 100,
            "Drone": 20
        }
        cost = costs.get(unit_type, 0)
        return (self.player_resources >= cost if is_player else self.ai_resources >= cost)
    
    def spend_resources(self, amount, is_player=True):
        if is_player:
            if self.player_resources >= amount:
                self.player_resources -= amount
                return True
        else:
            if self.ai_resources >= amount:
                self.ai_resources -= amount
                return True
        return False 