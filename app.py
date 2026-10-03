"""
Snake Game with Sprites - Main Entry Point
"""
import sys
import os

# Ensure project root is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game_engine import GameEngine

def main():
    """Initializes and runs the Snake Game."""
    engine = GameEngine()
    engine.run()

if __name__ == "__main__":
    main()