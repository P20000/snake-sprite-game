"""
Unit tests for GameEngine state transitions, resets, and mechanics.
"""
import os
import unittest

# Ensure Pygame runs headless during unit testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from src.game_engine import GameEngine
from src.constants import STATE_MENU, STATE_PLAYING, STATE_SETTINGS, STATE_GAME_OVER

class TestGameEngine(unittest.TestCase):
    """Tests for game engine states and update cycles."""

    def setUp(self):
        self.engine = GameEngine(headless=True)

    def test_initial_state(self):
        """Engine should start in menu state."""
        self.assertEqual(self.engine.state, STATE_MENU)
        self.assertEqual(self.engine.score, 0)
        self.assertFalse(self.engine.paused)

    def test_start_game_and_reset(self):
        """Transitioning to playing should reset score and snake."""
        self.engine.handle_menu_action(STATE_PLAYING)
        self.assertEqual(self.engine.state, STATE_PLAYING)
        self.assertEqual(self.engine.score, 0)
        self.assertEqual(len(self.engine.snake.body), 3)

    def test_settings_toggles(self):
        """Settings toggles should cycle values properly."""
        initial_sound = self.engine.settings["sound"]
        self.engine.handle_menu_action("toggle_sound")
        self.assertNotEqual(self.engine.settings["sound"], initial_sound)

        initial_diff = self.engine.settings["difficulty"]
        self.engine.handle_menu_action("toggle_difficulty")
        self.assertNotEqual(self.engine.settings["difficulty"], initial_diff)

    def test_pause_and_resume_actions(self):
        """Pause toggle, resume, and return to menu from pause."""
        self.engine.state = STATE_PLAYING
        self.assertFalse(self.engine.paused)

        # Toggle pause
        self.engine.handle_menu_action("toggle_pause")
        self.assertTrue(self.engine.paused)

        # Resume action
        self.engine.handle_menu_action("resume")
        self.assertFalse(self.engine.paused)

        # Paused -> Return to Main Menu unpauses
        self.engine.handle_menu_action("toggle_pause")
        self.assertTrue(self.engine.paused)
        self.engine.handle_menu_action(STATE_MENU)
        self.assertEqual(self.engine.state, STATE_MENU)
        self.assertFalse(self.engine.paused)

    def test_game_over_trigger(self):
        """Triggering game over should update state and shake camera."""
        self.engine.state = STATE_PLAYING
        self.engine.trigger_game_over()
        self.assertEqual(self.engine.state, STATE_GAME_OVER)
        self.assertGreater(self.engine.screen_shake, 0)

    def test_speed_boost(self):
        """Holding speed button activates boost flag in engine."""
        self.engine.state = STATE_PLAYING
        self.engine.update_gameplay(is_speed_held=True)
        self.assertTrue(self.engine.is_boosted)

        self.engine.update_gameplay(is_speed_held=False)
        # Without speed key held and without auto-play, boost is False
        self.assertFalse(self.engine.is_boosted)

if __name__ == "__main__":
    unittest.main()
