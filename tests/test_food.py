"""
Unit tests for Food items and spawn logic.
"""
import unittest
from src.food import Food
from src.constants import GRID_WIDTH, GRID_HEIGHT

class TestFood(unittest.TestCase):
    """Tests for food generation, expiration, and collision."""

    def test_spawn_never_on_snake(self):
        """Ensure newly spawned food is never on the snake body."""
        snake_body = [[x, 5] for x in range(20)]
        for _ in range(50):
            food = Food.spawn_new(snake_body, grid_w=GRID_WIDTH, grid_h=GRID_HEIGHT)
            self.assertNotIn([food.x, food.y], snake_body)
            self.assertTrue(0 <= food.x < GRID_WIDTH)
            self.assertTrue(0 <= food.y < GRID_HEIGHT)

    def test_golden_apple_timer_expiration(self):
        """Ensure golden apple counts down and flags expiration."""
        golden_food = Food(5, 5, "golden")
        self.assertEqual(golden_food.points, 50)
        self.assertFalse(golden_food.is_expired())
        
        # Countdown to 0
        for _ in range(golden_food.max_timer):
            golden_food.update()
            
        self.assertTrue(golden_food.is_expired())

    def test_normal_apple_no_expiration(self):
        """Normal apple should never expire."""
        normal_food = Food(5, 5, "normal")
        self.assertEqual(normal_food.points, 10)
        for _ in range(300):
            normal_food.update()
        self.assertFalse(normal_food.is_expired())

if __name__ == "__main__":
    unittest.main()
