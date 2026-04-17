import pygame
from frontend.scenes.bad_ending_scene import BadEnding

class WarScene:

    def __init__(self,manager):

        self.manager = manager

        self.smoke = pygame.image.load("assets/war.gif")

        self.timer = 0

    def update(self,events,state):

        self.timer += 1

        if self.timer > 300:

            self.manager.change(BadEnding(self.manager))

    def draw(self,screen,state):

        screen.blit(self.smoke,(450,250))