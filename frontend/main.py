import pygame
import sys

from frontend.scene_manager import SceneManager
from frontend.game_state import GameState
from frontend.settings import *
from backend import *

pygame.init()

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Water Conflict Simulation")

clock = pygame.time.Clock()

manager = SceneManager()
state = GameState()

village_a = Village("A", 300, 100, 2, 100)
village_b = Village("B", 300, 100, 2, 100)

global_manager = GlobalManager(2000)
water_source = WaterSource()

while True:

    events = pygame.event.get()

    for event in events:

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    manager.update(events,state)

    screen.fill((30,30,40))

    manager.draw(screen,state)

    pygame.display.flip()

    clock.tick(FPS)