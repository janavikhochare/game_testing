# Nebula Dominion

A 2D grid-based sci-fi strategy game where players command a fleet of various unit types in turn-based combat.

## Features

- 10x10 grid-based gameplay
- Four unique unit types:
  - Corvette: Fast scout ships with extended movement range
  - Mech: Balanced ground combat units
  - Dreadnought: Heavy combat units with high attack and defense
  - Drone: Resource gathering units
- Turn-based combat system
- Resource management
- Simple and intuitive UI

## Requirements

- Python 3.7+
- Pygame 2.5.2
- NumPy 1.24.3

## Installation

1. Clone this repository

2. Set up the virtual environment:

   **On macOS/Linux:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   **On Windows:**
   ```bash
   setup.bat
   ```

3. Activate the virtual environment:

   **On macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

   **On Windows:**
   ```bash
   venv\Scripts\activate
   ```

## How to Play

1. Make sure your virtual environment is activated, then run the game:
```bash
python main.py
```

2. Game Controls:
- Left-click to select a unit
- Left-click on an empty cell to move the selected unit
- Space bar to end your turn
- The game automatically switches between player and AI turns

3. Game Rules:
- Each unit has unique stats for movement, attack, and defense
- Resources are gained automatically each turn
- Units can only move to empty cells
- The game ends when one player's units are eliminated

## Development

The game is structured in a modular way, making it easy to add new features:
- `main.py`: Main game loop and initialization
- `game/grid.py`: Grid management and unit placement
- `game/units.py`: Unit classes and their behaviors
- `game/game_state.py`: Game state management
- `game/ui.py`: User interface and input handling 