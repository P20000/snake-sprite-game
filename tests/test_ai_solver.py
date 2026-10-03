"""
Unit tests for AISolver pathfinding and space safety heuristics.
"""
import unittest
from src.ai_solver import AISolver

class TestAISolver(unittest.TestCase):
    """Tests for BFS and trap prevention."""

    def test_straight_line_path(self):
        """AI should move directly towards food if path is open."""
        snake_body = [[5, 5], [6, 5], [7, 5]]
        food_pos = (10, 5)
        move = AISolver.get_next_move(snake_body, food_pos, 1, 0)
        self.assertEqual(move, (1, 0))

    def test_obstacle_avoidance(self):
        """AI should avoid immediate obstacles."""
        # Snake head at (5, 5), wall or body right ahead at (6, 5)
        snake_body = [[4, 6], [5, 6], [6, 6], [6, 5], [5, 5]]
        food_pos = (7, 5)
        move = AISolver.get_next_move(snake_body, food_pos, 0, -1)
        # Should not move into [6, 5] (body) or [5, 6] (body)
        self.assertIn(move, [(0, -1), (-1, 0)])

    def test_no_suicide_reverse(self):
        """AI should never command an exact 180-degree reversal."""
        snake_body = [[5, 5], [6, 5], [7, 5]]
        food_pos = (2, 5)
        move = AISolver.get_next_move(snake_body, food_pos, 1, 0)
        self.assertNotEqual(move, (-1, 0))

    def test_should_boost(self):
        """AI should identify safe open corridors for speed boost."""
        snake_body = [[5, 5], [6, 5], [7, 5]]
        food_pos = (15, 5)
        self.assertTrue(AISolver.should_boost(snake_body, food_pos, 1, 0))

if __name__ == "__main__":
    unittest.main()
