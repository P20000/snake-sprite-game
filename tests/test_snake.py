"""
Unit tests for the Snake entity and movement logic.
"""
import unittest
import pygame
from src.snake import Snake
from src.constants import GRID_WIDTH, GRID_HEIGHT

class TestSnake(unittest.TestCase):
    """Tests for snake motion, directional queues, and collisions."""

    def setUp(self):
        self.snake = Snake(start_x=10, start_y=10)

    def test_initialization(self):
        """Verify initial snake length, direction, and position."""
        self.assertEqual(len(self.snake.body), 3)
        self.assertEqual(self.snake.head, [10, 10])
        self.assertEqual(self.snake.dx, 1)
        self.assertEqual(self.snake.dy, 0)

    def test_single_step_forward(self):
        """Verify snake moves 1 tile in heading direction."""
        alive, head = self.snake.step()
        self.assertTrue(alive)
        self.assertEqual(head, [11, 10])
        self.assertEqual(len(self.snake.body), 3)
        self.assertEqual(self.snake.body[0], [9, 10])

    def test_turn_queue_and_reversal_prevention(self):
        """Verify rapid turns queue properly and 180 reversals are rejected."""
        # Moving right (+1, 0), trying to move left (-1, 0) should be ignored
        self.snake.queue_direction(-1, 0)
        self.assertEqual(len(self.snake.input_queue), 0)

        # Turning UP (0, -1) should be accepted
        self.snake.queue_direction(0, -1)
        self.assertEqual(len(self.snake.input_queue), 1)

        # Queuing next turn LEFT (-1, 0) after UP should be accepted
        self.snake.queue_direction(-1, 0)
        self.assertEqual(len(self.snake.input_queue), 2)

        # Step 1 -> Should turn UP
        alive, head = self.snake.step()
        self.assertTrue(alive)
        self.assertEqual(head, [10, 9])

        # Step 2 -> Should turn LEFT
        alive, head = self.snake.step()
        self.assertTrue(alive)
        self.assertEqual(head, [9, 9])

    def test_key_handling(self):
        """Verify WASD and Arrow key mappings."""
        self.snake.handle_key_event(pygame.K_UP)
        self.assertEqual(self.snake.input_queue[-1], (0, -1))

        self.snake.handle_key_event(pygame.K_a)
        self.assertEqual(self.snake.input_queue[-1], (-1, 0))

    def test_growth(self):
        """Verify snake grows by specified segments."""
        self.snake.grow(2)
        initial_length = self.snake.length
        
        self.snake.step()
        self.assertEqual(self.snake.length, initial_length + 1)
        
        self.snake.step()
        self.assertEqual(self.snake.length, initial_length + 2)
        
        self.snake.step()
        self.assertEqual(self.snake.length, initial_length + 2)

    def test_wall_collision_without_wrap(self):
        """Verify death on grid boundary hit when wall wrap is disabled."""
        edge_snake = Snake(start_x=GRID_WIDTH - 1, start_y=5)
        alive, head = edge_snake.step(wrap_walls=False)
        self.assertFalse(alive)
        self.assertEqual(head, [GRID_WIDTH, 5])

    def test_wall_wrap_mode(self):
        """Verify snake wraps to opposite edge when wrap_walls is enabled."""
        edge_snake = Snake(start_x=GRID_WIDTH - 1, start_y=5)
        alive, head = edge_snake.step(wrap_walls=True)
        self.assertTrue(alive)
        self.assertEqual(head, [0, 5])

    def test_self_collision(self):
        """Verify snake detects self-intersection."""
        # Create a longer snake
        snake = Snake(start_x=10, start_y=10)
        snake.grow(3)
        for _ in range(3):
            snake.step()

        # Execute loop: UP -> LEFT -> DOWN
        snake.queue_direction(0, -1)
        snake.step()
        snake.queue_direction(-1, 0)
        snake.step()
        snake.queue_direction(0, 1)
        alive, _ = snake.step()
        
        self.assertFalse(alive)

if __name__ == "__main__":
    unittest.main()
