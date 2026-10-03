"""
Asset loader for authentic sprite sheet sprites, sound effects, and fonts.
"""
import os
import pygame
from src.constants import TILE_SIZE, COLOR_GOLD, COLOR_RED, COLOR_GREEN

class AssetManager:
    """Manages sprite sheet extraction, sound playback, and typography."""

    def __init__(self, sprite_sheet_path="f92be3bf-c946-4fd6-a596-b69edf486679.png"):
        self.sprite_sheet_path = sprite_sheet_path
        self.sprites = {}
        self.eat_sound = None
        self.game_over_sound = None
        self.fonts = {}

        self._init_fonts()
        self._load_sprites()
        self._load_sounds()

    def _init_fonts(self):
        """Initializes cross-platform fonts with reliable fallbacks."""
        font_families = "dejavusans,liberationsans,helvetica,arial,freesans"
        try:
            self.fonts["small"] = pygame.font.SysFont(font_families, 16)
            self.fonts["regular"] = pygame.font.SysFont(font_families, 22)
            self.fonts["medium"] = pygame.font.SysFont(font_families, 30, bold=True)
            self.fonts["large"] = pygame.font.SysFont(font_families, 50, bold=True)
            self.fonts["title"] = pygame.font.SysFont(font_families, 64, bold=True)
        except Exception:
            self.fonts["small"] = pygame.font.Font(None, 18)
            self.fonts["regular"] = pygame.font.Font(None, 24)
            self.fonts["medium"] = pygame.font.Font(None, 34)
            self.fonts["large"] = pygame.font.Font(None, 56)
            self.fonts["title"] = pygame.font.Font(None, 72)

    def _load_sprites(self):
        """Loads and extracts authentic sprites from the original sprite sheet."""
        if os.path.exists(self.sprite_sheet_path):
            try:
                sheet = pygame.image.load(self.sprite_sheet_path)
                if pygame.display.get_surface() is not None:
                    sheet = sheet.convert_alpha()
                self._extract_sprites_from_sheet(sheet)
                return
            except Exception:
                pass

        self._create_fallback_sprites()

    def _extract_sprites_from_sheet(self, sheet):
        """Extracts standard 64x64 sprites from the authentic sprite sheet."""
        def get_sprite(x, y, w=64, h=64):
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            surf.blit(sheet, (0, 0), pygame.Rect(x, y, w, h))
            return pygame.transform.scale(surf, (TILE_SIZE, TILE_SIZE))

        self.sprites = {
            "apple": get_sprite(0, 191, 64, 64),
            "body_horizontal": get_sprite(64, 0, 64, 64),
            "body_vertical": get_sprite(128, 64, 64, 64),
            "corner": get_sprite(0, 0, 64, 64),
            "head_up": get_sprite(191, 0, 64, 64),
            "head_right": get_sprite(256, 0, 64, 64),
            "head_down": get_sprite(256, 64, 64, 64),
            "head_left": get_sprite(191, 64, 64, 64),
            "tail_up": get_sprite(191, 128, 64, 64),
            "tail_right": get_sprite(256, 128, 64, 64),
            "tail_down": get_sprite(256, 191, 64, 64),
            "tail_left": get_sprite(192, 192, 64, 64),
        }

        # Create Golden Apple variant (golden tinted)
        golden_apple = self.sprites["apple"].copy()
        gold_tint = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        gold_tint.fill((255, 215, 0, 140))
        golden_apple.blit(gold_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.sprites["golden_apple"] = golden_apple

    def _create_fallback_sprites(self):
        """Generates fallback textures if sprite sheet is unavailable."""
        def make_block(color):
            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(s, color, (1, 1, TILE_SIZE - 2, TILE_SIZE - 2), border_radius=3)
            return s

        self.sprites = {
            "apple": make_block(COLOR_RED),
            "golden_apple": make_block(COLOR_GOLD),
            "body_horizontal": make_block(COLOR_GREEN),
            "body_vertical": make_block(COLOR_GREEN),
            "corner": make_block(COLOR_GREEN),
            "head_up": make_block((39, 174, 96)),
            "head_right": make_block((39, 174, 96)),
            "head_down": make_block((39, 174, 96)),
            "head_left": make_block((39, 174, 96)),
            "tail_up": make_block((46, 204, 113)),
            "tail_right": make_block((46, 204, 113)),
            "tail_down": make_block((46, 204, 113)),
            "tail_left": make_block((46, 204, 113)),
        }

    def _load_sounds(self):
        """Loads audio effects safely."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            if os.path.exists("apple_crunch.wav"):
                self.eat_sound = pygame.mixer.Sound("apple_crunch.wav")
            if os.path.exists("game_over_buzz.wav"):
                self.game_over_sound = pygame.mixer.Sound("game_over_buzz.wav")
        except Exception as e:
            print(f"Audio init note: {e}")

    def play_sound(self, sound_type, enabled=True):
        """Plays specified sound effect if sound is enabled."""
        if not enabled:
            return
        try:
            if sound_type == "eat" and self.eat_sound:
                self.eat_sound.play()
            elif sound_type == "game_over" and self.game_over_sound:
                self.game_over_sound.play()
        except Exception:
            pass
