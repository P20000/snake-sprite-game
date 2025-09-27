# 🐍 Snake Game with Sprites

A modern take on the classic Snake game built with **Python** and **Pygame**, featuring realistic sprite animations, smooth 60 FPS gameplay, and intuitive WASD controls.

## 🎮 Features

- ✅ Smooth 60 FPS game loop
- ✅ Realistic sprite-based textures for the snake
- ✅ Intelligent turning animations using rotated corner sprites
- ✅ WASD movement control
- ✅ Pause the game with `Spacebar`
- ✅ Apple pickups that grow the snake
- ✅ Collision detection with self and walls
- ✅ Optional developer "cheat" mode for testing

## 🖼️ Preview

![image alt](https://github.com/P20000/snake-sprite-game/blob/main/screenshot-game.png?raw=true)

## 🧠 Controls

| Key        | Action         |
|------------|----------------|
| `W`        | Move Up        |
| `A`        | Move Left      |
| `S`        | Move Down      |
| `D`        | Move Right     |
| `Spacebar` | Pause/Unpause  |

## 🚀 Getting Started

### Requirements
- Python 3.x
- Pygame

### Installation
1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/snake-sprite-game.git
   cd snake-sprite-game
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install pygame
   ```

4. Run the game:
   ```bash
   python snake_game.py
   ```

## 🔧 Cheat Mode (For Testing)

Uncomment the following line in `game_loop()` to disable collision:
```python
# if head in snake:  # Disable this check to cheat
```

## 📁 Assets

All sprites are loaded from a single sprite sheet (`snake-graphics.png`) and carefully extracted with coordinates. You can replace this sheet with your own artwork.

## 📄 License

This project is open-source and free to use under the MIT License.

---

Made with ❤️ using Python + Pygame
