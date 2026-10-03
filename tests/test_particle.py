"""
Unit tests for Particle and ParticleSystem.
"""
import unittest
from src.particle import Particle, ParticleSystem
from src.constants import COLOR_RED

class TestParticles(unittest.TestCase):
    """Tests for particle lifecycles and burst systems."""

    def test_single_particle_lifecycle(self):
        """Particle should decay and eventually expire."""
        p = Particle(100, 100, 2, 2, COLOR_RED, radius=3, max_life=5)
        self.assertTrue(p.update())
        self.assertEqual(p.life, 4)
        for _ in range(4):
            p.update()
        self.assertFalse(p.update())

    def test_particle_system_bursts(self):
        """ParticleSystem should add and clean up dead particles."""
        ps = ParticleSystem()
        self.assertEqual(len(ps.particles), 0)

        ps.add_apple_burst(50, 50, is_golden=False)
        self.assertTrue(len(ps.particles) > 0)

        # Update until all die
        for _ in range(50):
            ps.update()
        self.assertEqual(len(ps.particles), 0)

    def test_speed_trail(self):
        """ParticleSystem should spawn speed boost trail particles without errors."""
        ps = ParticleSystem()
        ps.add_speed_trail(50, 50)
        self.assertEqual(len(ps.particles), 1)
        ps.update()

if __name__ == "__main__":
    unittest.main()
