import pygame
import random
import math

# Definir colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
# Otros colores según sea necesario


# Función para dispersar partículas
def dispersar_particulas(particula, ball):
    # Calcular la distancia entre la partícula y la pelota
    distancia_x = ball.x - particula.x
    distancia_y = ball.y - particula.y
    distancia_total = math.sqrt(distancia_x ** 2 + distancia_y ** 2)

    # Ajustar la velocidad en función de la distancia
    if distancia_total != 0:
        # Calcula un factor de escala basado en la distancia
        escala = 1000 / distancia_total
        particula.vx = distancia_x * escala
        particula.vy = distancia_y * escala


class Particula:
    def __init__(self, x, y):
        self.reset(x, y)

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)  # Velocidad aleatoria en x
        self.vy = random.uniform(-1, 1)  # Velocidad aleatoria en y
        self.color = BLANCO  # Color de la partícula
        self.alpha_offset = random.uniform(0, 2 * math.pi)  # Desfase para la función sinusoidal
        self.velocidad_anterior = (0, 0)

    def dibujar(self, pantalla, tiempo_actual):
        alpha = self.calculate_alpha(tiempo_actual)
        color_con_alfa = self.color + (alpha,)
        pygame.draw.circle(pantalla, color_con_alfa, (int(self.x), int(self.y)), 1)

    def calculate_alpha(self, tiempo_actual):
        # Utiliza una función sinusoidal para cambiar gradualmente el alpha
        periodo = 3000  # Cambia cada 2 segundos
        amplitud = 75 # 128  # Amplitud del cambio de alpha
        alpha = amplitud * math.sin((2 * math.pi / periodo) * tiempo_actual + self.alpha_offset) + 75 # 128
        return max(0, min(150, int(alpha)))  # Asegurarse de que alpha esté en el rango [0, 255]

    def mover(self, ball, screen_width, screen_height):
        # Si la partícula sale de la pantalla, la reseteamos en una posición aleatoria
        if self.x < 0 or self.x > screen_width or self.y < 0 or self.y > screen_height:
            self.reset(random.randint(0, screen_width), random.randint(0, screen_height))

        # Calculamos el vector de dirección desde la pelota a la partícula
        distancia_x = ball.rect.x - self.x
        distancia_y = ball.rect.y - self.y
        distancia_total = math.sqrt(distancia_x ** 2 + distancia_y ** 2)

        # Si la pelota está cerca de la partícula, la atraemos como si estuviera en un fluido
        if distancia_total < 35:
            if self.velocidad_anterior == (0, 0):
                # Si la velocidad anterior no está guardada, la guardamos
                self.velocidad_anterior = (self.vx, self.vy)

            # Calculamos el ángulo de desplazamiento en función de la posición relativa de la partícula con respecto a la pelota
            angulo_desplazamiento = math.atan2(distancia_y, distancia_x)

            # Calculamos la velocidad en función del ángulo de desplazamiento para simular un flujo alrededor de la pelota
            velocidad = 2  # Puedes ajustar la velocidad según lo desees
            self.vx = -velocidad * math.cos(angulo_desplazamiento)
            self.vy = -velocidad * math.sin(angulo_desplazamiento)
        elif self.velocidad_anterior != (0, 0):
            # Si la distancia supera el umbral y la velocidad anterior está guardada, la restauramos
            self.vx, self.vy = self.velocidad_anterior
            self.velocidad_anterior = (0, 0)  # Reiniciamos la velocidad anterior a (0, 0)

        self.x += self.vx
        self.y += self.vy



