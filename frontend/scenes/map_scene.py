import pygame
from frontend.ui.water_bar import WaterBar
from frontend.ui.humor_bar import HumorBar
from frontend.sprites.character import Character
from frontend.settings import *

from backend.GlobalManager import GlobalManager
from backend import ChoiceEnum
from backend.Village import Village

from pathlib import Path

current_path = Path.cwd()

# Assicurati di avere questo file creato, o adatta il nome
from frontend.scenes.good_ending_scene import GoodEnding 

class MapScene:
    def __init__(self, manager):
        self.manager = manager

        self.smoke_img = pygame.image.load(f"{current_path}/frontend/assets/smoke.png").convert_alpha()
        # Se    è troppo grande o piccola, ridimensionala così:
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
        
        # Bottoni Scelta Iniziale
        self.buttonA = Button("Paese A perde acqua", 300, 250, 200, 50)
        self.buttonB = Button("Paese B perde acqua", 550, 250, 200, 50)
        
        # Bottoni Scelta Finale (Collaborazione o Guerra)
        self.btn_collab = Button("Collaborazione", 250, 300, 200, 50)
        self.btn_guerra = Button("Guerra", 550, 300, 200, 50)

        # Gestore delle fasi: "scelta_iniziale", "simulazione", "camminata", "domanda", "collaborazione"
        self.fase_gioco = "scelta_iniziale" 
        self.village_a = None
        self.village_b = None

        # RITAGLIO PERSONAGGI (x, y, larghezza, altezza). 
        # Modifica 150, 150 se i volti sono più grandi o più piccoli
        self.char_walker = None # Lo creiamo dopo in base a chi perde acqua
        
        self.characters = [
            # Primo volto in alto a sinistra (0, 0)
            Character(f"{current_path}/frontend/assets/villageA_chars.png", 150, 400, rect=pygame.Rect(0, 0, 150, 150)),
            # Secondo volto (150, 0)
            Character(f"{current_path}/frontend/assets/villageA_chars.png", 220, 400, rect=pygame.Rect(150, 0, 150, 150)), 
        ]

        self.smoke_img = pygame.image.load(f"{current_path}/frontend/assets/smoke.png").convert_alpha()
        # Se è troppo grande o piccola, ridimensionala così:
        self.smoke_img = pygame.transform.scale(self.smoke_img, (200, 200))

    def update(self, events, state):

        state.humor_a = Village.VILLAGGIO_A.morale
        state.humor_b = Village.VILLAGGIO_B.morale
        # FASE 1: Scelta di chi perde acqua
        if self.fase_gioco == "scelta_iniziale":
            for e in events:
                if self.buttonA.clicked(e):
                    #self.losing_village = "A"
                    GlobalManager.INSTANCE.choice = ChoiceEnum.ALL_TO_A
                    self.char_walker = Character(f"{current_path}/frontend/assets/villageA_chars.png", 150, 400, rect=pygame.Rect(0, 0, 150, 150))
                    self.fase_gioco = "simulazione"
                    
                if self.buttonB.clicked(e):
                    #self.losing_village = "B"
                    GlobalManager.INSTANCE.choice = ChoiceEnum.ALL_TO_B
                    self.char_walker = Character(f"{current_path}/frontend/assets/villageB_chars.png", 850, 400, rect=pygame.Rect(0, 0, 150, 150))
                    self.fase_gioco = "simulazione"
            return

        # FASE 2: Simulazione anni normale
        elif self.fase_gioco == "simulazione":
            self.timer += 1
            if self.timer > 10:
                GlobalManager.INSTANCE.time.year_flow(GlobalManager.INSTANCE.choice)
                state.year = GlobalManager.INSTANCE.time.year
                self.timer = 0

                #if self.losing_village == "A": state.water_a -= 10
                #if self.losing_village == "B": state.water_b -= 10
                state.water_a = Village.VILLAGGIO_A.riserva_acqua
                state.water_b = Village.VILLAGGIO_B.riserva_acqua
                state.humor_a = Village.VILLAGGIO_A.morale
                state.humor_b = Village.VILLAGGIO_B.morale
                print(f"a: {state.water_a} - {Village.VILLAGGIO_A.riserva_acqua}\n")
                print(f"b: {state.water_b} - {Village.VILLAGGIO_B.riserva_acqua}")


            # Evento diga
            if state.year >= 2040 and not getattr(state, 'dam_built', False):
                state.dam_built = True
                #if self.losing_village == "B": state.water_b -= 40
                #if self.losing_village == "A": state.water_a -= 40

            # Controllo soglia critica dinamico (controlla il villaggio che sta perdendo acqua)
            #acqua_attuale = state.water_a if self.losing_village == "A" else state.water_b
            if Village.VILLAGGIO_A.morale < 40 or Village.VILLAGGIO_B.morale < 40:
                self.fase_gioco = "camminata"

        # FASE 3: Il personaggio cammina verso il centro
        elif self.fase_gioco == "camminata":
            # Muovi verso x=500
            if self.char_walker.x < 500: self.char_walker.x += 2
            elif self.char_walker.x > 500: self.char_walker.x -= 2
            
            # Quando arriva al centro esatto (o quasi)
            if abs(self.char_walker.x - 500) <= 2:
                self.fase_gioco = "domanda"

        # FASE 4: Scelta Guerra
        elif self.fase_gioco == "domanda":
            for e in events:
                if self.btn_collab.clicked(e):
                    self.fase_gioco = "collaborazione"
                    GlobalManager.INSTANCE.set_choice(ChoiceEnum.SHARED)
                
                if self.btn_guerra.clicked(e):
                    # Prepariamo i personaggi per la rissa
                    # Creiamo un secondo personaggio che corre dal lato opposto
                    if GlobalManager.INSTANCE.choice == ChoiceEnum.ALL_TO_B:
                        self.enemy_char = Character(f"{current_path}/frontend/assets/villageA_chars.png", 150, 400, rect=pygame.Rect(0, 0, 150, 150))
                    else:
                        self.enemy_char = Character(f"{current_path}/frontend/assets/villageB_chars.png", 850, 400, rect=pygame.Rect(0, 0, 150, 150))
                    
                    self.fase_gioco = "conflitto"
                    self.timer = 0

        # FASE 6: Animazione Battaglia
        elif self.fase_gioco == "conflitto":
            self.timer += 1
            
            # 1. I due personaggi corrono verso il centro (500)
            if self.char_walker.x < 450: self.char_walker.x += 5
            elif self.char_walker.x > 550: self.char_walker.x -= 5
            
            if self.enemy_char.x < 450: self.enemy_char.x += 5
            elif self.enemy_char.x > 550: self.enemy_char.x -= 5

            # 2. Dopo un po' che corrono, passiamo al Bad Ending
            if self.timer > 150:
                from frontend.scenes.bad_ending_scene import BadEnding
                self.manager.change(BadEnding(self.manager))

        # FASE 5: Collaborazione (Gli anni volano, l'acqua si equalizza)
        elif self.fase_gioco == "collaborazione":
            self.timer += 1
            if self.timer > 10: # Scorre molto più veloce!
                self.timer = 0
                if state.year < 2100:
                    GlobalManager.INSTANCE.time.year_flow(GlobalManager.INSTANCE.choice)
                    state.year = GlobalManager.INSTANCE.time.year
                    self.timer = 0

                    #if self.losing_village == "A": state.water_a -= 10
                    #if self.losing_village == "B": state.water_b -= 10
                    state.water_a = Village.VILLAGGIO_A.riserva_acqua
                    state.water_b = Village.VILLAGGIO_B.riserva_acqua
                    state.humor_a = Village.VILLAGGIO_A.morale
                    state.humor_b = Village.VILLAGGIO_B.morale
                    print(f"a: {state.water_a} - {Village.VILLAGGIO_A.riserva_acqua}\n")
                    print(f"b: {state.water_b} - {Village.VILLAGGIO_B.riserva_acqua}")
                else:
                    # Raggiunto il 2100, si vince!
                    self.manager.change(GoodEnding(self.manager))


    def draw(self, screen, state):

        self.title_font = pygame.font.SysFont("Arial", 16)
        
        # Disegno Schermata di Scelta Iniziale
        if self.fase_gioco == "scelta_iniziale":
            screen.fill((30, 30, 40))
            text = self.font.render("Quale villaggio perderà acqua?", True, (255, 255, 255))
            screen.blit(text, (330, 200))
            self.buttonA.draw(screen)
            self.buttonB.draw(screen)
            return

        # Disegno Mappa Normale (per tutte le altre fasi)
        screen.blit(self.map, (0, 0))

        self.barA.draw(screen, state.water_a)
        barA_title_text = self.title_font.render(f"water", True, (255, 255, 255))
        screen.blit(barA_title_text, (50, 32))

        self.barB.draw(screen, state.water_b)
        barB_title_text = self.title_font.render(f"water", True, (255, 255, 255))
        screen.blit(barB_title_text, (750, 32))

        self.humor_barA.draw(screen, state.humor_a)
        humor_barA_title_text = self.title_font.render(f"felicità", True, (255, 255, 255))
        screen.blit(humor_barA_title_text, (50, 70))

        self.humor_barB.draw(screen, state.humor_b)
        humor_barB_title_text = self.title_font.render(f"felicità", True, (255, 255, 255))
        screen.blit(humor_barB_title_text, (750, 70))

        year_text = self.font.render(f"Year: {state.year}", True, (255, 255, 255))
        screen.blit(year_text, (450, 20))

        numero_persone_a = Village.VILLAGGIO_A.num_persone
        numero_persone_b = Village.VILLAGGIO_B.num_persone

        persone_a_text = self.font.render(f"Popolazione: {numero_persone_a}", True, (150, 75, 0))
        persone_b_text = self.font.render(f"Popolazione: {numero_persone_b}", True, (150, 75, 0))

        screen.blit(persone_a_text, (50, 110))
        screen.blit(persone_b_text, (750, 110))

        # Disegno Personaggi Statici
        for c in self.characters:
            c.draw(screen)

        # Disegno Personaggio in cammino (se serve)
        if self.fase_gioco in ["camminata", "domanda", "collaborazione"]:
            self.char_walker.draw(screen)

        # Disegno Bottoni Domanda Finale
        if self.fase_gioco == "domanda":
            q_text = self.font.render("L'acqua sta finendo! Cosa volete fare?", True, (255, 255, 255))
            screen.blit(q_text, (320, 200))
            self.btn_collab.draw(screen)
            self.btn_guerra.draw(screen)


        # Se siamo in guerra, disegna il secondo personaggio e il fumo
        if self.fase_gioco == "conflitto":
            self.enemy_char.draw(screen)
            
            # Se i personaggi sono vicini al centro, facciamo apparire il fumo
            if abs(self.char_walker.x - self.enemy_char.x) < 100:
                # Effetto "tremolio" casuale per la battaglia
                import random
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                
                # Disegna il fumo al centro dello scontro
                screen.blit(self.smoke_img, (400 + offset_x, 350 + offset_y))
                
                # Opzionale: aggiungi una scritta tipo "BANG!" o "POW!"
                fight_text = self.font.render("SCONTRO!", True, (255, 0, 0))
                screen.blit(fight_text, (450, 300))