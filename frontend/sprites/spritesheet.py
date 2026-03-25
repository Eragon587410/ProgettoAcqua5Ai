import pygame
import random


class Spritesheet:
    """Taglia i personaggi da una griglia 4 colonne × 2 righe."""

    COLS = 4
    ROWS = 2

    def __init__(self, path: str):
        self.sheet = pygame.image.load(path).convert_alpha()
        w, h = self.sheet.get_size()
        self.sprite_w = w // self.COLS
        self.sprite_h = h // self.ROWS

    def get_sprite(self, col: int, row: int) -> pygame.Surface:
        """Ritorna il singolo sprite alla colonna/riga indicata (0-based)."""
        rect = pygame.Rect(col * self.sprite_w, row * self.sprite_h,
                           self.sprite_w, self.sprite_h)
        return self.sheet.subsurface(rect)

    def get_all_sprites(self) -> list[pygame.Surface]:
        """Ritorna tutti gli 8 sprite della griglia."""
        sprites = []
        for row in range(self.ROWS):
            for col in range(self.COLS):
                sprites.append(self.get_sprite(col, row))
        return sprites

    def get_random_sprites(self, n: int) -> list[pygame.Surface]:
        """Ritorna n sprite scelti casualmente (senza ripetizioni se possibile)."""
        all_s = self.get_all_sprites()
        k = min(n, len(all_s))
        return random.sample(all_s, k)