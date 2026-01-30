import pygame
import time
import math


class Disparador:
    def __init__(self, screen_width, screen_height, notas_progresivas):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pitch_detectado = None
        self.manteniendo_nota = False
        self.tiempo_inicio_nota = None
        self.onda_activa = False
        self.disparo_realizado = False
        self.notas_progresivas = notas_progresivas
        self.last_pitch = 0
        self.tiempo_inicio = 0
        self.banda_error = 0.4
        self.tiempo_umbral = 0.1
        self.tiempo_espera_disparo = 0.5  # Tiempo mínimo entre disparos consecutivos
        self.ultimo_disparo = 0  # Momento del último disparo
        self.color = (255, 255, 255)
        self.line_y = screen_height - 50

    def disparo_pitch(self, pitch):
        self.pitch_detectado = pitch
        tiempo_actual = time.time()
        if pitch is None:
            self.manteniendo_nota = False
            self.onda_activa = False
            self.disparo_realizado = False
            return

        # Comprobar si ha pasado suficiente tiempo desde el último disparo
        tiempo_desde_ultimo_disparo = tiempo_actual - self.ultimo_disparo
        puede_disparar_repetido = tiempo_desde_ultimo_disparo > self.tiempo_espera_disparo

        for note_value in self.notas_progresivas:
            if note_value - self.banda_error < pitch < note_value + self.banda_error:
                if self.last_pitch == note_value:
                    # Permitir disparo si ha pasado el tiempo umbral Y
                    if tiempo_actual - self.tiempo_inicio > self.tiempo_umbral and (not self.disparo_realizado or puede_disparar_repetido):
                        self.onda_activa = True
                        self.disparo_realizado = True
                        self.pitch_detectado = note_value  # Confirma la nota
                        self.ultimo_disparo = tiempo_actual  # Actualizar el tiempo del último disparo
                        print("Nota detectada: ")
                        print(self.pitch_detectado)
                else:
                    self.last_pitch = note_value
                    self.tiempo_inicio = tiempo_actual
                break
            else:
                self.manteniendo_nota = False
                self.onda_activa = False
                # Solo reset cuando cambia significativamente la nota
                if abs(pitch - self.last_pitch) > 1:
                    self.disparo_realizado = False
                    print("RESET")

    def generar_onda(self, pitch, t):
        frecuencia = pitch * 10  # Escalar frecuencia para la onda visual
        return math.sin(2 * math.pi * frecuencia * t) * 10

    def dibujar(self, screen):
        if self.onda_activa:
            for x in range(self.screen_width):
                y_offset = self.generar_onda(self.pitch_detectado, x / self.screen_width)
                pygame.draw.circle(screen, self.color, (x, self.line_y + int(y_offset)), 1)
        else:
            pygame.draw.line(screen, self.color, (0, self.line_y), (self.screen_width, self.line_y), 3)