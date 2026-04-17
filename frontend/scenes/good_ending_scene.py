import pygame
import math
import random


class GoodEnding:

    W, H = 1000, 600

    def __init__(self, manager):
        self.manager  = manager
        self.tick     = 0

        # Font
        self.font_title = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_sub   = pygame.font.SysFont("Arial", 28)
        self.font_small = pygame.font.SysFont("Arial", 18)

        # Stelle fisse di sfondo
        random.seed(42)
        self.stars = [
            (random.randint(0, self.W), random.randint(0, self.H),
             random.uniform(0.5, 2.0))
            for _ in range(120)
        ]

        # Particelle luminose fluttuanti
        self.particles = [
            {
                "x": random.uniform(0, self.W),
                "y": random.uniform(0, self.H),
                "vx": random.uniform(-0.3, 0.3),
                "vy": random.uniform(-0.6, -0.2),
                "r": random.randint(2, 5),
                "alpha": random.randint(80, 200),
            }
            for _ in range(60)
        ]

    # ------------------------------------------------------------------

    def update(self, events, state):
        self.tick += 1

        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["alpha"] -= 0.4
            if p["alpha"] <= 0 or p["y"] < -10:
                p["x"]     = random.uniform(0, self.W)
                p["y"]     = self.H + 5
                p["vy"]    = random.uniform(-0.6, -0.2)
                p["alpha"] = random.randint(80, 200)

    # ------------------------------------------------------------------

    def draw(self, screen, state):
        # Sfondo: gradiente verticale cielo notturno → alba
        for y in range(self.H):
            t = y / self.H
            r = int(10  + t * 30)
            g = int(15  + t * 40)
            b = int(60  + t * 80)
            pygame.draw.line(screen, (r, g, b), (0, y), (self.W, y))

        # Stelle fisse
        for sx, sy, br in self.stars:
            twinkle = int(150 + 80 * math.sin(self.tick * 0.04 + sx))
            pygame.draw.circle(screen, (twinkle, twinkle, twinkle), (sx, sy), 1)

        # Particelle fluttuanti (dorate)
        for p in self.particles:
            surf = pygame.Surface((p["r"] * 2, p["r"] * 2), pygame.SRCALPHA)
            a = max(0, min(255, int(p["alpha"])))
            pygame.draw.circle(surf, (255, 220, 80, a), (p["r"], p["r"]), p["r"])
            screen.blit(surf, (int(p["x"]) - p["r"], int(p["y"]) - p["r"]))

        # Alone luminoso centrale
        glow = pygame.Surface((400, 400), pygame.SRCALPHA)
        for radius in range(180, 0, -10):
            alpha = int(18 * (1 - radius / 180))
            pygame.draw.circle(glow, (100, 200, 120, alpha),
                               (200, 200), radius)
        screen.blit(glow, (self.W // 2 - 200, self.H // 2 - 200))

        # Titolo principale con ombra
        pulse = 1.0 + 0.03 * math.sin(self.tick * 0.05)
        title_str = "COOPERAZIONE RAGGIUNTA"
        shadow = self.font_title.render(title_str, True, (0, 60, 20))
        title  = self.font_title.render(title_str, True, (80, 255, 140))
        tx = self.W // 2 - title.get_width() // 2
        ty = self.H // 2 - 100
        screen.blit(shadow, (tx + 3, ty + 3))
        screen.blit(title,  (tx, ty))

        # Sottotitolo
        sub_str = "I villaggi hanno raggiunto il 2100 in pace."
        sub = self.font_sub.render(sub_str, True, (200, 255, 210))
        screen.blit(sub, (self.W // 2 - sub.get_width() // 2, ty + 90))

        # Anno raggiunto
        year_str = f"Anno: {state.year}"
        year_surf = self.font_sub.render(year_str, True, (255, 220, 80))
        screen.blit(year_surf, (self.W // 2 - year_surf.get_width() // 2, ty + 140))

        # Riga decorativa
        line_y = ty + 195
        pygame.draw.line(screen, (80, 200, 100),
                         (self.W // 2 - 180, line_y),
                         (self.W // 2 + 180, line_y), 1)

        # Nota piccola in basso
        note = self.font_small.render(
            "L'acqua è una risorsa condivisa. Grazie per aver cooperato.",
            True, (160, 210, 170))
        screen.blit(note, (self.W // 2 - note.get_width() // 2, self.H - 50))