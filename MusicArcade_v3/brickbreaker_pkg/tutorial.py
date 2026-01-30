# tutorial.py
import pygame
import random
import threading
from particulas import Particula
from brickbreaker_pkg.paddle import paddle
from brickbreaker_pkg.ball import game_ball
from brickbreaker_pkg.wall import wall
from utils import *
from COM.COM_Pd import *
from Musica_IA.music_funcs import *

class Tutorial:
    def __init__(self, screen, surface, screen_width, screen_height, state_callback=None):
        self.screen = screen
        self.surface = surface
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.bg_color = (0, 0, 0)
        self.font = pygame.font.SysFont('Constantia', 30)
        self.text_c = (78, 81, 139)

        # Inicializar objetos de juego
        self.wall = wall(screen_width, 3)
        self.ball = game_ball(screen_width // 2, screen_height // 2 + 200)
        self.paddle = paddle(screen_width, screen_height, ["C3", "D3", "E3", "F3"], [48, 50, 52, 53], self.ball)
        self.live_ball = False

        # Variable del juego
        self.cols = 3
        self.rows = 7
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.run = True
        self.live_ball = False
        self.tutorial_step = 0
        self.tutorial_sound = 1
        self.state_callback = state_callback

        # Variables para secciones de la pala
        self.scale_notes = ['C3', 'D3', 'E3', 'F3', 'G3', 'A3', 'B3', 'C4']
        self.notas_progresivas = [48, 50, 52, 53, 55, 57, 59, 60]  # Notas que se agregarán progresivamente
        self.notas_colisionadas = []
        self.tiempo_transcurrido = 0
        self.tiempo_agregar_seccion = 5000  # Tiempo en milisegundos (ejemplo: 5000ms = 5 segundos)

        # Variables musica
        self.pitch = 0
        self.last_pitch = 0
        self.amplitud = 0
        self.active_com = 0
        self.flag_setup = 0
        self.tempo_deseado = 80

        # Crear objetos del juego
        self.tutorial_wall = wall(self.screen_width, self.cols)
        self.tutorial_wall.create_wall_tutorial(self.rows, self.cols, self.scale_notes)
        self.ball = game_ball(self.screen_width // 2, self.screen_height // 2 + 200)
        self.paddle = paddle(self.screen_width, self.screen_height, self.scale_notes, self.notas_progresivas, self.ball)
        # Crear partículas
        self.NUM_PARTICULAS = 750
        self.particulas = [Particula(random.randint(0, self.screen_width), random.randint(0, self.screen_height)) for _
                           in range(self.NUM_PARTICULAS)]

    def reset(self):
        self.tutorial_step = 0
        self.active_com = 0
        self.ball.reset(self.paddle.x + (self.paddle.width // 2), self.paddle.y - self.paddle.height)
        self.paddle.reset(self.screen_width, self.screen_height, self.notas_progresivas)
        self.tutorial_wall.create_wall(self.rows, self.cols, self.scale_notes)
        self.run = True

    def play(self):
        while self.run:
            self.clock.tick(self.fps)
            self.screen.fill((0, 0, 0))  # (234, 218, 184))
            tiempo_actual = pygame.time.get_ticks()
            self.surface.fill((0, 0, 0, 0))  # Limpia con transparencia
            # Dibujar en surface
            for particula in self.particulas:
                particula.dibujar(self.surface, tiempo_actual)
                particula.mover(self.ball, self.screen_width, self.screen_height)
            # Dibujar pala
            self.paddle.draw(self.surface, self.pitch)
            # Updatear la pantalla surface
            self.screen.blit(self.surface, (0, 0))
            # Dibujar en screen
            self.paddle.draw_section_notes(self.screen)
            self.tutorial_wall.draw_wall(self.screen, self.bg_color)
            self.ball.draw(self.screen)

            # Inicio hilos msg y acordes
            if self.active_com == 0:
                # Recibir msg voz
                iniciar_osc()
                time.sleep(0.2)
                self.active_com = 1

            # Control de pitch/amplitud
            self.amplitud = msgL[1]
            if self.amplitud > 40:
                self.pitch = msgL[0]
                self.last_pitch = self.pitch
            else:
                self.pitch -= 10

            if self.tutorial_step//2 == 0:
                self.ball.reset(self.paddle.x + (self.paddle.width // 2), self.paddle.y - self.paddle.height)
                self.paddle.reset(self.screen_width, self.screen_height, self.notas_progresivas)
                # Definir las medidas del rectángulo
                rect = (self.screen_width//2 - 200, self.screen_height//2, 400, 120)
                # Texto a mostrar
                text = "Bienvenido al tutorial de MusicArcade! A continuación te acompañare en una pequeña demo del juego. Prepara tu instrumento y presta atención a las instrucciones!"
                # Dibujar el rectángulo con el texto
                draw_multiline_text_in_rect(self.screen, text, rect)
            elif self.tutorial_step // 2 == 1:
                # Definir las medidas del rectángulo
                rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 120)
                # Texto a mostrar
                text = "Si has jugado juegos de arcade alguna vez te sonara el Brick Breaker. Esto es practicamente lo mismo, salvo que controlamos la pala con música!"
                # Dibujar el rectángulo con el texto
                draw_multiline_text_in_rect(self.screen, text, rect)
            elif self.tutorial_step // 2 == 2:
                # Definir las medidas del rectángulo
                rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 80)
                # Texto a mostrar
                text = "Empecemos a jugar y te ire explicando poco a poco como funciona :)"
                # Dibujar el rectángulo con el texto
                draw_multiline_text_in_rect(self.screen, text, rect)
            elif self.tutorial_step // 2 == 3:
                if self.ball.speed_y > 0:
                    self.tutorial_step += 2
                # Mover bola
                self.game_over, nota = self.ball.move(self.screen_height, self.screen_width, self.tutorial_wall, self.paddle, self.notas_colisionadas)
            elif self.tutorial_step // 2 == 4:
                # Definir las medidas del rectángulo
                rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 120)
                # Texto a mostrar
                text = "Cuando la pelota choca contra los ladrillos, estos se rompen. El objetivo del juego es conseguir destruir toda la pared."
                # Dibujar el rectángulo con el texto
                draw_multiline_text_in_rect(self.screen, text, rect)
            elif self.tutorial_step // 2 == 5:
                # Mover bola
                self.game_over, nota = self.ball.move(self.screen_height, self.screen_width, self.tutorial_wall, self.paddle, self.notas_colisionadas)
                print(self.ball.rect.y)
                if self.ball.rect.y > 600:
                    self.tutorial_step += 2
            elif self.tutorial_step // 2 == 6:
                # Definir las medidas del rectángulo
                rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 120)
                # Texto a mostrar
                text = "Ahora es cuando entras tu! Como puedes ver abajo de la pala hay una nota."
                # Dibujar el rectángulo con el texto
                draw_multiline_text_in_rect(self.screen, text, rect)
            elif self.tutorial_step // 2 == 7:
                # Definir las medidas del rectángulo
                rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 120)
                # Texto a mostrar
                text = "En este caso, la nota que debes cantar o tocar es C3 o Do de la tercera octava. Escuchemos como suena..."
                # Dibujar el rectángulo con el texto
                draw_multiline_text_in_rect(self.screen, text, rect)
                if self.tutorial_sound != 0:
                    t_tutorial = threading.Thread(target=notas_tutorial, daemon=True, args=(self.tempo_deseado, self.paddle.section_notes[-1], 3,))
                    t_tutorial.start()

                    self.tutorial_sound = 0
            elif self.tutorial_step // 2 == 8:
                # Definir las medidas del rectángulo
                rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 120)
                # Texto a mostrar
                text = "Canta o toca esta nota con tu instrumento para que la pala aparezca y pare la pelota!"
                # Dibujar el rectángulo con el texto
                draw_multiline_text_in_rect(self.screen, text, rect)
                # Reconocer nota correcta
                if 47.5 < self.pitch < 48.5:
                    self.tutorial_step += 2
            elif self.tutorial_step // 2 == 9:
                # Mover bola
                self.game_over, nota = self.ball.move(self.screen_height, self.screen_width, self.tutorial_wall, self.paddle, self.notas_colisionadas)
                if self.game_over != 0:
                    # Definir las medidas del rectángulo
                    rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 120)
                    # Texto a mostrar
                    text = "Se te ha ido la pelota! Normalmente tendrias que empezar otra vez... Pero bueno como estamos practicando te lo perdono :). Apreta 'R' para resetear la pelota"
                    # Dibujar el rectángulo con el texto
                    draw_multiline_text_in_rect(self.screen, text, rect)
                if self.ball.rect.y < self.paddle.y - 100:
                    self.tutorial_step += 2
            elif self.tutorial_step // 2 == 10:
                # Definir las medidas del rectángulo
                rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 120)
                # Texto a mostrar
                text = "Muy bien! Sigue jugando y volveré cuando aparezca algo nuevo!"
                # Dibujar el rectángulo con el texto
                draw_multiline_text_in_rect(self.screen, text, rect)
            elif self.tutorial_step // 2 == 11:
                # Mover bola
                self.game_over, nota = self.ball.move(self.screen_height, self.screen_width, self.tutorial_wall, self.paddle, self.notas_colisionadas)
                if self.game_over != 0:
                    # Definir las medidas del rectángulo
                    rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 120)
                    # Texto a mostrar
                    text = "Se te ha ido la pelota! Normalmente tendrias que empezar otra vez... Pero bueno como estamos practicando te lo perdono :). Apreta 'R' para resetear la pelota"
                    # Dibujar el rectángulo con el texto
                    draw_multiline_text_in_rect(self.screen, text, rect)
                if len(self.paddle.section_notes) != len(self.paddle.previous_section_notes):
                    self.tutorial_step += 2
                    self.paddle.previous_section_notes = self.paddle.section_notes
            elif self.tutorial_step // 2 == 12:
                # Definir las medidas del rectángulo
                rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 120)
                # Texto a mostrar
                text = "Acabas de romper un ladrillo con una nota en su interior! Esto quiere decir que la pala se dividira en dos segmentos y controlaremos cada uno cantando la nota correspondiente."
                # Dibujar el rectángulo con el texto
                draw_multiline_text_in_rect(self.screen, text, rect)
            elif self.tutorial_step // 2 == 13:
                # Definir las medidas del rectángulo
                rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 120)
                # Texto a mostrar
                text = "Toca la nota correspondiente al ladrillo que acabas de romper para que aparezca su segmento y puedas parar la pelota!"
                # Dibujar el rectángulo con el texto
                draw_multiline_text_in_rect(self.screen, text, rect)
            elif self.tutorial_step // 2 == 14:
                # Mover bola
                self.game_over, nota = self.ball.move(self.screen_height, self.screen_width, self.tutorial_wall, self.paddle, self.notas_colisionadas)
                print(self.ball.rect.y)
                if self.ball.speed_y < 0 and self.ball.rect.y > 600:
                    self.tutorial_step += 2
            elif self.tutorial_step // 2 == 15:
                # Definir las medidas del rectángulo
                rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 120)
                # Texto a mostrar
                text = "Muy bien! Ya entiendes las bases del juego. Como puedes ver es bastante facil! Sigue jugando y destuye todos los ladrillos para ganar!"
                # Dibujar el rectángulo con el texto
                draw_multiline_text_in_rect(self.screen, text, rect)
            elif self.tutorial_step // 2 == 16:
                # Mover bola
                self.game_over, nota = self.ball.move(self.screen_height, self.screen_width, self.tutorial_wall, self.paddle, self.notas_colisionadas)
                if self.game_over != 0:
                    # Definir las medidas del rectángulo
                    rect = (self.screen_width // 2 - 200, self.screen_height // 2, 400, 120)
                    # Texto a mostrar
                    text = "Se te ha ido la pelota! Normalmente tendrias que empezar otra vez... Pero bueno como estamos practicando te lo perdono :). Apreta 'R' para resetear la pelota"
                    # Dibujar el rectángulo con el texto
                    draw_multiline_text_in_rect(self.screen, text, rect)

            # Manejar eventos del teclado
            for event in pygame.event.get():
                self.handle_events(event)

            pygame.display.update()

    def handle_events(self, event):
        key = pygame.key.get_pressed()
        """Maneja los eventos del tutorial."""
        if event.type == pygame.QUIT:
            self.run = False
            stop_osc()

        if key[pygame.K_ESCAPE]:  # El jugador presiona ESC para volver al menú
            self.state_callback = 0
            self.run = False
        if key[pygame.K_SPACE]:
            self.tutorial_step += 1  # Cambiar al estado de juego
        if key[pygame.K_r]:
            self.ball.reset(self.paddle.x + (self.paddle.width // 2), self.paddle.y - self.paddle.height)
        pass
