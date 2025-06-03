import pygame
import numpy as np
import random
import collections

class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = "wall"
        self.color = (100, 100, 100)  # Gray
    
    def draw(self, screen, cell_size):
        rect = pygame.Rect(self.x * cell_size, self.y * cell_size, cell_size, cell_size)
        pygame.draw.rect(screen, self.color, rect)

class Hazard:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = "mine"
        self.color = (255, 0, 0)  # Red
        self.damage = 50
    
    def draw(self, screen, cell_size):
        center_x = self.x * cell_size + cell_size // 2
        center_y = self.y * cell_size + cell_size // 2
        radius = cell_size // 3
        pygame.draw.circle(screen, self.color, (center_x, center_y), radius)

class ResourceNode:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = "resource"
        self.color = (0, 255, 255)  # Cyan
        self.value = 20
        self.owner = None
    
    def draw(self, screen, cell_size):
        center_x = self.x * cell_size + cell_size // 2
        center_y = self.y * cell_size + cell_size // 2
        points = []
        for i in range(5):
            angle = i * 72
            x = center_x + cell_size // 3 * pygame.math.Vector2(1, 0).rotate(angle).x
            y = center_y + cell_size // 3 * pygame.math.Vector2(1, 0).rotate(angle).y
            points.append((x, y))
        pygame.draw.polygon(screen, self.color, points)

class LiveObstacle:
    def __init__(self, x, y, grid_width, grid_height):
        self.x = x
        self.y = y
        self.type = "live_obstacle"
        self.color = (255, 140, 0)  # Orange
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.q_table = collections.defaultdict(lambda: np.zeros(5))  # 5 actions: stay, up, down, left, right
        self.last_state = None
        self.last_action = None
        self.owner = None

    def get_state(self, player_unit):
        dx = player_unit.x - self.x
        dy = player_unit.y - self.y
        return (dx, dy)

    def choose_action(self, state, epsilon=0.3):  # More random
        if random.random() < epsilon:
            return random.randint(0, 4)
        return np.argmax(self.q_table[state])

    def move(self, player_unit, occupied_positions):
        state = self.get_state(player_unit)
        action = self.choose_action(state)
        dx, dy = 0, 0
        if action == 1 and self.y > 0:
            dy = -1
        elif action == 2 and self.y < self.grid_height - 1:
            dy = 1
        elif action == 3 and self.x > 0:
            dx = -1
        elif action == 4 and self.x < self.grid_width - 1:
            dx = 1
        new_x, new_y = self.x + dx, self.y + dy
        # Prevent stacking
        if (new_x, new_y) in occupied_positions:
            new_x, new_y = self.x, self.y  # Stay in place
        self.last_state = state
        self.last_action = action
        self.x, self.y = new_x, new_y
        return (self.x, self.y)

    def update_q(self, player_unit, reward, alpha=0.5, gamma=0.9):
        if self.last_state is None or self.last_action is None:
            return
        next_state = self.get_state(player_unit)
        best_next = np.max(self.q_table[next_state])
        old_value = self.q_table[self.last_state][self.last_action]
        self.q_table[self.last_state][self.last_action] = old_value + alpha * (reward + gamma * best_next - old_value)

    def draw(self, screen, cell_size):
        rect = pygame.Rect(self.x * cell_size, self.y * cell_size, cell_size, cell_size)
        pygame.draw.rect(screen, self.color, rect)

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cell_size = 50
        self.grid = np.full((height, width), None, dtype=object)  # [y, x]
        self.units = []
        self.obstacles = []
        self.hazards = []
        self.resources = []
        self.valid_moves = []
        self.live_obstacles = []
        
        # Initialize obstacles and hazards
        self.initialize_obstacles()
        self.initialize_hazards()
        self.initialize_resources()
        self.initialize_live_obstacles()
    
    def add_unit(self, unit):
        """Add a unit to the grid."""
        if 0 <= unit.x < self.width and 0 <= unit.y < self.height:
            if self.is_valid_position(unit.x, unit.y):
                self.grid[unit.y, unit.x] = unit
                self.units.append(unit)
                return True
        return False
    
    def initialize_obstacles(self):
        # Add some random walls/asteroids
        num_obstacles = 5
        for _ in range(num_obstacles):
            x = random.randint(2, self.width-3)
            y = random.randint(2, self.height-3)
            # Don't place obstacles near bases
            if abs(x - 0) + abs(y - 0) > 2 and abs(x - (self.width-1)) + abs(y - (self.height-1)) > 2:
                obstacle = Obstacle(x, y)
                self.obstacles.append(obstacle)
                self.grid[y, x] = obstacle
    
    def initialize_hazards(self):
        # Add some space mines
        num_hazards = 3
        for _ in range(num_hazards):
            x = random.randint(2, self.width-3)
            y = random.randint(2, self.height-3)
            # Don't place hazards near bases
            if abs(x - 0) + abs(y - 0) > 2 and abs(x - (self.width-1)) + abs(y - (self.height-1)) > 2:
                hazard = Hazard(x, y)
                self.hazards.append(hazard)
                self.grid[y, x] = hazard
    
    def initialize_resources(self):
        # Add resource nodes
        num_resources = 4
        for _ in range(num_resources):
            x = random.randint(2, self.width-3)
            y = random.randint(2, self.height-3)
            # Don't place resources near bases
            if abs(x - 0) + abs(y - 0) > 2 and abs(x - (self.width-1)) + abs(y - (self.height-1)) > 2:
                resource = ResourceNode(x, y)
                self.resources.append(resource)
                self.grid[y, x] = resource
    
    def initialize_live_obstacles(self):
        # Add 2 live obstacles
        for _ in range(2):
            while True:
                x = random.randint(2, self.width-3)
                y = random.randint(2, self.height-3)
                if self.grid[y, x] is None:
                    live_obs = LiveObstacle(x, y, self.width, self.height)
                    self.live_obstacles.append(live_obs)
                    self.grid[y, x] = live_obs
                    break
    
    def is_valid_position(self, x, y):
        """Check if a position is valid (empty or contains a resource)"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        cell_content = self.grid[y, x]
        return cell_content is None or isinstance(cell_content, ResourceNode)
    
    def calculate_valid_moves(self, unit):
        """Calculate valid moves for a unit based on its movement range."""
        self.valid_moves = []
        if not unit:
            return
            
        current_x, current_y = unit.x, unit.y
        movement_range = unit.movement_range
        
        # Check all possible positions within movement range
        for dx in range(-movement_range, movement_range + 1):
            for dy in range(-movement_range, movement_range + 1):
                # Skip the current position
                if dx == 0 and dy == 0:
                    continue
                    
                new_x, new_y = current_x + dx, current_y + dy
                
                # Check if the new position is within grid bounds
                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    # Check if the cell is empty or contains a resource
                    cell_content = self.grid[new_y, new_x]
                    if cell_content is None or isinstance(cell_content, ResourceNode):
                        # Calculate Manhattan distance
                        distance = abs(dx) + abs(dy)
                        if distance <= movement_range:
                            self.valid_moves.append((new_x, new_y))
        
        print(f"Valid moves for {unit.__class__.__name__} at ({current_x}, {current_y}): {self.valid_moves}")
    
    def move_unit(self, unit, new_x, new_y):
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            if self.is_valid_position(new_x, new_y):
                self.grid[unit.y, unit.x] = None
                unit.x = new_x
                unit.y = new_y
                self.grid[new_y, new_x] = unit
                self.valid_moves = []
                unit.has_moved = True
                
                # Check for hazards
                for hazard in self.hazards:
                    if hazard.x == new_x and hazard.y == new_y:
                        unit.health -= hazard.damage
                        print(f"Unit hit a mine! Health reduced to {unit.health}")
                        if unit.health <= 0:
                            print(f"{unit.__class__.__name__} was destroyed by a mine!")
                            self.remove_dead_units()
                
                # Check for resources
                for resource in self.resources:
                    if resource.x == new_x and resource.y == new_y:
                        resource.owner = unit.owner
                        print(f"{unit.owner} captured a resource node!")
                
                return True
        return False
    
    def get_unit_at(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x]
        return None
    
    def draw(self, screen):
        # Draw grid lines
        for x in range(self.width + 1):
            pygame.draw.line(screen, (50, 50, 50),
                           (x * self.cell_size, 0),
                           (x * self.cell_size, self.height * self.cell_size))
        for y in range(self.height + 1):
            pygame.draw.line(screen, (50, 50, 50),
                           (0, y * self.cell_size),
                           (self.width * self.cell_size, y * self.cell_size))
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(screen, self.cell_size)
        
        # Draw hazards
        for hazard in self.hazards:
            hazard.draw(screen, self.cell_size)
        
        # Draw resources
        for resource in self.resources:
            resource.draw(screen, self.cell_size)
        
        # Draw valid moves
        for x, y in self.valid_moves:
            rect = pygame.Rect(x * self.cell_size, y * self.cell_size,
                             self.cell_size, self.cell_size)
            highlight = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            highlight.fill((0, 255, 0, 100))
            screen.blit(highlight, rect)
            pygame.draw.rect(screen, (0, 255, 0), rect, 2)
        
        # Draw units
        for unit in self.units:
            unit.draw(screen, self.cell_size)
        
        # Draw live obstacles
        for obs in self.live_obstacles:
            obs.draw(screen, self.cell_size)
    
    def get_units_in_range(self, x, y, range):
        """Get all units within a certain range of a position."""
        units = []
        for unit in self.units:
            distance = abs(unit.x - x) + abs(unit.y - y)
            if distance <= range:
                units.append(unit)
        return units
    
    def remove_dead_units(self):
        """Remove dead units from the grid and units list."""
        dead_units = [unit for unit in self.units if unit.is_dead()]
        for unit in dead_units:
            self.grid[unit.y, unit.x] = None
            self.units.remove(unit)
        return len(dead_units) > 0  # Return True if any units were removed
    
    def handle_combat(self, attacker, target_x, target_y):
        """Handle combat between units."""
        target = self.get_unit_at(target_x, target_y)
        # Only allow combat if both attacker and target are units (not obstacles)
        from game.units import Unit
        if not (isinstance(attacker, Unit) and isinstance(target, Unit)):
            return False
        if target and attacker.can_attack(target):
            if attacker.attack(target):
                # Check if target died
                if target.is_dead():
                    self.remove_dead_units()
                return True
        return False
    
    def use_ability(self, unit, ability_name, target_x=None, target_y=None):
        """Use a unit's special ability."""
        if ability_name not in unit.abilities:
            return False
            
        if ability_name == "Quick Strike":
            # Corvette can attack twice
            unit.has_attacked = False
            return True
            
        elif ability_name == "Repair":
            # Mech can heal adjacent friendly units
            if target_x is not None and target_y is not None:
                target = self.get_unit_at(target_x, target_y)
                if target and target.owner == unit.owner:
                    target.health = min(target.max_health, target.health + 20)
                    return True
                    
        elif ability_name == "Area Attack":
            # Dreadnought attacks all units in range
            units_in_range = self.get_units_in_range(unit.x, unit.y, unit.attack_range)
            for target in units_in_range:
                if target.owner != unit.owner:
                    unit.attack(target)
            self.remove_dead_units()
            return True
            
        elif ability_name == "Scout":
            # Drone reveals enemy units in a larger range
            # This is handled in the UI by showing enemy units
            return True
            
        return False

    def move_live_obstacles(self, player_unit):
        occupied = set((obs.x, obs.y) for obs in self.live_obstacles)
        for obs in self.live_obstacles:
            old_x, old_y = obs.x, obs.y
            self.grid[old_y, old_x] = None
            new_x, new_y = obs.move(player_unit, occupied)
            occupied.add((new_x, new_y))
            # Less reward for blocking, penalty for crowding
            reward = 0
            if new_x == player_unit.x and new_y == player_unit.y:
                reward = 2  # Lower reward for blocking
            elif abs(new_x - player_unit.x) + abs(new_y - player_unit.y) == 1:
                reward = -2  # Penalty for crowding
            else:
                reward = -1  # Small penalty for not blocking
            obs.update_q(player_unit, reward)
            self.grid[new_y, new_x] = obs 