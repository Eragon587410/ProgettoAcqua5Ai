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
        if random.random() < 0.5:
            self.vx = -self.vx
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

class Messenger:
    """
    Un cittadino estratto dalla folla che cammina verso un target X,
    si ferma lì, poi su richiesta torna al suo posto originale.

    Usato per la fase "camminata": invece di creare un nuovo Character,
    uno dei 6 esistenti esce dall'area e si dirige verso il centro.
    """
    WALK_SPEED = 2.5

    def __init__(self, citizen: _Citizen, target_x: float, target_y: float):
        self._c        = citizen
        self.target_x  = target_x
        self.target_y  = target_y
        self._origin_x = citizen.x
        self._origin_y = citizen.y
        self.arrived   = False
        self.returning = False
        self.done      = False

        # Imposta la direzione verso il target
        self._c.vx = self.WALK_SPEED if target_x > citizen.x else -self.WALK_SPEED

    def update(self):
        c = self._c

        if not self.arrived:
            c.x += c.vx
            if abs(c.x - self.target_x) <= abs(c.vx) + 1:
                c.x = self.target_x
                c.y = self.target_y
                c.vx = 0.0
                self.arrived = True

        elif self.returning:
            dx = self._origin_x - c.x
            c.vx = self.WALK_SPEED if dx > 0 else -self.WALK_SPEED
            c.x += c.vx
            if abs(dx) <= abs(c.vx) + 1:
                c.x = self._origin_x
                c.y = self._origin_y
                c.vx = random.uniform(_Citizen.SPEED_MIN, _Citizen.SPEED_MAX)
                self.done = True

        c.bob_phase += c.bob_speed

    def start_return(self):
        """Chiamare quando si vuole far tornare il messaggero al villaggio."""
        self.returning = True

    @property
    def x(self):
        return self._c.x

    @property
    def y(self):
        return self._c.y


# ======================================================================

class VillagePopulation:
    def __init__(self, sheet_path: str, area_rect: pygame.Rect,
                 initial_pop: int,
                 sprite_size: int = 80,
                 max_citizens: int = 6,
                 mask_path: str = None):

        self.area         = area_rect
        self.initial_pop  = max(1, initial_pop)
        self.max_citizens = max_citizens
        self.sprite_size  = sprite_size
        self.mask_path    = mask_path

        if mask_path:
            try:
                self.mask_img = pygame.image.load(mask_path).convert_alpha()
            except Exception:
                print(f"Errore caricamento maschera: {mask_path}")
                self.mask_img = None

        ss = Spritesheet(sheet_path)
        raw = ss.get_random_sprites(max_citizens)
        self.sprites = [
            pygame.transform.scale(s, (sprite_size, sprite_size)) for s in raw
        ]

        self._lanes: list[float] = self._compute_lanes()
        self._citizens: list[_Citizen] = []
        self._messenger: Messenger | None = None
        self._build_citizens(self.max_citizens)

    # ------------------------------------------------------------------
    # Interfaccia pubblica
    # ------------------------------------------------------------------

    def update(self, current_pop: int):
        target = self._target_count(current_pop)
        # Non toccare il messaggero nel conteggio
        messenger_citizen = self._messenger._c if self._messenger else None
        active = [c for c in self._citizens if c is not messenger_citizen]

        if target < len(active):
            # Rimuovi dalla fine, ma non il messaggero
            to_remove = len(active) - target
            removable = [c for c in reversed(self._citizens) if c is not messenger_citizen]
            for c in removable[:to_remove]:
                self._citizens.remove(c)
        elif target > len(active):
            self._build_citizens(target - len(active))

        for c in self._citizens:
            if c is messenger_citizen:
                continue   # il messaggero si aggiorna da solo
            c.update()

        if self._messenger and not self._messenger.done:
            self._messenger.update()
        elif self._messenger and self._messenger.done:
            self._messenger = None   # reintegrato nella folla

    def draw(self, screen: pygame.Surface):
        # Ordina per Y (pseudo-3D), il messaggero è già in self._citizens
        for c in sorted(self._citizens, key=lambda c: c.y):
            c.draw(screen)

    def extract_messenger(self, target_x: float, target_y: float) -> Messenger:
        """
        Estrae un cittadino dalla folla e lo manda verso (target_x, target_y).
        Ritorna il Messenger — map_scene può usarlo per controllare .arrived.
        Non serve disegnarlo separatamente: è già dentro self._citizens.
        """
        if not self._citizens:
            return None
        # Prende il cittadino più vicino al lato verso il target
        candidate = min(self._citizens, key=lambda c: abs(c.x - target_x))
        self._messenger = Messenger(candidate, target_x, target_y)
        return self._messenger

    def release_messenger(self):
        """Fa tornare il messaggero al suo posto originale."""
        if self._messenger and self._messenger.arrived:
            self._messenger.start_return()

    def has_active_messenger(self) -> bool:
        return self._messenger is not None and not self._messenger.done

    # ------------------------------------------------------------------
    # Metodi privati
    # ------------------------------------------------------------------

    def _compute_lanes(self) -> list[float]:
        n = self.max_citizens
        usable_h = self.area.height - self.sprite_size
        return [self.area.top + (usable_h * i / max(1, n - 1)) for i in range(n)]

    def _target_count(self, current_pop: int) -> int:
        return max(0, round(self.max_citizens * (current_pop / self.initial_pop)))

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