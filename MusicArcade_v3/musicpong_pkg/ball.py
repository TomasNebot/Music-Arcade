
import pygame
import random
import time

class Ball:
    def __init__(self, screen_width, screen_height, size=15):
        self.size = size
        self.reset(screen_width, screen_height)
        self.max_speed = 15
        
    def reset(self, screen_width, screen_height):
        """Reinicia la posición y velocidad de la pelota"""
        self.x = screen_width // 2 - self.size // 2
        self.y = screen_height // 2 - self.size // 2
        self.speed_x = 7 * random.choice([-1, 1])
        self.speed_y = 7 * random.choice([-1, 1])
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        
    def update(self):
        """Actualiza la posición de la pelota"""
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x = self.x
        self.rect.y = self.y
        
    def check_ceiling_floor_collision(self, screen_height, create_particles_callback=None):
        """Verifica colisiones con el techo y el suelo"""
        if self.rect.top <= 0 or self.rect.bottom >= screen_height:
            self.speed_y *= -1
            if create_particles_callback:
                pos_y = self.rect.centery if self.rect.top <= 0 else self.rect.bottom
                create_particles_callback(self.rect.centerx, pos_y)
                
    def check_paddle_collision(self, left_paddle, right_paddle, create_particles_callback=None):
        """Verifica colisiones con las paletas"""
        if self.rect.colliderect(left_paddle.rect) and self.speed_x < 0:
            self.speed_x *= -1.1  # Aumentar un poco la velocidad
            if create_particles_callback:
                create_particles_callback(left_paddle.rect.right, self.rect.centery, color=(100, 100, 255))
            # Añadir efecto basado en dónde golpea la pelota en la paleta
            relative_y = (self.rect.centery - left_paddle.rect.y) / left_paddle.height
            self.speed_y = 10 * (2 * relative_y - 1)
        
        if self.rect.colliderect(right_paddle.rect) and self.speed_x > 0:
            self.speed_x *= -1.1  # Aumentar un poco la velocidad
            if create_particles_callback:
                create_particles_callback(right_paddle.rect.left, self.rect.centery, color=(255, 100, 100))
            # Añadir efecto basado en dónde golpea la pelota en la paleta
            relative_y = (self.rect.centery - right_paddle.rect.y) / right_paddle.height
            self.speed_y = 10 * (2 * relative_y - 1)
    
    def check_goal(self, screen_width):
        """Verifica si la pelota salió por los laterales"""
        if self.rect.left <= 0:
            return 1  # Punto para jugador derecho
        elif self.rect.right >= screen_width:
            return -1  # Punto para jugador izquierdo
        return 0  # No hay punto
        
    def limit_speed(self):
        """Limita la velocidad máxima de la pelota"""
        if abs(self.speed_x) > self.max_speed:
            self.speed_x = self.max_speed * (1 if self.speed_x > 0 else -1)
        if abs(self.speed_y) > self.max_speed:
            self.speed_y = self.max_speed * (1 if self.speed_y > 0 else -1)
    
    def draw(self, screen):
        """Dibuja la pelota en la pantalla"""
        pygame.draw.ellipse(screen, (255, 255, 255), self.rect)
