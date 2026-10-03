"""
Menu and UI interface renderer with hover animations, glassmorphism cards, and interactive buttons.
"""
import pygame
from src.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_YELLOW, COLOR_GREEN,
    COLOR_RED, COLOR_GOLD, COLOR_GRAY, COLOR_CARD_BG, COLOR_CARD_BORDER,
    COLOR_HOVER, STATE_MENU, STATE_PLAYING, STATE_SETTINGS
)

class Button:
    """Represents an interactive UI button with hover animations and optional vector icons."""

    def __init__(self, rect, text, action, icon=None, color=COLOR_WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.icon = icon
        self.color = color

    def is_hovered(self, mouse_pos):
        """Checks if mouse is over the button."""
        return self.rect.collidepoint(mouse_pos)

    def draw(self, surface, font, is_hovered=False):
        """Draws button container, background, vector icon, and text."""
        bg_color = COLOR_HOVER if is_hovered else (35, 48, 70)
        border_color = COLOR_YELLOW if is_hovered else COLOR_CARD_BORDER

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=8)

        text_color = COLOR_YELLOW if is_hovered else self.color
        
        # Render text
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)

        # Draw vector pause bars if icon is "pause"
        if self.icon == "pause":
            text_rect.centerx += 8
            icon_x = text_rect.left - 16
            icon_y = self.rect.centery - 6
            bar_w, bar_h = 3, 12
            pygame.draw.rect(surface, text_color, (icon_x, icon_y, bar_w, bar_h), border_radius=1)
            pygame.draw.rect(surface, text_color, (icon_x + 6, icon_y, bar_w, bar_h), border_radius=1)

        surface.blit(text_surf, text_rect)


class MenuManager:
    """Manages all game menus and HUD elements."""

    def __init__(self, asset_manager):
        self.assets = asset_manager

    def draw_hud(self, surface, mouse_pos, score, high_score, difficulty, is_golden_active=False, is_boosted=False):
        """Draws top HUD during gameplay with current score, high score, difficulty, boost badge, and pause button."""
        hud_bg = pygame.Surface((SCREEN_WIDTH, 36), pygame.SRCALPHA)
        hud_bg.fill((15, 20, 30, 180))
        surface.blit(hud_bg, (0, 0))

        font = self.assets.fonts["regular"]
        small_font = self.assets.fonts["small"]

        # Current Score
        score_txt = font.render(f"Score: {score}", True, COLOR_WHITE)
        surface.blit(score_txt, (14, 6))

        # High Score
        high_txt = font.render(f"Best: {high_score}", True, COLOR_GOLD)
        surface.blit(high_txt, (140, 6))

        # Boost Badge
        if is_boosted:
            boost_bg = pygame.Surface((80, 24), pygame.SRCALPHA)
            boost_bg.fill((241, 196, 15, 60))
            surface.blit(boost_bg, (255, 6))
            pygame.draw.rect(surface, COLOR_GOLD, (255, 6, 80, 24), width=1, border_radius=4)
            boost_txt = small_font.render("⚡ BOOST", True, COLOR_GOLD)
            surface.blit(boost_txt, (262, 9))

        # Difficulty & Mode Info
        diff_txt = small_font.render(f"Diff: {difficulty}", True, COLOR_GRAY)
        surface.blit(diff_txt, (SCREEN_WIDTH - 210, 9))

        # Pause Button in HUD with vector pause icon
        pause_btn = Button((SCREEN_WIDTH - 95, 4, 85, 28), "Pause", "toggle_pause", icon="pause")
        pause_btn.draw(surface, small_font, pause_btn.is_hovered(mouse_pos))

        return [pause_btn]

    def draw_main_menu(self, surface, mouse_pos, high_score):
        """Renders modern main menu screen."""
        surface.fill((16, 22, 34))

        # Title
        title_font = self.assets.fonts["title"]
        title_surf = title_font.render("SNAKE ARCADE", True, COLOR_GREEN)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title_surf, title_rect)

        # High score banner with clean star styling
        reg_font = self.assets.fonts["regular"]
        best_surf = reg_font.render(f"★ HIGH SCORE: {high_score} ★", True, COLOR_GOLD)
        best_rect = best_surf.get_rect(center=(SCREEN_WIDTH // 2, 160))
        surface.blit(best_surf, best_rect)

        # Buttons
        med_font = self.assets.fonts["regular"]
        buttons = [
            Button((SCREEN_WIDTH // 2 - 120, 210, 240, 48), "Play Game", STATE_PLAYING),
            Button((SCREEN_WIDTH // 2 - 120, 275, 240, 48), "Settings", STATE_SETTINGS),
            Button((SCREEN_WIDTH // 2 - 120, 340, 240, 48), "Quit", "exit"),
        ]

        for btn in buttons:
            btn.draw(surface, med_font, btn.is_hovered(mouse_pos))

        # Footer Hint
        hint_font = self.assets.fonts["small"]
        hint_surf = hint_font.render("Controls: WASD/Arrows | Hold Shift/Space/Tab: Speed Boost | Esc: Pause", True, COLOR_GRAY)
        surface.blit(hint_surf, hint_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

        return buttons

    def draw_settings_menu(self, surface, mouse_pos, settings):
        """Renders settings menu with interactive toggles."""
        surface.fill((16, 22, 34))

        # Title
        title_font = self.assets.fonts["large"]
        title_surf = title_font.render("SETTINGS", True, COLOR_YELLOW)
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        reg_font = self.assets.fonts["regular"]
        buttons = [
            Button((SCREEN_WIDTH // 2 - 150, 130, 300, 44), f"Difficulty: {settings['difficulty']}", "toggle_difficulty"),
            Button((SCREEN_WIDTH // 2 - 150, 190, 300, 44), f"Sound: {'ON' if settings['sound'] else 'OFF'}", "toggle_sound"),
            Button((SCREEN_WIDTH // 2 - 150, 250, 300, 44), f"Auto-Play: {'ON' if settings['auto_play'] else 'OFF'}", "toggle_ai"),
            Button((SCREEN_WIDTH // 2 - 150, 310, 300, 44), f"Wall Wrap: {'ON' if settings['wrap_walls'] else 'OFF'}", "toggle_wrap"),
            Button((SCREEN_WIDTH // 2 - 100, 390, 200, 44), "Back", STATE_MENU),
        ]

        for btn in buttons:
            btn.draw(surface, reg_font, btn.is_hovered(mouse_pos))

        return buttons

    def draw_pause_overlay(self, surface, mouse_pos):
        """Draws interactive pause modal with Resume, Back to Menu, and Quit buttons."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 200))
        surface.blit(overlay, (0, 0))

        large_font = self.assets.fonts["large"]
        reg_font = self.assets.fonts["regular"]

        pause_surf = large_font.render("PAUSED", True, COLOR_YELLOW)
        surface.blit(pause_surf, pause_surf.get_rect(center=(SCREEN_WIDTH // 2, 120)))

        buttons = [
            Button((SCREEN_WIDTH // 2 - 120, 190, 240, 44), "Resume", "resume"),
            Button((SCREEN_WIDTH // 2 - 120, 250, 240, 44), "Back to Menu", STATE_MENU),
            Button((SCREEN_WIDTH // 2 - 120, 310, 240, 44), "Quit", "exit"),
        ]

        for btn in buttons:
            btn.draw(surface, reg_font, btn.is_hovered(mouse_pos))

        return buttons

    def draw_game_over(self, surface, mouse_pos, score, is_new_record, high_score):
        """Renders game over overlay with score summary and action buttons."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 210))
        surface.blit(overlay, (0, 0))

        large_font = self.assets.fonts["large"]
        med_font = self.assets.fonts["medium"]
        reg_font = self.assets.fonts["regular"]

        # Game Over Title
        title_surf = large_font.render("GAME OVER", True, COLOR_RED)
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 110)))

        # Score & Record Display
        score_surf = med_font.render(f"Final Score: {score}", True, COLOR_WHITE)
        surface.blit(score_surf, score_surf.get_rect(center=(SCREEN_WIDTH // 2, 170)))

        if is_new_record:
            rec_surf = reg_font.render("★ NEW HIGH SCORE RECORD! ★", True, COLOR_GOLD)
            surface.blit(rec_surf, rec_surf.get_rect(center=(SCREEN_WIDTH // 2, 210)))
        else:
            rec_surf = reg_font.render(f"Best Score: {high_score}", True, COLOR_GRAY)
            surface.blit(rec_surf, rec_surf.get_rect(center=(SCREEN_WIDTH // 2, 210)))

        # Buttons
        buttons = [
            Button((SCREEN_WIDTH // 2 - 120, 260, 240, 44), "Play Again (R)", "restart"),
            Button((SCREEN_WIDTH // 2 - 120, 320, 240, 44), "Main Menu (M)", STATE_MENU),
        ]

        for btn in buttons:
            btn.draw(surface, reg_font, btn.is_hovered(mouse_pos))

        return buttons
