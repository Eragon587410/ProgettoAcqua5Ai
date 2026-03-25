import pygame
from frontend.ui.water_bar import WaterBar
from frontend.ui.humor_bar import HumorBar
from frontend.sprites.character import Character
from frontend.sprites.village_population import VillagePopulation   # <-- NUOVO
from frontend.settings import *

from backend.GlobalManager import GlobalManager
from backend import ChoiceEnum
from backend.Village import Village

from pathlib import Path

current_path = Path.cwd()

from frontend.scenes.good_ending_scene import GoodEnding


class MapScene:
    def __init__(self, manager, intro_choice=None):
        self.manager = manager

        self.smoke_img = pygame.image.load(f"{current_path}/frontend/assets/smoke.png").convert_alpha()
        self.smoke_img = pygame.transform.scale(self.smoke_img, (200, 200))

        img_originale = pygame.image.load(f"{current_path}/frontend/assets/map.png").convert_alpha()
        self.map = pygame.transform.scale(img_originale, (1000, 600))

        self.barA = WaterBar(50, 50)
        self.barB = WaterBar(750, 50)
        self.humor_barA = HumorBar(50, 90)
        self.humor_barB = HumorBar(750, 90)

        self.timer = 0
        self.font = pygame.font.SysFont(None, 30)

        from frontend.ui.button import Button

        self.buttonA = Button("Villaggio A ha tutta l'acqua", 300, 250, 200, 50)
        self.buttonB = Button("Villaggio B ha tutta l'acqua", 550, 250, 200, 50)

        self.btn_collab = Button("Collaborazione", 250, 300, 200, 50)
        self.btn_guerra = Button("Guerra", 550, 300, 200, 50)

        self.village_a = None
        self.village_b = None
        self.char_walker = None

        # ------------------------------------------------------------------
        # Folle animate – sostituiscono i vecchi characters statici
        # Le aree dei villaggi sono i rettangoli sinistro/destro della mappa
        # ------------------------------------------------------------------
        initial_pop = Village.VILLAGGIO_A.num_persone  # stessa di partenza per entrambi

        # In map_scene.py
        self.crowd_a = VillagePopulation(
            sheet_path=f"{current_path}/frontend/assets/villageA_chars.png",
            area_rect=pygame.Rect(20, 380, 300, 180),
            initial_pop=initial_pop,
            sprite_size=80,
            mask_path=f"{current_path}/frontend/assets/mask_villageA.png", # Ora funziona!
        )

        self.crowd_b = VillagePopulation(
            sheet_path=f"{current_path}/frontend/assets/villageB_chars.png",
            area_rect=pygame.Rect(680, 380, 300, 180),
            initial_pop=initial_pop,
            sprite_size=80,
            mask_path=None, # Metti None o il path per il villaggio B
        )


        # --- Gestione scelta dall'IntroScene ---
        if intro_choice == 0:
            GlobalManager.INSTANCE.choice = ChoiceEnum.SHARED
            self.char_walker = Character(
                f"{current_path}/frontend/assets/villageA_chars.png",
                500, 400, rect=pygame.Rect(0, 0, 150, 150)
            )
            self.fase_gioco = "collaborazione"

        elif intro_choice == 1:
            GlobalManager.INSTANCE.choice = ChoiceEnum.ALL_TO_A
            self.char_walker = Character(
                f"{current_path}/frontend/assets/villageB_chars.png",
                850, 400, rect=pygame.Rect(0, 0, 150, 150)
            )
            self.fase_gioco = "simulazione"

        elif intro_choice == 2:
            GlobalManager.INSTANCE.choice = ChoiceEnum.ALL_TO_B
            self.char_walker = Character(
                f"{current_path}/frontend/assets/villageA_chars.png",
                150, 400, rect=pygame.Rect(0, 0, 150, 150)
            )
            self.fase_gioco = "simulazione"

        else:
            self.fase_gioco = "scelta_iniziale"

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update(self, events, state):

        state.humor_a = Village.VILLAGGIO_A.morale
        state.humor_b = Village.VILLAGGIO_B.morale

        # Aggiorna le folle ogni frame (animazione + riduzione proporzionale)
        self.crowd_a.update(Village.VILLAGGIO_A.num_persone)
        self.crowd_b.update(Village.VILLAGGIO_B.num_persone)

        if self.fase_gioco == "scelta_iniziale":
            for e in events:
                if self.buttonA.clicked(e):
                    GlobalManager.INSTANCE.choice = ChoiceEnum.ALL_TO_A
                    self.char_walker = Character(
                        f"{current_path}/frontend/assets/villageB_chars.png",
                        850, 400, rect=pygame.Rect(0, 0, 150, 150)
                    )
                    self.fase_gioco = "simulazione"

                if self.buttonB.clicked(e):
                    GlobalManager.INSTANCE.choice = ChoiceEnum.ALL_TO_B
                    self.char_walker = Character(
                        f"{current_path}/frontend/assets/villageA_chars.png",
                        150, 400, rect=pygame.Rect(0, 0, 150, 150)
                    )
                    self.fase_gioco = "simulazione"
            return

        elif self.fase_gioco == "simulazione":
            self.timer += 1
            if self.timer > 10:
                GlobalManager.INSTANCE.time.year_flow(GlobalManager.INSTANCE.choice)
                state.year = GlobalManager.INSTANCE.time.year
                self.timer = 0
                state.water_a = Village.VILLAGGIO_A.riserva_acqua
                state.water_b = Village.VILLAGGIO_B.riserva_acqua
                state.humor_a = Village.VILLAGGIO_A.morale
                state.humor_b = Village.VILLAGGIO_B.morale

            if state.year >= 2040 and not getattr(state, 'dam_built', False):
                state.dam_built = True

            if Village.VILLAGGIO_A.morale < 40 or Village.VILLAGGIO_B.morale < 40:
                self.fase_gioco = "camminata"

        elif self.fase_gioco == "camminata":
            if self.char_walker.x < 500: self.char_walker.x += 2
            elif self.char_walker.x > 500: self.char_walker.x -= 2
            if abs(self.char_walker.x - 500) <= 2:
                self.fase_gioco = "domanda"

        elif self.fase_gioco == "domanda":
            for e in events:
                if self.btn_collab.clicked(e):
                    self.fase_gioco = "collaborazione"
                    GlobalManager.INSTANCE.set_choice(ChoiceEnum.SHARED)

                if self.btn_guerra.clicked(e):
                    if GlobalManager.INSTANCE.choice == ChoiceEnum.ALL_TO_B:
                        self.enemy_char = Character(f"{current_path}/frontend/assets/villageA_chars.png", 150, 400, rect=pygame.Rect(0, 0, 150, 150))
                    else:
                        self.enemy_char = Character(f"{current_path}/frontend/assets/villageB_chars.png", 850, 400, rect=pygame.Rect(0, 0, 150, 150))
                    self.fase_gioco = "conflitto"
                    self.timer = 0

        elif self.fase_gioco == "conflitto":
            self.timer += 1
            if self.char_walker.x < 450: self.char_walker.x += 5
            elif self.char_walker.x > 550: self.char_walker.x -= 5
            if self.enemy_char.x < 450: self.enemy_char.x += 5
            elif self.enemy_char.x > 550: self.enemy_char.x -= 5
            if self.timer > 150:
                GlobalManager.INSTANCE.war()
                GlobalManager.INSTANCE.time.year_flow(GlobalManager.INSTANCE.choice)
                state.year = GlobalManager.INSTANCE.time.year
                self.timer = 0

                state.water_a = Village.VILLAGGIO_A.riserva_acqua
                state.water_b = Village.VILLAGGIO_B.riserva_acqua
                state.humor_a = Village.VILLAGGIO_A.morale
                state.humor_b = Village.VILLAGGIO_B.morale

                if Village.VILLAGGIO_A.estinto or Village.VILLAGGIO_B.estinto:
                    from frontend.scenes.bad_ending_scene import BadEnding
                    self.manager.change(BadEnding(self.manager))

        elif self.fase_gioco == "collaborazione":
            self.timer += 1
            if self.timer > 10:
                self.timer = 0
                if state.year < 2100:
                    GlobalManager.INSTANCE.time.year_flow(GlobalManager.INSTANCE.choice)
                    state.year = GlobalManager.INSTANCE.time.year
                    state.water_a = Village.VILLAGGIO_A.riserva_acqua
                    state.water_b = Village.VILLAGGIO_B.riserva_acqua
                    state.humor_a = Village.VILLAGGIO_A.morale
                    state.humor_b = Village.VILLAGGIO_B.morale
                else:
                    self.manager.change(GoodEnding(self.manager))


    def _draw_bars_panel(self, screen, x, y, width, height, label_water, label_humor,
                         water_val, humor_val, bar_water, bar_humor):
        """
        Pannello 1: sfondo nero semi-trasparente con bordo bianco.
        Contiene scritta + barra Water e scritta + barra Felicità.
        """
        # Sfondo semi-trasparente
        panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 140))
        screen.blit(panel_surf, (x, y))
 
        # Bordo bianco
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2, border_radius=6)
 
        label_font = pygame.font.SysFont("Arial", 13)
 
        # --- Riga WATER ---
        water_label_surf = label_font.render(label_water, True, (100, 200, 255))
        screen.blit(water_label_surf, (x + 8, y + 8))
        bar_water.x = x + 8
        bar_water.y = y + 26
        bar_water.draw(screen, water_val)
 
        # --- Riga FELICITA ---
        humor_label_surf = label_font.render(label_humor, True, (255, 220, 80))
        screen.blit(humor_label_surf, (x + 8, y + 50))
        bar_humor.x = x + 8
        bar_humor.y = y + 68
        bar_humor.draw(screen, humor_val)

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------

    def draw(self, screen, state):

        self.title_font = pygame.font.SysFont("Arial", 18, bold=True)

        if self.fase_gioco == "scelta_iniziale":
            screen.fill((30, 30, 40))
            text = self.font.render("Quale villaggio perderà acqua?", True, (255, 255, 255))
            screen.blit(text, (330, 200))
            self.buttonA.draw(screen)
            self.buttonB.draw(screen)
            return

        screen.blit(self.map, (0, 0))


         # ── PANNELLO VILLAGGIO A (in alto a sinistra) ──────────────────────────
        self._draw_bars_panel(
            screen,
            x=25, y=10,
            width=220, height=130,
            label_water="Water",
            label_humor="Felicità",
            water_val=state.water_a,
            humor_val=state.humor_a,
            bar_water=self.barA,
            bar_humor=self.humor_barA,
        )
 
        # ── PANNELLO VILLAGGIO B (in alto a destra) ────────────────────────────
        self._draw_bars_panel(
            screen,
            x=725, y=10,
            width=220, height=130,
            label_water="Water",
            label_humor="Felicità",
            water_val=state.water_b,
            humor_val=state.humor_b,
            bar_water=self.barB,
            bar_humor=self.humor_barB,
        )

        year_text = self.font.render(f"Year: {state.year}", True, (0, 0, 0))
        screen.blit(year_text, (450, 20))

        numero_persone_a = Village.VILLAGGIO_A.num_persone
        numero_persone_b = Village.VILLAGGIO_B.num_persone
        screen.blit(self.font.render(f"Popolazione: {numero_persone_a}", True, (255, 255, 255)), (50, 110))
        screen.blit(self.font.render(f"Popolazione: {numero_persone_b}", True, (255, 255, 255)), (750, 110))

        # ------------------------------------------------------------------
        # Disegna le folle animate (sostituiscono i vecchi characters statici)
        # Le folle sono sempre visibili tranne nella fase di scelta iniziale
        # ------------------------------------------------------------------
        self.crowd_a.draw(screen)
        self.crowd_b.draw(screen)

        if self.fase_gioco in ["camminata", "domanda", "collaborazione"]:
            self.char_walker.draw(screen)

        if self.fase_gioco == "domanda":
            q_text = self.font.render("L'acqua sta finendo! Cosa volete fare?", True, (255, 255, 255))
            screen.blit(q_text, (320, 200))
            self.btn_collab.draw(screen)
            self.btn_guerra.draw(screen)

        if self.fase_gioco == "conflitto":
            self.char_walker.draw(screen)
            self.enemy_char.draw(screen)
            if abs(self.char_walker.x - self.enemy_char.x) < 100:
                import random
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                screen.blit(self.smoke_img, (400 + offset_x, 350 + offset_y))
                screen.blit(self.font.render("SCONTRO!", True, (255, 0, 0)), (450, 300))