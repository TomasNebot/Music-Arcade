
import pygame
import random
import time

class ParticleSystem:
    def __init__(self, max_particles=100):
        self.particles = []
        self.max_particles = max_particles
        
    def create_particles(self, x, y, count=20, color=(255, 255, 255)):
        """Crea partículas en la posición dada"""
        for _ in range(count):
            speed_x = random.uniform(-3, 3)
            speed_y = random.uniform(-3, 3)
            lifetime = random.uniform(0.5, 1.5)
            size = random.uniform(2, 5)
            self.particles.append({
                'x': x,
                'y': y,
                'speed_x': speed_x,
                'speed_y': speed_y,
                'size': size,
                'color': color,
                'lifetime': lifetime,
                'created': time.time()
            })
            
            # Mantener el número de partículas bajo control
            if len(self.particles) > self.max_particles:
                self.particles.pop(0)
    
    def update_and_draw(self, surface):
        """Actualiza y renderiza las partículas"""
        current_time = time.time()
        for particle in self.particles[:]:
            # Verificar tiempo de vida
            if current_time - particle['created'] > particle['lifetime']:
                self.particles.remove(particle)
                continue
                
            # Actualizar posición
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            
            # Dibujar partícula con opacidad basada en tiempo de vida
            alpha = 255 * (1 - (current_time - particle['created']) / particle['lifetime'])
            color = particle['color'] + (int(alpha),)
            pygame.draw.circle(surface, color, 
                              (int(particle['x']), int(particle['y'])), 
                              int(particle['size']))
