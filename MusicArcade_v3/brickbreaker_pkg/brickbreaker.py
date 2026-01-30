from utils import *
from COM.COM_Pd import *
from Musica_IA.music_funcs import *
from particulas import Particula
from brickbreaker_pkg.paddle import paddle
from brickbreaker_pkg.ball import game_ball
from brickbreaker_pkg.wall import wall


class BrickBreaker:
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
        self.game_over = 0
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
        self.wall = wall(self.screen_width, self.cols)
        self.wall.create_wall(self.rows, self.cols, self.scale_notes)
        self.ball = game_ball(self.screen_width // 2, self.screen_height // 2 + 200)
        self.paddle = paddle(self.screen_width, self.screen_height, self.scale_notes, self.notas_progresivas, self.ball)
        # Crear partículas
        self.NUM_PARTICULAS = 750
        self.particulas = [Particula(random.randint(0, self.screen_width), random.randint(0, self.screen_height)) for _
                           in range(self.NUM_PARTICULAS)]

    def reset(self):
        # Resetear pared
        self.wall.create_wall(self.rows, self.cols, self.scale_notes)
        self.paddle = paddle(self.screen_width, self.screen_height, self.scale_notes, self.notas_progresivas, self.ball)
        self.run = True

    def play(self):
        while self.run:
            self.clock.tick(self.fps)
            self.screen.fill((0, 0, 0))
            self.surface.fill((0, 0, 0, 0))  # Limpia con transparencia
            tiempo_actual = pygame.time.get_ticks()
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
            self.wall.draw_wall(self.screen, self.bg_color)
            self.ball.draw(self.screen)
            # Si la pelota esta en movimiento
            if self.live_ball:
                draw_arrow_indication(self.last_pitch, self.amplitud, self.paddle, self.screen_height,
                                      self.screen_width, self.screen)
                # Inicio hilos msg y acordes
                if self.active_com == 0:
                    # Recibir msg voz
                    iniciar_osc()
                    time.sleep(0.1)
                    # Limpio eventos de stop
                    stop_chords.clear()
                    stop_mel.clear()
                    # Inicio reproduccion de acordes
                    gen_acordes_ia_paralelo(sg, self.notas_progresivas[0], 11)
                    gen_melodia_ia_paralelo(mg, self.notas_progresivas[0])
                    print(acordes)
                    # Inicializar sincronización
                    iniciar_sincronizacion(self.tempo_deseado, stop_mel)
                    # Iniciar musica
                    iniciar_acordes_en_paralelo(self.tempo_deseado, start_chords, stop_chords)
                    iniciar_melodia_en_paralelo(self.tempo_deseado, start_mel, stop_mel)
                    start_chords.set()
                    start_mel.set()
                    # Levanto bandera inicio
                    self.active_com = 1

                # Control logica melodia
                # logic_gen_mel(mg, self.pitch, self.notas_progresivas)

                # Control de pitch/amplitud
                mensaje = get_msgL()
                self.amplitud = mensaje[1]
                if self.amplitud > 40:
                    self.pitch = mensaje[0]
                    self.last_pitch = self.pitch
                else:
                    self.pitch -= 10
                # Dibujar bola
                self.game_over, nota = self.ball.move(self.screen_height, self.screen_width, self.wall, self.paddle,
                                                      self.notas_colisionadas)
                # Generar nueva semilla para la IA
                if nota != 0:
                    # Generar acordes
                    gen_acordes_ia_paralelo(sg, nota, 4)
                    gen_melodia_ia_paralelo(mg, nota)
                    print(acordes)
                # Pierdo
                if self.game_over != 0:
                    self.live_ball = False
                    # Parar musica
                    stop_chords.set()
                    stop_mel.set()
            # Si la pelota se para
            if not self.live_ball:
                if self.active_com == 1:
                    stop_osc()
                    self.active_com = 0
                    print(self.notas_colisionadas)
                if self.game_over == 0:
                    draw_text('PRESS SPACE TO START', self.font, self.text_c, self.screen_width // 2,
                              (self.screen_height // 2) + 100, self.screen)
                elif self.game_over == 1:
                    draw_text('YOU WON!', self.font, self.text_c, (self.screen_width // 2) - 90,
                              (self.screen_height // 2) + 50, self.screen)
                    draw_text('PRESS SPACE TO START', self.font, self.text_c, self.screen_width // 2 - 200,
                              (self.screen_height // 2) + 100, self.screen)
                elif self.game_over == -1:
                    draw_text('YOU LOST!', self.font, self.text_c, (self.screen_width // 2) - 80,
                              (self.screen_height // 2) + 50, self.screen)
                    draw_text('PRESS SPACE TO START', self.font, self.text_c, self.screen_width // 2 - 200,
                              (self.screen_height // 2) + 100, self.screen)

            # Manejar eventos del teclado
            for event in pygame.event.get():
                self.handle_events(event)

            pygame.display.update()

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            self.run = False
            stop_osc()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # El jugador presiona ESC para volver al menú
                self.state_callback(0)  # Cambiar al estado inicial del menú
                self.run = False
                # Parar osc
                stop_osc()
                # Parar musica
                stop_chords.set()
                stop_mel.set()
            if event.key == pygame.K_SPACE:
                self.live_ball = True  # Iniciar el juego
                self.ball.reset(self.paddle.x + (self.paddle.width // 2), self.paddle.y - self.paddle.height)
                self.paddle.reset(self.screen_width, self.screen_height, self.notas_progresivas)
                self.wall.create_wall(self.rows, self.cols, self.scale_notes)
                self.notas_colisionadas = []
            pass
