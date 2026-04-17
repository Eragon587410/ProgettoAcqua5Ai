import pygame
import math
import random


class BadEnding:

    W, H = 1000, 600

    def __init__(self, manager):
        self.manager = manager
        self.tick    = 0

        # Font
        self.font_title = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_sub   = pygame.font.SysFont("Arial", 28)
        self.font_small = pygame.font.SysFont("Arial", 18)

        # Braci / cenere che cadono
        random.seed(7)
        self.embers = [
            {
                "x": random.uniform(0, self.W),
                "y": random.uniform(0, self.H),
                "vx": random.uniform(-0.4, 0.4),
                "vy": random.uniform(0.3, 1.2),
                "r": random.randint(1, 3),
                "alpha": random.randint(120, 255),
                "color": random.choice([
                    (255, 80,  20),
                    (255, 140, 0),
                    (200, 60,  0),
                ]),
            }
            for _ in range(80)
        ]

    # ------------------------------------------------------------------

    def update(self, events, state):
        self.tick += 1

        for e in self.embers:
            e["x"] += e["vx"] + 0.2 * math.sin(self.tick * 0.02 + e["x"])
            e["y"] += e["vy"]
            e["alpha"] -= 0.5
            if e["alpha"] <= 0 or e["y"] > self.H + 10:
                e["x"]     = random.uniform(0, self.W)
                e["y"]     = -5
                e["vy"]    = random.uniform(0.3, 1.2)
                e["alpha"] = random.randint(120, 255)

    # ------------------------------------------------------------------

    def draw(self, screen, state):
        # Sfondo: gradiente rosso fuoco → nero
        for y in range(self.H):
            t = y / self.H
            r = int(80  * (1 - t) + 10 * t)
            g = int(10  * (1 - t))
            b = 0
            pygame.draw.line(screen, (r, g, b), (0, y), (self.W, y))

        # Alone rossastro centrale (fuoco lontano)
        glow = pygame.Surface((500, 300), pygame.SRCALPHA)
        for radius in range(140, 0, -8):
            alpha = int(20 * (1 - radius / 140))
            pygame.draw.circle(glow, (200, 40, 0, alpha),
                               (250, 150), radius)
        screen.blit(glow, (self.W // 2 - 250, self.H // 2 - 80))

        # Braci / cenere
        for e in self.embers:
            surf = pygame.Surface((e["r"] * 2, e["r"] * 2), pygame.SRCALPHA)
            a = max(0, min(255, int(e["alpha"])))
            pygame.draw.circle(surf, (*e["color"], a),
                               (e["r"], e["r"]), e["r"])
            screen.blit(surf, (int(e["x"]) - e["r"], int(e["y"]) - e["r"]))

        # Titolo con sfarfallio (flickering)
        flicker = max(180, 255 - int(40 * abs(math.sin(self.tick * 0.15))))
        title_str = "GUERRA PER L'ACQUA"
        shadow = self.font_title.render(title_str, True, (60, 0, 0))
        title  = self.font_title.render(title_str, True, (flicker, 40, 0))
        tx = self.W // 2 - title.get_width() // 2
        ty = self.H // 2 - 100
        screen.blit(shadow, (tx + 4, ty + 4))
        screen.blit(title,  (tx, ty))

        # Sottotitolo
        sub_str = "La civiltà è crollata prima del 2100."
        sub = self.font_sub.render(sub_str, True, (220, 160, 120))
        screen.blit(sub, (self.W // 2 - sub.get_width() // 2, ty + 90))

        # Anno in cui è crollata
        year_str = f"Crollo nell'anno: {state.year}"
        year_surf = self.font_sub.render(year_str, True, (255, 100, 50))
        screen.blit(year_surf, (self.W // 2 - year_surf.get_width() // 2, ty + 140))

        # Riga decorativa
        line_y = ty + 195
        pygame.draw.line(screen, (150, 40, 0),
                         (self.W // 2 - 180, line_y),
                         (self.W // 2 + 180, line_y), 1)

        # Nota piccola in basso
        note = self.font_small.render(
            "L'acqua non condivisa porta alla distruzione.",
            True, (180, 100, 80))
        screen.blit(note, (self.W // 2 - note.get_width() // 2, self.H - 50))