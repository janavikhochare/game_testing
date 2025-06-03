import pygame

class Unit:
    def __init__(self, x, y, owner):
        self.x = x
        self.y = y
        self.owner = owner  # "player" or "ai"
        self.movement_range = 1
        self.attack_power = 1
        self.defense = 1
        self.health = 100
        self.max_health = 100
        self.attack_range = 1  # Range for attacking other units
        self.has_attacked = False  # Track if unit has attacked this turn
        self.has_moved = False    # Track if unit has moved this turn
        self.abilities = []       # List of special abilities
        # Base colors for player units
        self.colors = {
            "player": {
                "Corvette": (0, 255, 255),    # Cyan
                "Mech": (0, 255, 0),          # Green
                "Dreadnought": (255, 165, 0),  # Orange
                "Drone": (255, 255, 0)        # Yellow
            },
            "ai": {
                "Corvette": (255, 0, 255),    # Magenta
                "Mech": (255, 0, 0),          # Red
                "Dreadnought": (255, 69, 0),   # Red-Orange
                "Drone": (255, 140, 0)        # Dark Orange
            }
        }
        self.font = pygame.font.Font(None, 20)
    
    def draw(self, screen, cell_size, selected=False):
        """Draw the unit on the screen."""
        # Calculate position
        x = self.x * cell_size
        y = self.y * cell_size
        
        # Draw unit body (human-like shape)
        color = (0, 255, 0) if self.owner == "player" else (255, 0, 0)
        
        # Draw body (torso)
        body_rect = pygame.Rect(x + cell_size//4, y + cell_size//4, cell_size//2, cell_size//2)
        pygame.draw.rect(screen, color, body_rect)
        
        # Draw head
        head_radius = cell_size//6
        head_center = (x + cell_size//2, y + cell_size//4)
        pygame.draw.circle(screen, color, head_center, head_radius)
        
        # Draw arms
        arm_width = cell_size//8
        arm_height = cell_size//3
        # Left arm
        left_arm = pygame.Rect(x + cell_size//8, y + cell_size//3, arm_width, arm_height)
        pygame.draw.rect(screen, color, left_arm)
        # Right arm
        right_arm = pygame.Rect(x + cell_size - cell_size//8 - arm_width, y + cell_size//3, arm_width, arm_height)
        pygame.draw.rect(screen, color, right_arm)
        
        # Draw legs
        leg_width = cell_size//8
        leg_height = cell_size//3
        # Left leg
        left_leg = pygame.Rect(x + cell_size//3, y + cell_size//2 + cell_size//4, leg_width, leg_height)
        pygame.draw.rect(screen, color, left_leg)
        # Right leg
        right_leg = pygame.Rect(x + cell_size - cell_size//3 - leg_width, y + cell_size//2 + cell_size//4, leg_width, leg_height)
        pygame.draw.rect(screen, color, right_leg)
        
        # Draw health bar
        health_width = cell_size
        health_height = 5
        health_x = x
        health_y = y - 10
        health_rect = pygame.Rect(health_x, health_y, health_width, health_height)
        pygame.draw.rect(screen, (255, 0, 0), health_rect)  # Red background
        current_health_width = int(health_width * (self.health / self.max_health))
        current_health_rect = pygame.Rect(health_x, health_y, current_health_width, health_height)
        pygame.draw.rect(screen, (0, 255, 0), current_health_rect)  # Green health
        
        # Draw selection indicator
        if selected:
            selection_rect = pygame.Rect(x, y, cell_size, cell_size)
            pygame.draw.rect(screen, (255, 255, 0), selection_rect, 2)  # Yellow border

    def can_attack(self, target):
        """Check if this unit can attack the target unit."""
        if self.has_attacked:
            return False
        if target.owner == self.owner:
            return False
        # Check if target is within attack range
        distance = abs(self.x - target.x) + abs(self.y - target.y)
        return distance <= self.attack_range
    
    def attack(self, target):
        """Attack another unit."""
        if not self.can_attack(target):
            return False
        
        # Calculate damage
        damage = max(1, self.attack_power - target.defense)
        target.health = max(0, target.health - damage)
        self.has_attacked = True
        return True
    
    def reset_turn(self):
        """Reset unit's turn-based flags."""
        self.has_attacked = False
        self.has_moved = False
    
    def is_dead(self):
        """Check if unit is dead."""
        return self.health <= 0

class Corvette(Unit):
    def __init__(self, x, y, owner):
        super().__init__(x, y, owner)
        self.movement_range = 3
        self.attack_power = 2
        self.defense = 1
        self.health = 60
        self.max_health = 60
        self.attack_range = 1
        self.abilities = ["Quick Strike"]  # Can attack twice in one turn

class Mech(Unit):
    def __init__(self, x, y, owner):
        super().__init__(x, y, owner)
        self.movement_range = 2
        self.attack_power = 3
        self.defense = 2
        self.health = 100
        self.max_health = 100
        self.attack_range = 1
        self.abilities = ["Repair"]  # Can heal adjacent friendly units

class Dreadnought(Unit):
    def __init__(self, x, y, owner):
        super().__init__(x, y, owner)
        self.movement_range = 1
        self.attack_power = 5
        self.defense = 4
        self.health = 150
        self.max_health = 150
        self.attack_range = 2
        self.abilities = ["Area Attack"]  # Can attack all units in range

class Drone(Unit):
    def __init__(self, x, y, owner):
        super().__init__(x, y, owner)
        self.movement_range = 2
        self.attack_power = 1
        self.defense = 1
        self.health = 40
        self.max_health = 40
        self.attack_range = 1
        self.abilities = ["Scout"]  # Can see enemy units from further away
        self.resource_gathering = 2 