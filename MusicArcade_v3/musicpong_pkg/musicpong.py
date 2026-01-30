import pygame
import time
import threading
import random
from utils import *
from COM.COM_Pd import get_msgL, get_msgR, iniciar_osc, stop_osc
from musicpong_pkg.paddle import Paddle
from musicpong_pkg.ball import Ball
from musicpong_pkg.particles import ParticleSystem

class MusicPong:
    def __init__(self, screen, surface, screen_width, screen_height, state_callback=None, game_settings=None):
        self.screen = screen
        self.surface = surface
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.bg_color = (0, 0, 0)
        self.state_callback = state_callback
        # Desempaquetar configuraciones del juego
        if isinstance(game_settings, tuple) and len(game_settings) == 3:
            self.game_mode = game_settings[0]  # 1: un jugador, 2: dos jugadores
            self.pitch_min = game_settings[1]  # Valor mínimo de pitch (predeterminado: 30)
            self.pitch_max = game_settings[2]  # Valor máximo de pitch (predeterminado: 80)
        else:
            self.game_mode = 1 if game_settings is None else game_settings
            self.pitch_min = 45  # Valor predeterminado
            self.pitch_max = 80  # Valor predeterminado

        # Fuentes y colores
        self.font = pygame.font.SysFont('Constantia', 30)
        self.text_c = (78, 81, 139)

        # Variables del juego
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.run = True
        self.game_over = 0  # 0: jugando, 1: victoria, -1: derrota

        # Puntuaciones
        self.score_left = 0
        self.score_right = 0

        # Barras de los jugadores
        self.left_paddle = Paddle(20, screen_height, color=(100, 100, 255))
        self.right_paddle = Paddle(screen_width - 40, screen_height, color=(255, 100, 100))

        # Pelota
        self.ball = Ball(screen_width, screen_height)

        # Variables de pitch
        self.pitch_left = 0
        self.last_pitch_left = 0
        self.amplitud_left = 0

        self.pitch_right = 0
        self.last_pitch_right = 0
        self.amplitud_right = 0

        self.active_com = 0

        # Sistema de partículas
        self.particle_system = ParticleSystem()

    def create_particles(self, x, y, count=20, color=(255, 255, 255)):
        """Método para crear partículas desde cualquier parte del juego"""
        self.particle_system.create_particles(x, y, count, color)

    def update_paddle_positions(self):
        """Actualiza la posición de las paletas según los valores de pitch"""
        # Paleta izquierda (controlada por msgl)
        if self.amplitud_left > 40:  # Umbral de amplitud para detectar sonido
            # Normalizar el pitch usando el rango configurado
            target_y = map_range(self.pitch_left, self.pitch_min, self.pitch_max,
                                 self.screen_height - self.left_paddle.height, 0)
            self.left_paddle.update(target_y)

        # Paleta derecha (controlada por IA en modo 1 jugador, por msgr en modo 2 jugadores)
        if self.game_mode == 1:  # Modo un jugador (IA)
            # La IA sigue la pelota con un ligero retraso
            if self.ball.speed_x > 0:  # Solo mover cuando la pelota va hacia la derecha
                target_y = self.ball.y - self.right_paddle.height // 2 + random.randint(-30, 30)
                self.right_paddle.update(target_y)
        else:  # Modo dos jugadores
            if self.amplitud_right > 40:  # Umbral para detectar sonido
                target_y = map_range(self.pitch_right, self.pitch_min, self.pitch_max,
                                     self.screen_height - self.right_paddle.height, 0)
                self.right_paddle.update(target_y)

        # Mantener las paletas dentro de los límites de la pantalla
        self.left_paddle.keep_in_bounds(self.screen_height)
        self.right_paddle.keep_in_bounds(self.screen_height)

    def update_game(self):
        """Actualiza todos los elementos del juego"""
        # Actualizar posiciones de las paletas
        self.update_paddle_positions()

        # Actualizar posición de la pelota
        self.ball.update()

        # Verificar colisiones
        self.ball.check_ceiling_floor_collision(self.screen_height, self.create_particles)
        self.ball.check_paddle_collision(self.left_paddle, self.right_paddle, self.create_particles)

        # Limitar velocidad de la pelota
        self.ball.limit_speed()

        # Verificar si hay punto
        goal = self.ball.check_goal(self.screen_width)
        if goal == 1:  # Punto para jugador derecho
            self.score_right += 1
            self.ball.reset(self.screen_width, self.screen_height)
        elif goal == -1:  # Punto para jugador izquierdo
            self.score_left += 1
            self.ball.reset(self.screen_width, self.screen_height)

    def draw(self):
        """Dibuja todos los elementos del juego"""
        # Fondo negro
        self.screen.fill((0, 0, 0))
        self.surface.fill((0, 0, 0, 0))  # Superficie para efectos con transparencia

        # Línea central punteada
        for y in range(0, self.screen_height, 20):
            pygame.draw.rect(self.screen, (50, 50, 50), (self.screen_width // 2 - 5, y, 10, 10))

        # Dibujar paletas
        self.left_paddle.draw(self.screen)
        self.right_paddle.draw(self.screen)

        # Dibujar pelota
        self.ball.draw(self.screen)

        # Dibujar partículas
        self.particle_system.update_and_draw(self.surface)

        # Dibujar puntuaciones
        draw_text(str(self.score_left), self.font, self.text_c, self.screen_width // 4, 50, self.screen)
        draw_text(str(self.score_right), self.font, self.text_c, 3 * self.screen_width // 4, 50, self.screen)

        # Dibujar indicadores de pitch (visualización del sonido)
        if self.amplitud_left > 40:
            indicator_height = map_range(self.pitch_left, self.pitch_min, self.pitch_max, self.screen_height - 20, 20)
            pygame.draw.circle(self.surface, (100, 100, 255, 128), (40, indicator_height), 20)

        if self.game_mode == 2 and self.amplitud_right > 40:
            indicator_height = map_range(self.pitch_right, self.pitch_min, self.pitch_max, self.screen_height - 20, 20)
            pygame.draw.circle(self.surface, (255, 100, 100, 128), (self.screen_width - 40, indicator_height), 20)

        # Mostrar el rango de pitch configurado
        pitch_text = self.font.render(f"Rango de Pitch: {self.pitch_min} - {self.pitch_max}", True, self.text_c)
        self.screen.blit(pitch_text, (self.screen_width // 2 - pitch_text.get_width() // 2, 10))

        # Aplicar la superficie con transparencia
        self.screen.blit(self.surface, (0, 0))

    def check_game_over(self):
        """Verifica si hay un ganador (10 puntos)"""
        if self.score_left >= 10:
            self.game_over = 1  # Victoria del jugador izquierdo
            return True
        elif self.score_right >= 10:
            self.game_over = -1  # Victoria del jugador derecho
            return True
        return False

    def handle_events(self):
        """Maneja los eventos de pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                stop_osc()
                if self.state_callback:
                    self.state_callback(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.run = False
                    stop_osc()
                    if self.state_callback:
                        self.state_callback(0)

                # Controles de depuración (para pruebas)
                if event.key == pygame.K_SPACE and (self.game_over != 0 or not self.run):
                    self.reset()
                    self.run = True
                    self.game_over = 0

    def reset(self):
        """Reinicia el juego"""
        self.score_left = 0
        self.score_right = 0
        self.ball.reset(self.screen_width, self.screen_height)
        self.game_over = 0
        self.run = True

    def play(self):
        """Función principal del juego"""
        self.reset()

        # Iniciar comunicación OSC
        iniciar_osc()
        self.active_com = 1

        while self.run:
            self.clock.tick(self.fps)

            # Obtener datos de pitch
            mensaje_left = get_msgL()
            self.amplitud_left = mensaje_left[1]
            if self.amplitud_left > 40:
                self.pitch_left = mensaje_left[0]
                self.last_pitch_left = self.pitch_left

            if self.game_mode == 2:  # Solo obtener datos del segundo jugador en modo 2 jugadores
                mensaje_right = get_msgR()
                self.amplitud_right = mensaje_right[1]
                if self.amplitud_right > 40:
                    self.pitch_right = mensaje_right[0]
                    self.last_pitch_right = self.pitch_right

            # Actualizar estado del juego
            self.update_game()

            # Dibujar todo
            self.draw()

            # Verificar fin del juego
            if self.check_game_over():
                if self.game_over == 1:
                    draw_text('¡JUGADOR IZQUIERDO GANA!', self.font, self.text_c, 
                             self.screen_width // 2, self.screen_height // 2, self.screen)
                else:
                    draw_text('¡JUGADOR DERECHO GANA!', self.font, self.text_c, 
                             self.screen_width // 2, self.screen_height // 2, self.screen)

                draw_text('Presiona ESPACIO para jugar de nuevo', self.font, self.text_c, 
                         self.screen_width // 2, self.screen_height // 2 + 50, self.screen)

            # Manejar eventos
            self.handle_events()

            pygame.display.update()

        # Detener comunicación OSC al salir
        if self.active_com == 1:
            stop_osc()
            self.active_com = 0

# Función auxiliar para mapear rangos
def map_range(value, in_min, in_max, out_min, out_max):
    """Mapea un valor de un rango a otro"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min