"""
Manages persistent high scores stored in a local JSON file.
"""
import json
import os
from src.constants import HIGH_SCORE_FILE

class HighScoreManager:
    """Handles high score loading, checking, updating, and saving."""

    def __init__(self, filepath=HIGH_SCORE_FILE):
        self.filepath = filepath
        self.scores = {"Easy": 0, "Medium": 0, "Hard": 0, "Insane": 0}
        self.load()

    def load(self):
        """Loads scores from the JSON file if available."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for k, v in data.items():
                            if k in self.scores and isinstance(v, int):
                                self.scores[k] = v
            except Exception as e:
                print(f"Failed to load high scores: {e}")

    def save(self):
        """Persists current high scores to JSON file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.scores, f, indent=2)
        except Exception as e:
            print(f"Failed to save high scores: {e}")

    def get_high_score(self, difficulty="Medium"):
        """Returns the high score for a specific difficulty level."""
        return self.scores.get(difficulty, 0)

    def update_score(self, score, difficulty="Medium"):
        """
        Updates the high score if the new score exceeds the previous record.
        Returns True if a new record was set, False otherwise.
        """
        current_best = self.get_high_score(difficulty)
        if score > current_best:
            self.scores[difficulty] = score
            self.save()
            return True
        return False
