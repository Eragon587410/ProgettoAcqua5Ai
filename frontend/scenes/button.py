import pygame


class Button:

    def __init__(self, text, x, y, w, h,
                 color=None, hover_color=None,
                 text_color=(255, 255, 255),
                 border_color=None,
                 font_size=22,
                 border_radius=8):

        self.rect         = pygame.Rect(x, y, w, h)
        self.text         = text
        self.color        = color        or (70, 70, 90)
        self.hover_color  = hover_color  or (100, 100, 130)
        self.text_color   = text_color
        self.border_color = border_color or (180, 180, 200)
        self.border_radius = border_radius
        self.font         = pygame.font.SysFont("Arial", font_size)
        self._hovered     = False

    # ------------------------------------------------------------------

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        self._hovered = self.rect.collidepoint(mouse_pos)

        bg = self.hover_color if self._hovered else self.color

        # Ombra leggera
        shadow = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 60))
        screen.blit(shadow, (self.rect.x + 3, self.rect.y + 4))

        # Sfondo pulsante
        pygame.draw.rect(screen, bg, self.rect, border_radius=self.border_radius)

        # Bordo
        pygame.draw.rect(screen, self.border_color, self.rect,
                         width=2, border_radius=self.border_radius)

        # Testo centrato
        txt_surf = self.font.render(self.text, True, self.text_color)
        tx = self.rect.x + (self.rect.w - txt_surf.get_width())  // 2
        ty = self.rect.y + (self.rect.h - txt_surf.get_height()) // 2
        screen.blit(txt_surf, (tx, ty))

    # ------------------------------------------------------------------

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True