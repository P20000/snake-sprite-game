"""
Food items (regular apples, golden power-up apples) and spawn mechanics.
"""
import random
import pygame
from src.constants import TILE_SIZE, COLOR_GOLD, COLOR_RED, GRID_WIDTH, GRID_HEIGHT

class Food:
    """Represents food items on the grid with optional golden apple timers."""

    def __init__(self, x=0, y=0, food_type="normal"):
        self.x = x
        self.y = y
        self.type = food_type
        self.points = 50 if food_type == "golden" else 10
        self.growth = 2 if food_type == "golden" else 1
        
        # Golden apple timer
        self.timer = 150 if food_type == "golden" else 0
        self.max_timer = self.timer

    @property
    def pos(self):
        """Returns tuple position (x, y)."""
        return (self.x, self.y)

    def is_expired(self):
        """Checks if a timed golden apple has run out of time."""
        return self.type == "golden" and self.timer <= 0

    def update(self):
        """Ticks the countdown timer for timed items."""
        if self.type == "golden" and self.timer > 0:
            self.timer -= 1

    @classmethod
    def spawn_new(cls, snake_body, grid_w=GRID_WIDTH, grid_h=GRID_HEIGHT, score=0):
        """
        Spawns a new food item in a free grid tile.
        Has a chance to spawn a golden apple if score >= 30.
        """
        snake_set = set(tuple(p) for p in snake_body)
        all_positions = [(x, y) for x in range(grid_w) for y in range(grid_h)]
        available = [p for p in all_positions if p not in snake_set]

        if not available:
            return cls(0, 0, "normal")

        fx, fy = random.choice(available)
        
        # 20% chance of golden apple if player has scored >= 30
        is_golden = (score >= 30) and (random.random() < 0.20)
        food_type = "golden" if is_golden else "normal"

        return cls(fx, fy, food_type)

    def draw(self, surface, sprites):
        """Draws the food sprite and timer bar for golden apples."""
        px = self.x * TILE_SIZE
        py = self.y * TILE_SIZE

        sprite_key = "golden_apple" if self.type == "golden" else "apple"
        sprite = sprites.get(sprite_key)
        
        if sprite:
            surface.blit(sprite, (px, py))
        else:
            color = COLOR_GOLD if self.type == "golden" else COLOR_RED
            pygame.draw.circle(surface, color, (px + TILE_SIZE // 2, py + TILE_SIZE // 2), TILE_SIZE // 2 - 2)

        # Draw a subtle countdown indicator for golden apples
        if self.type == "golden" and self.max_timer > 0:
            progress = self.timer / self.max_timer
            bar_w = int((TILE_SIZE - 2) * progress)
            pygame.draw.rect(surface, (50, 50, 50), (px + 1, py - 3, TILE_SIZE - 2, 2))
            pygame.draw.rect(surface, COLOR_GOLD, (px + 1, py - 3, bar_w, 2))
