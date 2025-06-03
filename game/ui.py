import pygame

class UI:
    def __init__(self, screen, grid, game_state):
        self.screen = screen
        self.grid = grid
        self.game_state = game_state
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.selected_cell = None
        
        # Calculate UI regions
        self.grid_width = grid.width * grid.cell_size
        self.grid_height = grid.height * grid.cell_size
        self.sidebar_width = 250  # Width for the right sidebar
        self.bottom_height = 100  # Height for the bottom info bar
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            grid_x = x // self.grid.cell_size
            grid_y = y // self.grid.cell_size
            
            # Check if click is within grid
            if 0 <= grid_x < self.grid.width and 0 <= grid_y < self.grid.height:
                clicked_unit = self.grid.get_unit_at(grid_x, grid_y)
                
                # If a unit is selected
                if self.game_state.selected_unit:
                    unit = self.game_state.selected_unit
                    # Check if unit has already moved and attacked
                    if unit.has_moved and unit.has_attacked:
                        print("This unit has already moved and attacked this turn! Deselecting.")
                        self.grid.valid_moves = []
                        self.game_state.selected_unit = None
                        return
                        
                    # Try to move the selected unit
                    if (grid_x, grid_y) in self.grid.valid_moves and not unit.has_moved:
                        if self.grid.move_unit(self.game_state.selected_unit, grid_x, grid_y):
                            print(f"Moved {unit.__class__.__name__} to ({grid_x}, {grid_y})")
                            # Only deselect if unit has now both moved and attacked
                            if unit.has_moved and unit.has_attacked:
                                print("Deselecting after move+attack.")
                                self.game_state.selected_unit = None
                                self.grid.valid_moves = []
                            else:
                                print("Unit can still act, recalculating valid moves.")
                                self.grid.calculate_valid_moves(unit)
                            return
                    
                    # Try to attack
                    elif clicked_unit and clicked_unit.owner != self.game_state.current_player and not unit.has_attacked:
                        if self.grid.handle_combat(self.game_state.selected_unit, grid_x, grid_y):
                            print(f"Attacked {clicked_unit.__class__.__name__}!")
                            # Only deselect if unit has now both moved and attacked
                            if unit.has_moved and unit.has_attacked:
                                print("Deselecting after attack+move.")
                                self.game_state.selected_unit = None
                                self.grid.valid_moves = []
                            else:
                                print("Unit can still act, recalculating valid moves.")
                                self.grid.calculate_valid_moves(unit)
                            return
                    
                    # Try to use ability
                    elif clicked_unit and clicked_unit.owner == self.game_state.current_player:
                        for ability in self.game_state.selected_unit.abilities:
                            if self.grid.use_ability(self.game_state.selected_unit, ability, grid_x, grid_y):
                                print(f"Used {ability} ability!")
                                break
                    # Always recalculate valid moves after any action if still selected
                    if self.game_state.selected_unit:
                        print("Recalculating valid moves after action.")
                        self.grid.calculate_valid_moves(self.game_state.selected_unit)
                
                # Select a unit
                elif clicked_unit and clicked_unit.owner == self.game_state.current_player:
                    # Don't allow selecting units that have already moved and attacked
                    if not (clicked_unit.has_moved and clicked_unit.has_attacked):
                        if self.game_state.select_unit(clicked_unit):
                            print(f"Selected {clicked_unit.__class__.__name__} at ({grid_x}, {grid_y})")
                            self.grid.calculate_valid_moves(clicked_unit)
                    else:
                        print("This unit has already moved and attacked this turn!")
                else:
                    # Deselect if clicking empty cell
                    print("Deselected unit.")
                    self.game_state.selected_unit = None
                    self.grid.valid_moves = []
            
            # Check if end turn button was clicked
            end_turn_rect = pygame.Rect(
                self.screen.get_width() - self.sidebar_width + 10,
                self.screen.get_height() - 40,
                100, 30
            )
            if end_turn_rect.collidepoint(x, y):
                if self.game_state.current_player == "player":
                    # Reset all units' turn flags
                    for unit in self.grid.units:
                        unit.reset_turn()
                    self.game_state.next_turn()
                    self.grid.valid_moves = []
                    self.game_state.selected_unit = None
                    print("Player ended turn. AI's turn now.")
    
    def draw(self):
        # Draw UI elements
        self.draw_resources()
        self.draw_turn_info()
        self.draw_selected_unit_info()
        self.draw_legend()
        self.draw_instructions()
        
        # Draw end turn button
        if self.game_state.current_player == "player":
            end_turn_rect = pygame.Rect(
                self.screen.get_width() - self.sidebar_width + 10,
                self.screen.get_height() - 40,
                100, 30
            )
            pygame.draw.rect(self.screen, (0, 255, 0), end_turn_rect)  # Green button
            text_surface = self.font.render("End Turn", True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=end_turn_rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Draw selection indicator
        if self.selected_cell:
            x, y = self.selected_cell
            rect = pygame.Rect(x * self.grid.cell_size, y * self.grid.cell_size,
                             self.grid.cell_size, self.grid.cell_size)
            pygame.draw.rect(self.screen, (255, 255, 0), rect, 3)  # Yellow border for selected unit
    
    def draw_resources(self):
        # Draw player resources
        player_text = f"Player Resources: {self.game_state.player_resources}"
        text_surface = self.font.render(player_text, True, (0, 255, 0))
        self.screen.blit(text_surface, (10, self.grid_height + 10))
        
        # Draw AI resources
        ai_text = f"AI Resources: {self.game_state.ai_resources}"
        text_surface = self.font.render(ai_text, True, (255, 0, 0))
        self.screen.blit(text_surface, (10, self.grid_height + 40))
    
    def draw_turn_info(self):
        turn_text = f"Turn: {self.game_state.current_turn} - {self.game_state.current_player.capitalize()}'s Turn"
        text_surface = self.font.render(turn_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.grid_width // 2, 20))
        self.screen.blit(text_surface, text_rect)
    
    def draw_selected_unit_info(self):
        if self.game_state.selected_unit:
            unit = self.game_state.selected_unit
            y_offset = 50
            
            # Draw unit type and health
            text = f"{unit.__class__.__name__} - Health: {unit.health}/{unit.max_health}"
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (self.screen.get_width() - self.sidebar_width + 10, y_offset))
            y_offset += 30
            
            # Draw stats
            stats = [
                f"Attack: {unit.attack_power}",
                f"Defense: {unit.defense}",
                f"Movement: {unit.movement_range}",
                f"Attack Range: {unit.attack_range}"
            ]
            for stat in stats:
                text_surface = self.font.render(stat, True, (255, 255, 255))
                self.screen.blit(text_surface, (self.screen.get_width() - self.sidebar_width + 10, y_offset))
                y_offset += 20
            
            # Draw turn status
            y_offset += 10
            status = []
            if unit.has_moved:
                status.append("Moved")
            if unit.has_attacked:
                status.append("Attacked")
            if status:
                text = f"Status: {', '.join(status)}"
                text_surface = self.font.render(text, True, (255, 200, 0))
                self.screen.blit(text_surface, (self.screen.get_width() - self.sidebar_width + 10, y_offset))
                y_offset += 30
            
            # Draw abilities
            if unit.abilities:
                y_offset += 10
                text_surface = self.font.render("Abilities:", True, (255, 255, 255))
                self.screen.blit(text_surface, (self.screen.get_width() - self.sidebar_width + 10, y_offset))
                y_offset += 20
                for ability in unit.abilities:
                    text_surface = self.font.render(f"- {ability}", True, (255, 255, 255))
                    self.screen.blit(text_surface, (self.screen.get_width() - self.sidebar_width + 20, y_offset))
                    y_offset += 20
    
    def draw_legend(self):
        legend_text = [
            "Unit Legend:",
            "▲ Corvette (Fast Scout)",
            "■ Mech (Balanced)",
            "⬡ Dreadnought (Heavy)",
            "● Drone (Resource)",
            "Player: Cyan/Green/Orange/Yellow",
            "AI: Magenta/Red/Red-Orange/Dark Orange",
            "",
            "Map Elements:",
            "■ Wall/Asteroid (Impassable)",
            "● Mine (50 Damage)",
            "⬡ Resource Node (20 Resources)"
        ]
        
        # Draw in the right sidebar below unit info
        for i, text in enumerate(legend_text):
            text_surface = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (self.grid_width + 10, 200 + i * 20))
    
    def draw_instructions(self):
        instructions = [
            "How to Play:",
            "1. Click on your unit to select it",
            "2. Green squares show valid moves",
            "3. Click a green square to move",
            "4. Click enemy unit to attack",
            "5. Click friendly unit to use ability",
            "6. End Turn when all units used",
            "7. Each unit can move AND attack once per turn",
            "",
            "Watch out for:",
            "- Gray walls block movement",
            "- Red mines deal 50 damage",
            "- Cyan resource nodes give 20 resources"
        ]
        
        # Draw instructions in the right sidebar
        for i, text in enumerate(instructions):
            text_surface = self.small_font.render(text, True, (200, 200, 200))
            self.screen.blit(text_surface, (self.grid_width + 10, 350 + i * 20)) 