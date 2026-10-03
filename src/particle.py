"""
Particle effects system for juice, bite sparks, and explosion animations.
"""
import random
import pygame
from src.constants import COLOR_GOLD, COLOR_RED, COLOR_GREEN, COLOR_WHITE

class Particle:
    """Represents an individual visual particle."""

    def __init__(self, x, y, vx, vy, color, radius=3, max_life=20):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.radius = radius
        self.life = max_life
        self.max_life = max_life

    def update(self):
        """Updates particle position, drag, and lifetime. Returns False when dead."""
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94  # Slight drag
        self.vy *= 0.94
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        """Draws the particle with fading radius and alpha."""
        if self.life <= 0:
            return
        fade_ratio = self.life / self.max_life
        current_radius = max(1, int(self.radius * fade_ratio))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), current_radius)


class ParticleSystem:
    """Manages active particles and generation presets."""

    def __init__(self):
        self.particles = []

    def clear(self):
        """Clears all active particles."""
        self.particles.clear()

    def add_apple_burst(self, screen_x, screen_y, is_golden=False):
        """Spawns a burst of particles when eating an apple."""
        base_color = COLOR_GOLD if is_golden else COLOR_RED
        count = 16 if is_golden else 10
        
        for _ in range(count):
            angle_speed = random.uniform(1.0, 4.0)
            vx = random.uniform(-1, 1) * angle_speed
            vy = random.uniform(-1, 1) * angle_speed
            
            # Slight color variation
            r = min(255, max(0, base_color[0] + random.randint(-20, 20)))
            g = min(255, max(0, base_color[1] + random.randint(-20, 20)))
            b = min(255, max(0, base_color[2] + random.randint(-20, 20)))
            
            self.particles.append(
                Particle(screen_x, screen_y, vx, vy, (r, g, b), radius=random.randint(2, 4), max_life=random.randint(15, 25))
            )

    def add_death_burst(self, screen_x, screen_y):
        """Spawns an explosive burst of snake fragments on collision."""
        for _ in range(25):
            angle_speed = random.uniform(1.5, 5.5)
            vx = random.uniform(-1, 1) * angle_speed
            vy = random.uniform(-1, 1) * angle_speed
            
            r = min(255, max(0, COLOR_GREEN[0] + random.randint(-30, 30)))
            g = min(255, max(0, COLOR_GREEN[1] + random.randint(-30, 30)))
            b = min(255, max(0, COLOR_GREEN[2] + random.randint(-30, 30)))
            
            self.particles.append(
                Particle(screen_x, screen_y, vx, vy, (r, g, b), radius=random.randint(3, 5), max_life=random.randint(20, 35))
            )

    def add_speed_trail(self, screen_x, screen_y):
        """Spawns trailing sparks when speed boost is engaged."""
        vx = random.uniform(-0.6, 0.6)
        vy = random.uniform(-0.6, 0.6)
        color = random.choice([COLOR_GOLD, (115, 235, 165), COLOR_WHITE])
        self.particles.append(
            Particle(screen_x, screen_y, vx, vy, color, radius=random.randint(1, 2), max_life=random.randint(6, 12))
        )

    def update(self):
        """Updates all living particles."""
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        """Renders all active particles."""
        for particle in self.particles:
            particle.draw(surface)
