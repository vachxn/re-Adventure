# re-Adventure - Quick Start Guide

## Installation

1. **Install PyQt6** (if not already installed):
```bash
pip install PyQt6==6.10.0
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Running the Game

### Windows
Double-click `run.bat` or run:
```cmd
cd adventure_modern
python main.py
```

### Linux/Mac
```bash
cd re-Adventure
chmod +x run.sh
./run.sh
```

Or:
```bash
cd re-Adventure
python3 main.py
```

## How to Play

### Controls
- **WASD** or **Arrow Keys**: Move your character
- **Space** or **E**: Attack (requires sword)
- **ESC**: Quit game

### Objective
Find the **Enchanted Chalice** in the Throne Room to win!

### Tips
1. **Get the Sword First**: It's in the Castle Entrance room. You need it to fight dragons.
2. **Explore Carefully**: Dragons will chase you when you get close.
3. **Watch Your Health**: You have 3 hearts. Touching enemies damages you.
4. **Room Exits**: Look for colored rectangles at room edges - these are exits.
5. **Collect Items**: Walk over items to pick them up automatically.

### The Path to Victory
1. Start in **Castle Entrance** - grab the sword
2. Go north to **Great Hall** - get the gold key
3. Go north to **Throne Room** - defeat the dragon and grab the chalice!

### Explore More
- Visit the **Armory** (east) to find a silver key
- Explore the **Forest** area through the Training Grounds
- Brave the **Dungeon** area through the Courtyard
- Navigate the **Labyrinth** (beware of bats!)

## Game Features

✅ **15 interconnected rooms** to explore  
✅ **Multiple enemy types**: Red/Yellow/Green Dragons, Bats  
✅ **Inventory system**: Sword, Keys, Quest Items  
✅ **Health system**: 3 hearts  
✅ **Simple combat**: Attack with sword (space/E)  
✅ **Enemy AI**: Dragons chase you when close  
✅ **Win condition**: Find the Enchanted Chalice  

## Troubleshooting

### "No module named 'PyQt6'"
Install PyQt6:
```bash
pip install PyQt6==6.10.0
```

### Game window doesn't appear
Make sure you're in the `re-Adventure` directory when running.

### Game runs but shows errors
Check that all files are present in the correct structure (see README.md).

## Game World Map

```
            [Throne Room]
                  |
  [Library] - [Great Hall] - 
                  |
            [Castle Entrance] - [Armory] - [Training Grounds]
                  |                              |
            [Courtyard]                    [Forest Edge]
                  |                              |
         [Dungeon Entrance]                [Deep Forest] - [Dark Cave]
                  |
          [Dungeon Depths] - [Labyrinth Start]
                                   |     |
                          [Labyrinth N] [Labyrinth S]
```

## Have Fun!

**re-Adventure** - A modern tribute to the classic Atari Adventure. Enjoy exploring!

