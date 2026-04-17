import pygame
import os
from frontend.ui.water_bar import WaterBar
from frontend.ui.humor_bar import HumorBar
from frontend.sprites.character import Character
from frontend.sprites.village_population import VillagePopulation
from frontend.settings import *

from backend.GlobalManager import GlobalManager
from backend import ChoiceEnum
from backend.Village import Village
from backend.WaterSource import WaterSource

from pathlib import Path
current_path = Path.cwd()

from frontend.scenes.good_ending_scene import GoodEnding


class MapScene:
    def __init__(self, manager, intro_choice=None):
        self.manager = manager

        # war.png caricata come immagine statica (pygame non supporta gif animate)
        war_frames_path = f"{current_path}/frontend/assets/war"
        self.war_frames = []

        for i in range(9):
            frame = pygame.image.load(os.path.join(war_frames_path, f"{i+1}.png")).convert_alpha()
            frame = pygame.transform.scale(frame, (260, 160))
            self.war_frames.append(frame)
        self.war_frame_index = 0
        self.war_frame_timer = 0
        self.war_frame_speed = 6  

        img_originale = pygame.image.load(f"{current_path}/frontend/assets/map.png").convert_alpha()
        self.map = pygame.transform.scale(img_originale, (1000, 600))

        self.barA = WaterBar(50, 50)
        self.barB = WaterBar(750, 50)
        self.humor_barA = HumorBar(50, 90)
        self.humor_barB = HumorBar(750, 90)

        self.timer = 0
        self.font = pygame.font.SysFont(None, 30)

        from frontend.ui.button import Button
        self.buttonA = Button("Villaggio A ha tutta l'acqua", 300, 250, 200, 50, color=(20, 90, 40), hover_color=(30, 130, 60),
            border_color=(80, 200, 100), font_size=24,)
        self.buttonB = Button("Villaggio B ha tutta l'acqua", 550, 250, 200, 50,color=(20, 90, 40), hover_color=(30, 130, 60),
            border_color=(80, 200, 100), font_size=24,)
        # Pulsanti domanda: centrati a 1000x600, affiancati con gap
        btn_w, btn_h = 240, 58
        gap = 40
        total = btn_w * 2 + gap
        bx = (1000 - total) // 2
        by = 360
        self.btn_collab = Button(
            "Collaborazione", bx, by, btn_w, btn_h,
            color=(20, 90, 40), hover_color=(30, 130, 60),
            border_color=(80, 200, 100), font_size=24,
        )
        self.btn_guerra = Button(
            "Guerra", bx + btn_w + gap, by, btn_w, btn_h,
            color=(100, 20, 20), hover_color=(150, 30, 30),
            border_color=(220, 70, 70), font_size=24,
        )

        wall_original = pygame.image.load(f"{current_path}/frontend/assets/wall.png").convert_alpha()
        self.wall_img = pygame.transform.scale(wall_original, (1000, 600))
        self.wall_rect = self.wall_img.get_rect()

        wall_original_2 = pygame.image.load(f"{current_path}/frontend/assets/wall2.png").convert_alpha()
        self.wall_img_2 = pygame.transform.scale(wall_original_2, (1000, 600))
        self.wall_rect_2 = self.wall_img_2.get_rect()

        self._messenger = None
        self.enemy_char = None

        # Area pixel dei due villaggi (stessa usata per crowd)
        self.area_a = pygame.Rect(20, 380, 260, 140)
        self.area_b = pygame.Rect(680, 380, 260, 140)

        initial_pop = Village.VILLAGGIO_A.num_persone

        self.crowd_a = VillagePopulation(
            sheet_path=f"{current_path}/frontend/assets/villageA_chars.png",
            area_rect=self.area_a,
            initial_pop=initial_pop,
            sprite_size=80,
            mask_path=f"{current_path}/frontend/assets/mask_villageA.png",
        )
        self.crowd_b = VillagePopulation(
            sheet_path=f"{current_path}/frontend/assets/villageB_chars.png",
            area_rect=self.area_b,
            initial_pop=initial_pop,
            sprite_size=80,
            mask_path=None,
        )

        if intro_choice == 0:
            GlobalManager.INSTANCE.choice = ChoiceEnum.SHARED
            self.fase_gioco = "collaborazione"
        elif intro_choice == 1:
            GlobalManager.INSTANCE.choice = ChoiceEnum.ALL_TO_A
            self.fase_gioco = "simulazione"
        elif intro_choice == 2:
            GlobalManager.INSTANCE.choice = ChoiceEnum.ALL_TO_B
            self.fase_gioco = "simulazione"
        else:
            self.fase_gioco = "scelta_iniziale"

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update(self, events, state):
        state.humor_a = Village.VILLAGGIO_A.morale
        state.humor_b = Village.VILLAGGIO_B.morale

        self.crowd_a.update(Village.VILLAGGIO_A.num_persone)
        self.crowd_b.update(Village.VILLAGGIO_B.num_persone)

        if self.fase_gioco == "scelta_iniziale":
            for e in events:
                if self.buttonA.clicked(e):
                    GlobalManager.INSTANCE.choice = ChoiceEnum.ALL_TO_A
                    self.fase_gioco = "simulazione"
                if self.buttonB.clicked(e):
                    GlobalManager.INSTANCE.choice = ChoiceEnum.ALL_TO_B
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
                if Village.VILLAGGIO_B.morale < 40 or GlobalManager.INSTANCE.choice == ChoiceEnum.ALL_TO_A:
                    self._messenger = self.crowd_b.extract_messenger(target_x=320, target_y=430)
                else:
                    self._messenger = self.crowd_a.extract_messenger(target_x=650, target_y=430)
                self.fase_gioco = "camminata"

        elif self.fase_gioco == "camminata":
            if self._messenger and self._messenger.arrived:
                self.fase_gioco = "domanda"

        elif self.fase_gioco == "domanda":
            for e in events:
                if self.btn_collab.clicked(e):
                    if GlobalManager.INSTANCE.choice == ChoiceEnum.ALL_TO_A:
                        self.crowd_b.release_messenger()
                    else:
                        self.crowd_a.release_messenger()
                    self.fase_gioco = "collaborazione"
                    GlobalManager.INSTANCE.set_choice(ChoiceEnum.SHARED)

                if self.btn_guerra.clicked(e):
                    if GlobalManager.INSTANCE.choice == ChoiceEnum.ALL_TO_A:
                        self.crowd_b.release_messenger()
                    else:
                        self.crowd_a.release_messenger()
                    self.fase_gioco = "conflitto"
                    self.timer = 0

        elif self.fase_gioco == "conflitto":
            self.timer += 1

            # Animazione frame: gira ogni frame, indipendente dal timer di gioco
            self.war_frame_timer += 1
            if self.war_frame_timer >= self.war_frame_speed:
                self.war_frame_timer = 0
                self.war_frame_index = (self.war_frame_index + 1) % len(self.war_frames)

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
                    WaterSource.INSTANCE.poisoned = True
                    self.fase_gioco = "avvelenamento"
                    


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
        elif self.fase_gioco == "avvelenamento":
            self.timer += 1
            if self.timer > 10:
                self.timer = 0
                GlobalManager.INSTANCE.time.year_flow(GlobalManager.INSTANCE.choice)
                state.year = GlobalManager.INSTANCE.time.year
                state.water_a = Village.VILLAGGIO_A.riserva_acqua
                state.water_b = Village.VILLAGGIO_B.riserva_acqua
                state.humor_a = Village.VILLAGGIO_A.morale
                state.humor_b = Village.VILLAGGIO_B.morale

        


        if Village.VILLAGGIO_A.estinto and Village.VILLAGGIO_B.estinto:
            from frontend.scenes.bad_ending_scene import BadEnding
            self.manager.change(BadEnding(self.manager))

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _draw_bars_panel(self, screen, x, y, width, height,
                         label_water, label_humor,
                         water_val, humor_val, bar_water, bar_humor):
        panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 140))
        screen.blit(panel_surf, (x, y))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2, border_radius=6)
        label_font = pygame.font.SysFont("Arial", 13)
        screen.blit(label_font.render(label_water, True, (100, 200, 255)), (x + 8, y + 8))
        bar_water.x = x + 8
        bar_water.y = y + 26
        bar_water.draw(screen, water_val)
        screen.blit(label_font.render(label_humor, True, (255, 220, 80)), (x + 8, y + 50))
        bar_humor.x = x + 8
        bar_humor.y = y + 68
        bar_humor.draw(screen, humor_val)

    def _draw_war_smoke(self, screen):
        """
        Disegna la gif war sopra il villaggio perdente (stesso lato del muro).
        ALL_TO_A → muro su A → fumo su A (villaggio A perde acqua).
        ALL_TO_B → muro su B → fumo su B.
        Copre i cittadini con un rettangolo nero prima, poi disegna la gif sopra.
        """
        choice = GlobalManager.INSTANCE.choice
        if choice == ChoiceEnum.ALL_TO_A:
            area = self.area_b   # A ha tutta l'acqua → B è il perdente
        elif choice == ChoiceEnum.ALL_TO_B:
            area = self.area_a   # B ha tutta l'acqua → A è il perdente
        else:
            return  # collaborazione: niente fumo

        # Frame centrato nell'area (niente sfondo nero: i PNG hanno già trasparenza)
        current_frame = self.war_frames[self.war_frame_index]
        gif_x = area.x + (area.width - current_frame.get_width()) // 2
        gif_y = area.y + (area.height - current_frame.get_height()) // 2
        screen.blit(current_frame, (gif_x, gif_y))
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

        # 1. Mappa di sfondo
        screen.blit(self.map, (0, 0))

        # 2. Muri
        if GlobalManager.INSTANCE.choice == ChoiceEnum.ALL_TO_B:
            self.wall_rect.topleft = (0, 0)
            screen.blit(self.wall_img, self.wall_rect)

        if GlobalManager.INSTANCE.choice == ChoiceEnum.ALL_TO_A:
            self.wall_rect_2.topleft = (5, 0)
            screen.blit(self.wall_img_2, self.wall_rect_2)

        # 3. Pannelli barre
        self._draw_bars_panel(
            screen, x=25, y=10, width=220, height=130,
            label_water="Water", label_humor="Felicità",
            water_val=state.water_a, humor_val=state.humor_a,
            bar_water=self.barA, bar_humor=self.humor_barA,
        )
        self._draw_bars_panel(
            screen, x=725, y=10, width=220, height=130,
            label_water="Water", label_humor="Felicità",
            water_val=state.water_b, humor_val=state.humor_b,
            bar_water=self.barB, bar_humor=self.humor_barB,
        )

        year_text = self.font.render(f"Year: {state.year}", True, (0, 0, 0))
        screen.blit(year_text, (450, 20))

        numero_persone_a = Village.VILLAGGIO_A.num_persone
        numero_persone_b = Village.VILLAGGIO_B.num_persone
        screen.blit(self.font.render(f"Popolazione: {numero_persone_a}", True, (255, 255, 255)), (50, 110))
        screen.blit(self.font.render(f"Popolazione: {numero_persone_b}", True, (255, 255, 255)), (750, 110))

        # 4. Folle: in conflitto, nascondi il villaggio sotto la gif guerra
        choice = GlobalManager.INSTANCE.choice
        hide_a = (self.fase_gioco == "conflitto" and choice == ChoiceEnum.ALL_TO_B)
        hide_b = (self.fase_gioco == "conflitto" and choice == ChoiceEnum.ALL_TO_A)
        if not hide_a:
            self.crowd_a.draw(screen)
        if not hide_b:
            self.crowd_b.draw(screen)

        # 5. In fase conflitto: copri i cittadini e mostra la gif guerra
        if self.fase_gioco == "conflitto":
            self._draw_war_smoke(screen)
            # Pannello semitrasparente + scritta SCONTRO! centrata
            scontro_surf = pygame.Surface((200, 50), pygame.SRCALPHA)
            scontro_surf.fill((0, 0, 0, 160))
            screen.blit(scontro_surf, (400, 325))
            pygame.draw.rect(screen, (255, 80, 80), (400, 325, 200, 50), 2, border_radius=6)
            scontro_txt = self.font.render("SCONTRO!", True, (255, 80, 80))
            screen.blit(scontro_txt, (400 + (200 - scontro_txt.get_width()) // 2, 338))

        # 6. Domanda
        if self.fase_gioco == "domanda":
            # Pannello semitrasparente centrato
            panel_w, panel_h = 560, 200
            panel_x = (1000 - panel_w) // 2
            panel_y = 270
            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            screen.blit(panel, (panel_x, panel_y))
            pygame.draw.rect(screen, (180, 180, 200),
                             (panel_x, panel_y, panel_w, panel_h), 2, border_radius=10)
            # Titolo
            q_font = pygame.font.SysFont("Arial", 22, bold=True)
            q_text = q_font.render("L'acqua sta finendo! Cosa volete fare?",
                                   True, (255, 255, 255))
            screen.blit(q_text, (1000 // 2 - q_text.get_width() // 2, panel_y + 22))
            # Linea divisoria
            pygame.draw.line(screen, (120, 120, 150),
                             (panel_x + 30, panel_y + 58),
                             (panel_x + panel_w - 30, panel_y + 58), 1)
            self.btn_collab.draw(screen)
            self.btn_guerra.draw(screen)