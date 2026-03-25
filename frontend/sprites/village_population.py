import pygame
import random
import math
from frontend.sprites.spritesheet import Spritesheet

class _Citizen:
    """Un singolo personaggio animato che cammina avanti/indietro."""
    SPEED_MIN = 0.4
    SPEED_MAX = 1.2
    FLIP_CHANCE   = 0.005
    BOUNCE_MARGIN = 10
    SPRITE_FACES_LEFT = True

    def __init__(self, sprite: pygame.Surface, x: float, y: float,
                 x_min: float, x_max: float):
        self.base_sprite = sprite
        self.sprite_w = sprite.get_width()
        self.x = x
        self.y = y
        self.x_min = x_min
        self.x_max = x_max
        self.vx = random.uniform(self.SPEED_MIN, self.SPEED_MAX)
        if random.random() < 0.5: self.vx = -self.vx
        self.bob_phase = random.uniform(0, math.tau)
        self.bob_speed = random.uniform(0.04, 0.09)
        self.bob_amp   = random.uniform(1.5, 3.0)

    def _should_flip(self) -> bool:
        moving_right = self.vx > 0
        return moving_right if self.SPRITE_FACES_LEFT else not moving_right

    def update(self):
        self.x += self.vx
        if self.x <= self.x_min + self.BOUNCE_MARGIN:
            self.vx = abs(self.vx)
        elif self.x + self.sprite_w >= self.x_max - self.BOUNCE_MARGIN:
            self.vx = -abs(self.vx)
        if random.random() < self.FLIP_CHANCE:
            self.vx = -self.vx
        self.bob_phase += self.bob_speed

    def draw(self, screen: pygame.Surface):
        img = pygame.transform.flip(self.base_sprite, self._should_flip(), False)
        draw_y = self.y + math.sin(self.bob_phase) * self.bob_amp
        screen.blit(img, (int(self.x), int(draw_y)))

# ======================================================================

class VillagePopulation:
    def __init__(self, sheet_path: str, area_rect: pygame.Rect,
                 initial_pop: int,
                 sprite_size: int = 80,
                 max_citizens: int = 6,
                 mask_path: str = None): # <-- AGGIUNTO QUI

        self.area         = area_rect
        self.initial_pop  = max(1, initial_pop)
        self.max_citizens = max_citizens
        self.sprite_size  = sprite_size
        self.mask_path    = mask_path

        # Se vuoi caricare la maschera per usarla in futuro
        if mask_path:
            try:
                self.mask_img = pygame.image.load(mask_path).convert_alpha()
            except:
                print(f"Errore caricamento maschera: {mask_path}")
                self.mask_img = None

        ss = Spritesheet(sheet_path)
        raw = ss.get_random_sprites(max_citizens)
        self.sprites = [
            pygame.transform.scale(s, (sprite_size, sprite_size)) for s in raw
        ]

        self._lanes = self._compute_lanes()
        self._citizens: list[_Citizen] = []
        self._build_citizens(self.max_citizens)

    def update(self, current_pop: int):
        target  = self._target_count(current_pop)
        current = len(self._citizens)
        if target < current:
            self._citizens = self._citizens[:target]
        elif target > current:
            self._build_citizens(target - current)
        for c in self._citizens:
            c.update()

    def draw(self, screen: pygame.Surface):
        for c in sorted(self._citizens, key=lambda c: c.y):
            c.draw(screen)

    def _compute_lanes(self) -> list[float]:
        n = self.max_citizens
        usable_h = self.area.height - self.sprite_size
        return [self.area.top + (usable_h * i / max(1, n - 1)) for i in range(n)]

    def _target_count(self, current_pop: int) -> int:
        ratio = current_pop / self.initial_pop
        return max(0, round(self.max_citizens * ratio))

    def _build_citizens(self, n: int):
        x_min, x_max = float(self.area.left), float(self.area.right)
        used_lanes = {round(c.y) for c in self._citizens}
        free_lanes = [y for y in self._lanes if round(y) not in used_lanes]
        random.shuffle(free_lanes)

        for _ in range(n):
            sprite = random.choice(self.sprites)
            y = free_lanes.pop() if free_lanes else random.choice(self._lanes)
            x = random.uniform(x_min, x_max - self.sprite_size)
            self._citizens.append(_Citizen(sprite, x, y, x_min, x_max))
