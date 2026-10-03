"""
GameEngine coordinator uniting all subsystems, game states, and event handling.
"""
import random
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, FPS, COLOR_BG_DARK, COLOR_BG_GRID,
    STATE_MENU, STATE_PLAYING, STATE_SETTINGS, STATE_GAME_OVER, DIFFICULTY_MAP
)
from src.assets import AssetManager
from src.high_score import HighScoreManager
from src.particle import ParticleSystem
from src.menu import MenuManager
from src.snake import Snake
from src.food import Food
from src.ai_solver import AISolver

class GameEngine:
    """Core game coordinator managing state machines, rendering, and logic updates."""

    def __init__(self, headless=False):
        self.headless = headless
        if not pygame.get_init():
            pygame.init()

        self.screen = None if headless else pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        if not headless:
            pygame.display.set_caption("Snake Game Arcade")

        self.clock = pygame.time.Clock()
        self.assets = AssetManager()
        self.high_scores = HighScoreManager()
        self.particles = ParticleSystem()
        self.menus = MenuManager(self.assets)

        self.state = STATE_MENU
        self.paused = False
        self.score = 0
        self.is_new_record = False
        self.is_boosted = False
        self.move_counter = 0
        self.screen_shake = 0

        self.settings = {
            "difficulty": "Medium",
            "sound": True,
            "auto_play": False,
            "wrap_walls": False,
        }

        self.snake = None
        self.food = None
        self.reset_game()

    def reset_game(self):
        """Initializes game variables for a fresh match."""
        self.snake = Snake()
        self.food = Food.spawn_new(self.snake.body, score=0)
        self.score = 0
        self.is_new_record = False
        self.is_boosted = False
        self.move_counter = 0
        self.paused = False
        self.particles.clear()
        self.screen_shake = 0

    def trigger_game_over(self):
        """Transitions state to game over, creates burst, and checks high score."""
        self.state = STATE_GAME_OVER
        self.screen_shake = 8
        self.assets.play_sound("game_over", self.settings["sound"])
        
        # Spawn explosion at snake head
        head_px = self.snake.head[0] * TILE_SIZE + TILE_SIZE // 2
        head_py = self.snake.head[1] * TILE_SIZE + TILE_SIZE // 2
        self.particles.add_death_burst(head_px, head_py)

        # Check high score
        self.is_new_record = self.high_scores.update_score(self.score, self.settings["difficulty"])

    def update_gameplay(self, is_speed_held=False):
        """Executes one frame step of playing state with turbo boost support."""
        if self.paused:
            return

        self.food.update()
        if self.food.is_expired():
            self.food = Food.spawn_new(self.snake.body, score=self.score)

        # AI Move input and Auto-Boost heuristic if enabled
        if self.settings["auto_play"]:
            ai_move = AISolver.get_next_move(
                self.snake.body, self.food.pos, self.snake.dx, self.snake.dy
            )
            if ai_move:
                self.snake.queue_direction(ai_move[0], ai_move[1])
            ai_boost = AISolver.should_boost(
                self.snake.body, self.food.pos, self.snake.dx, self.snake.dy
            )
            self.is_boosted = is_speed_held or ai_boost
        else:
            self.is_boosted = is_speed_held

        base_delay = DIFFICULTY_MAP[self.settings["difficulty"]]
        move_delay = max(1, base_delay // 3) if self.is_boosted else base_delay
        self.move_counter += 1

        if self.move_counter >= move_delay:
            self.move_counter = 0
            is_alive, head = self.snake.step(wrap_walls=self.settings["wrap_walls"])

            if not is_alive:
                self.trigger_game_over()
                return

            # Add speed boost spark trail
            if self.is_boosted and self.snake.body:
                tail_px = self.snake.body[0][0] * TILE_SIZE + TILE_SIZE // 2
                tail_py = self.snake.body[0][1] * TILE_SIZE + TILE_SIZE // 2
                self.particles.add_speed_trail(tail_px, tail_py)

            # Check Food Collision
            if head[0] == self.food.x and head[1] == self.food.y:
                self.score += self.food.points
                self.snake.grow(self.food.growth)
                
                food_px = self.food.x * TILE_SIZE + TILE_SIZE // 2
                food_py = self.food.y * TILE_SIZE + TILE_SIZE // 2
                self.particles.add_apple_burst(food_px, food_py, is_golden=(self.food.type == "golden"))
                self.assets.play_sound("eat", self.settings["sound"])

                self.food = Food.spawn_new(self.snake.body, score=self.score)

        self.particles.update()

    def handle_menu_action(self, action):
        """Executes actions triggered by menu clicks."""
        if action == STATE_PLAYING:
            self.reset_game()
            self.state = STATE_PLAYING
        elif action == STATE_SETTINGS:
            self.state = STATE_SETTINGS
        elif action == STATE_MENU:
            self.state = STATE_MENU
            self.paused = False
        elif action == "restart":
            self.reset_game()
            self.state = STATE_PLAYING
        elif action == "toggle_pause":
            self.paused = not self.paused
        elif action == "resume":
            self.paused = False
        elif action == "toggle_difficulty":
            diffs = list(DIFFICULTY_MAP.keys())
            idx = (diffs.index(self.settings["difficulty"]) + 1) % len(diffs)
            self.settings["difficulty"] = diffs[idx]
        elif action == "toggle_sound":
            self.settings["sound"] = not self.settings["sound"]
        elif action == "toggle_ai":
            self.settings["auto_play"] = not self.settings["auto_play"]
        elif action == "toggle_wrap":
            self.settings["wrap_walls"] = not self.settings["wrap_walls"]
        elif action == "exit":
            return False
        return True

    def draw_grid_background(self, surface):
        """Renders grid tile background."""
        surface.fill(COLOR_BG_DARK)
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(surface, COLOR_BG_GRID, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(surface, COLOR_BG_GRID, (0, y), (SCREEN_WIDTH, y), 1)

    def render(self):
        """Draws current frame based on state with camera shake effects."""
        if self.headless or not self.screen:
            return

        render_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        mouse_pos = pygame.mouse.get_pos()
        high_score = self.high_scores.get_high_score(self.settings["difficulty"])

        if self.state == STATE_MENU:
            self.current_buttons = self.menus.draw_main_menu(render_surf, mouse_pos, high_score)
        elif self.state == STATE_SETTINGS:
            self.current_buttons = self.menus.draw_settings_menu(render_surf, mouse_pos, self.settings)
        elif self.state == STATE_PLAYING:
            self.draw_grid_background(render_surf)
            self.food.draw(render_surf, self.assets.sprites)
            self.snake.draw(render_surf, self.assets.sprites)
            self.particles.draw(render_surf)
            hud_buttons = self.menus.draw_hud(
                render_surf, mouse_pos, self.score, high_score, self.settings["difficulty"],
                is_boosted=self.is_boosted
            )
            if self.paused:
                self.current_buttons = self.menus.draw_pause_overlay(render_surf, mouse_pos)
            else:
                self.current_buttons = hud_buttons
        elif self.state == STATE_GAME_OVER:
            self.draw_grid_background(render_surf)
            self.food.draw(render_surf, self.assets.sprites)
            self.snake.draw(render_surf, self.assets.sprites)
            self.particles.draw(render_surf)
            self.current_buttons = self.menus.draw_game_over(
                render_surf, mouse_pos, self.score, self.is_new_record, high_score
            )

        # Apply screen shake offset
        shake_offset = (0, 0)
        if self.screen_shake > 0:
            shake_offset = (
                random.randint(-self.screen_shake, self.screen_shake),
                random.randint(-self.screen_shake, self.screen_shake),
            )
            self.screen_shake -= 1

        self.screen.fill((0, 0, 0))
        self.screen.blit(render_surf, shake_offset)
        pygame.display.flip()

    def run(self):
        """Starts main application loop."""
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(self, "current_buttons"):
                        for btn in self.current_buttons:
                            if btn.is_hovered(mouse_pos):
                                if not self.handle_menu_action(btn.action):
                                    running = False
                                break
                elif event.type == pygame.KEYDOWN:
                    if self.state == STATE_PLAYING:
                        if event.key in (pygame.K_ESCAPE, pygame.K_p):
                            self.paused = not self.paused
                        elif not self.paused and not self.settings["auto_play"]:
                            self.snake.handle_key_event(event.key)
                    elif self.state == STATE_GAME_OVER:
                        if event.key == pygame.K_r:
                            self.handle_menu_action("restart")
                        elif event.key == pygame.K_m:
                            self.handle_menu_action(STATE_MENU)

            if self.state == STATE_PLAYING:
                keys = pygame.key.get_pressed()
                is_speed_held = bool(
                    keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or
                    keys[pygame.K_TAB] or keys[pygame.K_SPACE] or
                    keys[pygame.K_f] or keys[pygame.K_e]
                )
                self.update_gameplay(is_speed_held=is_speed_held)

            self.render()
            self.clock.tick(FPS)

        pygame.quit()
