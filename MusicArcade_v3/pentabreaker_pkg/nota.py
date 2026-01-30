import pygame
import random

COLOR_DEFAULT = (255, 255, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0,255,255)
COLOR_VIOLET = (111, 0, 255)

# Mapeo de notas MIDI a nombres en español
NOMBRE_NOTAS = {
    # Notas básicas
    48: "Do",  # C3
    50: "Re",  # D3
    52: "Mi",  # E3
    53: "Fa",  # F3
    55: "Sol", # G3
    57: "La",  # A3
    59: "Si",  # B3
    60: "Do",  # C4
    62: "Re",  # D4
    64: "Mi",  # E4
    65: "Fa",  # F4
    67: "Sol", # G4
    69: "La",  # A4
    71: "Si",  # B4
    72: "Do"   # C5
}

class Nota:
    def __init__(self, nota, x, y):
        self.x = x
        self.y = float(y)
        self.midi = nota
        self.impactado = False


class NotaDisparada:
    def __init__(self, pitch, x, y):
        self.pitch = pitch
        self.x = x  # Posición central de la pantalla
        self.y = y  # Dispara desde abajo
        self.velocidad = -5  # Movimiento hacia arriba
        self.radio = 6
        self.nombre = NOMBRE_NOTAS.get(pitch, "")  # Obtener el nombre de la nota

    def mover(self):
        self.y += self.velocidad

    def dibujar(self, screen, mostrar_texto=True):
        pygame.draw.circle(screen, COLOR_DEFAULT, (self.x, self.y), self.radio)
        # Si se debe mostrar texto y la nota tiene nombre
        if mostrar_texto and self.nombre:
            font = pygame.font.SysFont('Constantia', 16)
            texto = font.render(self.nombre, True, COLOR_BLUE)
            screen.blit(texto, (self.x + 12, self.y - 8))  # Mostrar texto a la derecha de la nota


class ParticulaImpacto:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)  # Velocidad horizontal aleatoria
        self.vy = random.uniform(-3, 3)  # Velocidad vertical
        self.alpha = 255  # Opacidad inicial
        self.size = random.randint(2, 5)  # Tamaño aleatorio

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 5  # Reducir opacidad progresivamente

    def dibujar(self, screen):
        if self.alpha > 0:
            color = (255, 255, 255, self.alpha)
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (self.size//2, self.size//2), self.size)
            screen.blit(surface, (self.x, self.y))


def actualizar_particulas(particulas):
    nuevas_particulas = []
    for particula in particulas:
        particula.actualizar()
        if particula.alpha > 0:
            nuevas_particulas.append(particula)
    particulas = nuevas_particulas