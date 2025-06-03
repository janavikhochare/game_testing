import pygame
import sys
import random
import collections
import numpy as np
import time
from game.grid import Grid, ResourceNode
from game.units import Unit, Corvette, Mech, Dreadnought, Drone
from game.game_state import GameState
from game.ui import UI

class QLearningAI:
    def __init__(self, grid_size):
        self.q_table = collections.defaultdict(lambda: np.zeros(5))  # 5 actions: stay, up, down, left, right
        self.grid_size = grid_size
        self.last_state = None
        self.last_action = None
        self.learning_rate = 0.8  # Increased learning rate
        self.discount_factor = 0.95  # Increased discount factor
        self.exploration_rate = 0.2  # Balanced exploration rate
        self.memory = []  # Store recent experiences for better learning

    def get_state(self, unit, player_base):
        dx = player_base[0] - unit.x
        dy = player_base[1] - unit.y
        # Normalize distances to make state space smaller
        dx = max(min(dx, 5), -5)
        dy = max(min(dy, 5), -5)
        return (dx, dy)

    def choose_action(self, state, epsilon=None):
        if epsilon is None:
            epsilon = self.exploration_rate
            
        if np.random.rand() < epsilon:
            # Weighted random choice based on Q-values
            q_values = self.q_table[state]
            exp_q = np.exp(q_values - np.max(q_values))  # Subtract max for numerical stability
            probs = exp_q / np.sum(exp_q)
            action = np.random.choice(5, p=probs)
            print(f"[AI RL] Weighted random action {action} for state {state}")
            return action
            
        # Get Q-values for current state
        q_values = self.q_table[state]
        
        # Add small random noise to break ties
        noise = np.random.randn(5) * 0.1
        q_values = q_values + noise
        
        action = np.argmax(q_values)
        print(f"[AI RL] Greedy action {action} for state {state} with Q-values {self.q_table[state]}")
        return action

    def move(self, unit, player_base, grid):
        state = self.get_state(unit, player_base)
        action = self.choose_action(state)
        
        # Calculate potential moves
        moves = [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)]  # stay, up, down, left, right
        dx, dy = moves[action]
        
        new_x, new_y = unit.x + dx, unit.y + dy
        
        # Check if move is valid
        if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
            if grid.is_valid_position(new_x, new_y):
                print(f"[AI RL] Moving from ({unit.x}, {unit.y}) to ({new_x}, {new_y})")
                unit.x, unit.y = new_x, new_y
            else:
                print(f"[AI RL] Tried invalid move from ({unit.x}, {unit.y}) to ({new_x}, {new_y})")
        else:
            print(f"[AI RL] Tried move outside grid from ({unit.x}, {unit.y}) to ({new_x}, {new_y})")
            
        self.last_state = state
        self.last_action = action
        return (unit.x, unit.y)

    def update_q(self, unit, player_base, reward, alpha=None, gamma=None):
        if self.last_state is None or self.last_action is None:
            return
            
        if alpha is None:
            alpha = self.learning_rate
        if gamma is None:
            gamma = self.discount_factor
            
        next_state = self.get_state(unit, player_base)
        best_next = np.max(self.q_table[next_state])
        old_value = self.q_table[self.last_state][self.last_action]
        
        # Q-learning update with higher learning rate
        new_value = old_value + alpha * (reward + gamma * best_next - old_value)
        self.q_table[self.last_state][self.last_action] = new_value
        
        # Store experience in memory
        self.memory.append((self.last_state, self.last_action, reward, next_state))
        
        # Update Q-values based on recent experiences
        if len(self.memory) > 10:
            for exp_state, exp_action, exp_reward, exp_next_state in self.memory[-10:]:
                exp_best_next = np.max(self.q_table[exp_next_state])
                exp_old_value = self.q_table[exp_state][exp_action]
                self.q_table[exp_state][exp_action] = exp_old_value + alpha * (exp_reward + gamma * exp_best_next - exp_old_value)
        
        print(f"[AI RL] Updated Q for state {self.last_state}, action {self.last_action}: {new_value}")

class NebulaDominion:
    def __init__(self):
        pygame.init()
        self.grid_size = 10
        self.cell_size = 50
        self.sidebar_width = 250
        self.bottom_height = 100
        
        self.screen_width = self.grid_size * self.cell_size + self.sidebar_width
        self.screen_height = self.grid_size * self.cell_size + self.bottom_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Nebula Dominion")
        
        self.clock = pygame.time.Clock()
        self.grid = Grid(self.grid_size, self.grid_size)
        self.game_state = GameState(self.grid)
        self.ui = UI(self.screen, self.grid, self.game_state)
        
        # Base locations
        self.player_base = (0, 0)
        self.ai_base = (self.grid_size - 1, self.grid_size - 1)
        
        # Initialize some units for testing
        self.initialize_test_units()
        self.game_over = False
        self.winner = None
        self.live_obstacles_moved = False
        
        self.ai_rl = QLearningAI(self.grid_size)
    
    def initialize_test_units(self):
        # Player unit - placed near player base (0,0)
        player_unit = Corvette(1, 1, "player")
        if self.grid.add_unit(player_unit):
            print(f"Added player unit at (1, 1)")
        
        # AI unit - placed near AI base (9,9)
        ai_unit = Corvette(8, 8, "ai")
        if self.grid.add_unit(ai_unit):
            print(f"Added AI unit at (8, 8)")
        
        # Select player's unit at start
        self.game_state.select_unit(player_unit)
        self.grid.calculate_valid_moves(player_unit)
    
    def ai_turn(self):
        """AI's turn logic with RL"""
        ai_units = [unit for unit in self.grid.units if unit.owner == "ai"]
        player_units = [unit for unit in self.grid.units if unit.owner == "player"]
        
        # AI gets 2 moves per turn
        for move in range(2):
            print(f"\nAI Move {move + 1}/2:")
            for unit in ai_units:
                # RL move
                old_x, old_y = unit.x, unit.y
                old_distance = abs(unit.x - self.player_base[0]) + abs(unit.y - self.player_base[1])
                
                # Try to attack first if possible
                attacked = False
                for player_unit in player_units:
                    if unit.can_attack(player_unit):
                        if self.grid.handle_combat(unit, player_unit.x, player_unit.y):
                            print(f"AI attacked player's {player_unit.__class__.__name__}!")
                            self.ai_rl.update_q(unit, self.player_base, 15)  # Higher reward for attacking
                            attacked = True
                            break
                
                if not attacked:
                    # Move if didn't attack
                    self.ai_rl.move(unit, self.player_base, self.grid)
                    new_distance = abs(unit.x - self.player_base[0]) + abs(unit.y - self.player_base[1])
                    
                    # Calculate reward based on movement
                    reward = 0
                    if new_distance < old_distance:
                        reward += 4  # Higher reward for getting closer
                    elif new_distance > old_distance:
                        reward -= 3  # Higher penalty for moving away
                    else:
                        reward -= 1  # Penalty for not moving
                    
                    # Additional rewards
                    if isinstance(self.grid.grid[unit.y, unit.x], ResourceNode):
                        reward += 8  # Higher reward for capturing resource nodes
                    
                    # Reward for being in a good position (near player but not too close)
                    if 2 <= new_distance <= 4:
                        reward += 3
                    
                    # Penalty for being too close to player (vulnerable position)
                    if new_distance <= 1:
                        reward -= 2
                    
                    self.ai_rl.update_q(unit, self.player_base, reward)
                
                time.sleep(0.3)  # Reduced delay for smoother gameplay
        
        self.game_state.next_turn()
        print("AI turn ended. Player's turn.")
    
    def check_win_condition(self):
        # Player wins if any player unit reaches AI base
        for unit in self.grid.units:
            if unit.owner == "player" and (unit.x, unit.y) == self.ai_base:
                self.game_over = True
                self.winner = "Player"
                return
            if unit.owner == "ai" and (unit.x, unit.y) == self.player_base:
                self.game_over = True
                self.winner = "AI"
                return
    
    def draw_bases(self):
        # Draw player base
        base_size = self.cell_size
        player_rect = pygame.Rect(
            self.player_base[0] * self.cell_size, self.player_base[1] * self.cell_size, base_size, base_size)
        ai_rect = pygame.Rect(
            self.ai_base[0] * self.cell_size, self.ai_base[1] * self.cell_size, base_size, base_size)
        pygame.draw.rect(self.screen, (0, 0, 255), player_rect, 4)  # Blue border
        pygame.draw.rect(self.screen, (255, 0, 0), ai_rect, 4)      # Red border
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if not self.game_over:
                    self.ui.handle_event(event)
                    self.live_obstacles_moved = False  # Reset flag when player acts
            
            # AI turn
            if not self.game_over and self.game_state.current_player == "ai":
                print("\nAI's turn starting...")
                self.ai_turn()
                # Check win condition after AI moves
                self.check_win_condition()
                print("AI's turn ended.\n")
                self.live_obstacles_moved = False  # Reset flag after AI acts
            
            # Move live obstacles only once per full turn
            if not self.game_over and not self.live_obstacles_moved:
                player_units = [u for u in self.grid.units if u.owner == "player"]
                if player_units:
                    self.grid.move_live_obstacles(player_units[0])
                    self.live_obstacles_moved = True
            
            # Draw everything
            self.screen.fill((0, 0, 0))  # Black background
            self.grid.draw(self.screen)
            self.draw_bases()
            self.ui.draw()
            
            # Draw win message
            if self.game_over:
                font = pygame.font.Font(None, 60)
                text = f"{self.winner} wins!"
                text_surface = font.render(text, True, (255, 255, 0))
                rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                self.screen.blit(text_surface, rect)
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = NebulaDominion()
    game.run() 