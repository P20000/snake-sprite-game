"""
Game constants, configuration settings, and color palettes.
"""

# Screen & Display
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TILE_SIZE = 16
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE   # 40 tiles
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE # 30 tiles
FPS = 60

# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_SETTINGS = 2
STATE_GAME_OVER = 3

# Difficulty Mapping (frames per movement step)
DIFFICULTY_MAP = {
    "Easy": 12,
    "Medium": 8,
    "Hard": 4,
    "Insane": 2,
}

# Color Palette (Modern Arcade Theme)
COLOR_BG_DARK = (20, 26, 38)
COLOR_BG_GRID = (30, 40, 58)
COLOR_WHITE = (245, 245, 250)
COLOR_YELLOW = (255, 215, 0)
COLOR_GREEN = (46, 204, 113)
COLOR_RED = (231, 76, 60)
COLOR_GOLD = (241, 196, 15)
COLOR_PURPLE = (155, 89, 182)
COLOR_GRAY = (120, 130, 145)
COLOR_CARD_BG = (28, 38, 55, 220)
COLOR_CARD_BORDER = (50, 70, 100)
COLOR_HOVER = (60, 90, 130)

# High score save path
HIGH_SCORE_FILE = "highscores.json"
