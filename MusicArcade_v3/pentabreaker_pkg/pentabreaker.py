
import pygame
import pygame.freetype

from pentabreaker_pkg.disparador import Disparador
from pentabreaker_pkg.nota import NotaDisparada, ParticulaImpacto, actualizar_particulas
from pentabreaker_pkg.pentagrama import Pentagrama

from utils import *
from COM.COM_Pd import *
from Musica_IA.music_funcs import *

# Configuración de teclas para probar disparos manualmente según la clave
TECLA_NOTAS_POR_CLAVE = {
    "sol": {  # Clave de Sol
        pygame.K_c: 60,  # Do (C4)
        pygame.K_d: 62,  # Re (D4)
        pygame.K_e: 64,  # Mi (E4)
        pygame.K_f: 65,  # Fa (F4)
        pygame.K_g: 67,  # Sol (G4)
        pygame.K_a: 69,  # La (A4)
        pygame.K_b: 71,  # Si (B4)
        pygame.K_h: 72   # Do (C5) - Usando 'h' para otro Do
    },
    "do": {   # Clave de Do
        pygame.K_c: 60,  # Do (C4)
        pygame.K_d: 62,  # Re (D4)
        pygame.K_e: 64,  # Mi (E4)
        pygame.K_f: 65,  # Fa (F4)
        pygame.K_g: 67,  # Sol (G4)
        pygame.K_a: 57,  # La (A3)
        pygame.K_b: 59   # Si (B3)
    },
    "fa": {   # Clave de Fa
        pygame.K_c: 48,  # Do (C3)
        pygame.K_d: 50,  # Re (D3)
        pygame.K_e: 52,  # Mi (E3)
        pygame.K_f: 53,  # Fa (F3)
        pygame.K_g: 55,  # Sol (G3)
        pygame.K_a: 57,  # La (A3)
        pygame.K_b: 59,  # Si (B3)
        pygame.K_h: 60   # Do (C4) - Usando 'h' para otro Do
    }
}

class PentaBreaker:
    def __init__(self, screen, surface, screen_width, screen_height, state_callback=None, tipo_clave="do"):
        pygame.init()
        self.screen = screen
        self.surface = surface
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.bg_color = (0, 0, 0)
        self.font = pygame.font.SysFont('Constantia', 20)
        self.text_c = (255, 255, 255)
        self.notas_progresivas = [60, 62, 64, 65, 67]
        self.tipo_clave = tipo_clave  # Tipo de clave (sol, do, fa)

        # Establecer las notas progresivas según la clave
        from pentabreaker_pkg.pentagrama import NOTAS_POR_CLAVE
        self.notas_progresivas = NOTAS_POR_CLAVE[tipo_clave]
        
        # Variables del juego
        self.puntuacion = 0  # Sistema de puntuación
        self.nivel = 1  # Nivel actual del juego
        self.vidas = 3  # Número de vidas del jugador
        self.game_over = False  # Estado de game over
        self.indice_secuencia = 0  # Para controlar la secuencia correcta
        self.notas_en_proceso = []  # Notas que están en animación hasta la colisión
        self.particulas = []  # Lista de partículas de impacto

        # Inicializar objetos de juego
        self.pentagrama = Pentagrama(screen_width, screen_height, tipo_clave)
        self.disparador = Disparador(screen_width, screen_height, self.notas_progresivas)
        self.notas_disparadas = []

        # Variables de estado del juego
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        self.state_callback = state_callback
        self.mostrando_menu_claves = False  # Para mostrar menú de selección de claves

        # Variables musica
        self.pitch = 0
        self.last_pitch = 0
        self.amplitud = 0
        self.active_com = 0

    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                print(f"Key pressed: {pygame.key.name(event.key)}")
                # Si es game over, permitir reiniciar con la tecla espacio
                if self.game_over and event.key == pygame.K_SPACE:
                    self.reiniciar_juego()
                    return

                # Obtener mapeo de teclas según la clave actual
                teclas_clave_actual = TECLA_NOTAS_POR_CLAVE.get(self.tipo_clave, {})

                if event.key in teclas_clave_actual and not self.game_over:
                    nota_midi = teclas_clave_actual[event.key]
                    print(f"Note triggered: {nota_midi}")
                    self.notas_disparadas.append(NotaDisparada(nota_midi, self.screen_width//2, self.screen_height - 50))
                    
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                    print("Game exiting...")

        # Solo procesar disparador si no es game over
        if not self.game_over:
            # Guardamos el estado anterior
            disparo_previo = self.disparador.disparo_realizado
            # Procesamos el nuevo pitch
            self.disparador.disparo_pitch(self.pitch)
            # Solo crear nueva nota si el disparo acaba de ocurrir
            if self.disparador.disparo_realizado and not disparo_previo:
                self.notas_disparadas.append(NotaDisparada(self.disparador.pitch_detectado, self.screen_width//2, self.screen_height - 50))

    def reiniciar_juego(self):
        """Reinicia las variables del juego para empezar de nuevo"""
        self.puntuacion = 0
        self.nivel = 1
        self.vidas = 3
        self.game_over = False
        self.indice_secuencia = 0
        self.notas_en_proceso = []
        self.particulas = []
        self.notas_disparadas = []
        # Establecer las notas progresivas según la clave seleccionada
        from pentabreaker_pkg.pentagrama import NOTAS_POR_CLAVE
        self.notas_progresivas = NOTAS_POR_CLAVE[self.tipo_clave]
        # Mantener la misma clave que se seleccionó
        self.pentagrama.tipo_clave = self.tipo_clave
        self.pentagrama.velocidad = 0.5
        self.pentagrama.notas_disponibles = self.notas_progresivas
        self.pentagrama.generar_nuevo_pentagrama()

    def actualizar(self):
        # Inicio hilo msg (pitch, amplitud)
        if self.active_com == 0:
            # Recibir msg voz
            iniciar_osc()
            time.sleep(0.1)
            self.active_com = 1

        # Control de pitch/amplitud
        mensaje = get_msgL()
        self.amplitud = mensaje[1]
        if self.amplitud > 40:
            self.pitch = mensaje[0]
            self.last_pitch = self.pitch
        elif self.pitch >= 0:
            self.pitch -= 40

        # Actualizar pentagrama y verificar si llegó al disparador
        if not self.pentagrama.actualizar():
            self.vidas -= 1
            print(f"¡Perdiste una vida! Vidas restantes: {self.vidas}")

            # Verificar si el juego ha terminado
            if self.vidas <= 0:
                self.game_over = True
                # Dejo de recibir msg
                stop_osc()
                self.active_com = 0
                print("¡GAME OVER!")
                return

            # Generar nuevo pentagrama si aún hay vidas
            self.pentagrama.generar_nuevo_pentagrama()
            self.indice_secuencia = 0
        nuevas_notas_disparadas = []
        notas_colisionadas = []

        for nota in self.notas_disparadas:
            nota.mover()
            if nota.y > 0:  # Mantener solo notas visibles
                if self.indice_secuencia < len(self.pentagrama.notas):
                    nota_esperada = self.pentagrama.notas[self.indice_secuencia]
                    if nota.pitch == nota_esperada.midi and nota.y <= nota_esperada.y:
                        self.pentagrama.notas[self.indice_secuencia].impactado = True
                        notas_colisionadas.append(nota)
                        self.indice_secuencia += 1
                        self.notas_en_proceso.append(nota)
                        for _ in range(10):  # Crear 10 partículas por impacto
                            self.particulas.append(ParticulaImpacto(nota.x, nota.y))
    
                        if self.indice_secuencia == len(self.pentagrama.notas):
                            self.puntuacion += 10
                            print(f"Puntuación: {self.puntuacion}")
                            # Subir de nivel cada 5 pentagramas completados
                            if self.puntuacion >= self.nivel * 50:
                                self.nivel += 1
                                self.pentagrama.velocidad = min(3.0, 0.5 + (self.nivel * 0.25))  # Aumenta velocidad con límite
                                print(f"¡Subiste al nivel {self.nivel}!")
                            self.pentagrama.generar_nuevo_pentagrama()
                            self.indice_secuencia = 0
                            self.notas_en_proceso = []

                if nota not in notas_colisionadas:
                    nuevas_notas_disparadas.append(nota)

        self.notas_disparadas = nuevas_notas_disparadas
        actualizar_particulas(self.particulas)

    def dibujar(self):
        self.screen.fill(self.bg_color)

        # Mostrar pantalla de game over
        if self.game_over:
            game_over_texto = self.font.render("¡GAME OVER!", True, (255, 0, 0))
            puntuacion_final = self.font.render(f"Puntuación final: {self.puntuacion}", True, self.text_c)
            nivel_final = self.font.render(f"Nivel alcanzado: {self.nivel}", True, self.text_c)
            reiniciar_texto = self.font.render("Presiona ESPACIO para reiniciar", True, self.text_c)

            self.screen.blit(game_over_texto, (self.screen_width//2 - game_over_texto.get_width()//2, self.screen_height//2 - 100))
            self.screen.blit(puntuacion_final, (self.screen_width//2 - puntuacion_final.get_width()//2, self.screen_height//2 - 40))
            self.screen.blit(nivel_final, (self.screen_width//2 - nivel_final.get_width()//2, self.screen_height//2))
            self.screen.blit(reiniciar_texto, (self.screen_width//2 - reiniciar_texto.get_width()//2, self.screen_height//2 + 60))
        else:
            # Determinar si se deben mostrar los nombres de las notas (solo en nivel 1)
            mostrar_nombres = (self.nivel == 1)

            # Dibujar elementos del juego normal
            self.pentagrama.dibujar(self.screen, mostrar_nombres)
            self.disparador.dibujar(self.screen)
            for nota in self.notas_disparadas:
                nota.dibujar(self.screen)
            for particula in self.particulas:
                particula.dibujar(self.screen)

            # Mostrar información del juego
            puntuacion_texto = self.font.render(f"Puntuación: {self.puntuacion}", True, self.text_c)
            nivel_texto = self.font.render(f"Nivel: {self.nivel}", True, self.text_c)
            vidas_texto = self.font.render(f"Vidas: {self.vidas}", True, self.text_c)

            self.screen.blit(puntuacion_texto, (20, 20))
            self.screen.blit(nivel_texto, (20, 60))
            self.screen.blit(vidas_texto, (20, 100))

            # Mostrar mensaje informativo en nivel 1
            if mostrar_nombres:
                ayuda_texto = self.font.render("Nivel 1: Aprende las notas", True, (255, 255, 0))
                self.screen.blit(ayuda_texto, (self.screen_width//2 - ayuda_texto.get_width()//2, 20))
            
        pygame.display.flip()

    def ejecutar(self):
        while self.running:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.clock.tick(self.fps)

        if self.state_callback:
            self.state_callback(0)  # Volver al menú si el juego termina

def mostrar_menu_seleccion_clave(screen, screen_width, screen_height):
    """Muestra un menú para seleccionar el tipo de clave"""
    from pentagrama import CLAVE_DO, CLAVE_FA, CLAVE_SOL

    pygame.freetype.init()  # Asegurarse de que freetype esté inicializado
    font = pygame.font.SysFont('Constantia', 30)
    font_titulo = pygame.font.SysFont('Constantia', 40)

    screen.fill((0, 0, 0))

    titulo = font_titulo.render("Selecciona el tipo de clave", True, (255, 255, 0))
    screen.blit(titulo, (screen_width//2 - titulo.get_width()//2, 100))

    # Dibujar opciones de clave
    opciones = [
        {"texto": "Clave de Sol (G)", "imagen": "clave_sol.png", "clave": CLAVE_SOL, "y": 250},
        {"texto": "Clave de Do (C)", "imagen": "clave_do.png", "clave": CLAVE_DO, "y": 350},
        {"texto": "Clave de Fa (F)", "imagen": "clave_fa.png", "clave": CLAVE_FA, "y": 450}
    ]

    mouse_pos = pygame.mouse.get_pos()

    for opcion in opciones:
        # Rectángulo para la opción
        rect = pygame.Rect(screen_width//2 - 250, opcion["y"], 500, 60)

        # Verificar si el mouse está sobre esta opción
        hover = rect.collidepoint(mouse_pos)
        color_rect = (50, 50, 80) if hover else (30, 30, 50)

        # Dibujar rectángulo de fondo
        pygame.draw.rect(screen, color_rect, rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 150), rect, 2, border_radius=5)

        # Dibujar texto de la opción
        texto = font.render(opcion["texto"], True, (255, 255, 255))
        screen.blit(texto, (rect.x + 20, rect.y + 15))

        # Dibujar claves
        imagen = pygame.image.load(opcion["imagen"])
        imagen = pygame.transform.scale(imagen, (50, 50))
        imagen_rect = imagen.get_rect(center=(screen_width // 2 + 200, opcion["y"] + 30))
        screen.blit(imagen, imagen_rect)

    pygame.display.flip()

    return opciones