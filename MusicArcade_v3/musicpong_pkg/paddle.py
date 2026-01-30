
import pygame
from utils import map_range

class Paddle:
    def __init__(self, x, screen_height, width=20, height=120, color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.x = x
        self.y = screen_height // 2 - height // 2
        self.color = color
        self.rect = pygame.Rect(x, self.y, width, height)
        
    def update(self, target_y):
        """Actualiza la posición vertical del paddle"""
        # Aplicar suavizado para movimiento más natural
        self.y += (target_y - self.y) * 0.2
        self.rect.y = self.y
        
    def keep_in_bounds(self, screen_height):
        """Mantiene el paddle dentro de los límites de la pantalla"""
        if self.rect.top < 0:
            self.rect.top = 0
            self.y = self.rect.y
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.y = self.rect.y
            
    def draw(self, screen):
        """Dibuja el paddle en la pantalla"""
        pygame.draw.rect(screen, self.color, self.rect)
