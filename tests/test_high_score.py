"""
Unit tests for HighScoreManager.
"""
import unittest
import os
from src.high_score import HighScoreManager

class TestHighScore(unittest.TestCase):
    """Tests for saving, loading, and record checking."""

    def setUp(self):
        self.test_file = "test_highscores_tmp.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.manager = HighScoreManager(filepath=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_update_high_score(self):
        """Ensure high scores update only when exceeded."""
        self.assertEqual(self.manager.get_high_score("Medium"), 0)
        
        # New record set
        is_record = self.manager.update_score(100, "Medium")
        self.assertTrue(is_record)
        self.assertEqual(self.manager.get_high_score("Medium"), 100)

        # Lower score does not overwrite
        is_record_2 = self.manager.update_score(50, "Medium")
        self.assertFalse(is_record_2)
        self.assertEqual(self.manager.get_high_score("Medium"), 100)

    def test_persistence_across_instances(self):
        """Ensure scores reload properly from disk."""
        self.manager.update_score(250, "Hard")
        
        # Create fresh manager loading same file
        new_manager = HighScoreManager(filepath=self.test_file)
        self.assertEqual(new_manager.get_high_score("Hard"), 250)
        self.assertEqual(new_manager.get_high_score("Easy"), 0)

if __name__ == "__main__":
    unittest.main()
