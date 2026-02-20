# game.py
from utils import *
from COM.COM_Pd import *
from brickbreaker_pkg.brickbreaker import BrickBreaker
from brickbreaker_pkg.tutorial import Tutorial
from brickbreaker_pkg.config import Config
from pentabreaker_pkg.pentabreaker import PentaBreaker
from pentabreaker_pkg.menu import MenuPentaBreaker
from musicpong_pkg.musicpong import MusicPong
from musicpong_pkg.menu import MenuMusicPong

class Game:
    def __init__(self):
        # Inicializar pygame
        pygame.init()
        self.screen_width = 1080
        self.screen_height = 780
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.bg_color = (0, 0, 0)  # (234, 218, 184)

        # Definir font
        self.font = pygame.font.SysFont('Constantia', 30)
        self.font2 = pygame.font.SysFont('Constantia', 20)
        self.font_title = pygame.font.SysFont('Constantia', 60)
        self.font_menu = pygame.font.SysFont('Constantia', 40)
        self.text_c = (78, 81, 139)
        self.hover_c = (128, 131, 189)  # Color para el hover

        pygame.display.set_caption('Music Arcade')

        # Estado del juego
        self.game_state = 0  # 0: menú principal
        self.submenu_state = 0
        self.running = True

        # Botones del menú principal
        self.main_menu_buttons = [
            {"text": "Note Breaker",
             "rect": pygame.Rect(self.screen_width // 2 - 150, self.screen_height // 2 + 100, 300, 60)},
            {"text": "Penta Breaker",
             "rect": pygame.Rect(self.screen_width // 2 - 150, self.screen_height // 2 + 200, 300, 60)},
            {"text": "Music Pong",
             "rect": pygame.Rect(self.screen_width // 2 - 150, self.screen_height // 2, 300, 60)}
        ]

        # Botones del submenú Note Breaker
        self.note_breaker_buttons = [
            {"text": "Jugar",
             "rect": pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 - 100, 200, 60)},
            {"text": "Tutorial", "rect": pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2, 200, 60)},
            {"text": "Configuración",
             "rect": pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 + 100, 200, 60)},
            {"text": "Volver",
             "rect": pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 + 200, 200, 60)}
        ]

        # Inicializar modos
        self.brick_breaker = BrickBreaker(self.screen, self.surface, self.screen_width, self.screen_height, self.change_game_state)
        self.tutorial = Tutorial(self.screen, self.surface, self.screen_width, self.screen_height, self.change_game_state)
        self.config = Config(self.screen, self.screen_width, self.screen_height)
        self.penta_menu = MenuPentaBreaker(self.screen, self.screen_width, self.screen_height, self.change_game_state)
        self.musicpong_menu = MenuMusicPong(self.screen, self.screen_width, self.screen_height, self.change_game_state)

        # Setup servidor com
        osc_setup()

    def change_game_state(self, new_state):
        self.game_state = new_state
        print(f"Estado del juego: {self.game_state}")

    def show_menu(self):
        """Muestra el menú principal en pantalla."""
        # Obtener posición del mouse
        mouse_pos = pygame.mouse.get_pos()

        # Dibujar botones del menú principal
        if self.game_state == 0:
            self.screen.fill((0, 0, 0))
            # Título principal
            draw_text('MUSIC ARCADE', self.font_title, self.text_c, self.screen_width // 2, self.screen_height // 4,
                      self.screen)
            for btn in self.main_menu_buttons:
                # Verificar si el mouse está sobre el botón
                if btn["rect"].collidepoint(mouse_pos):
                    color = self.hover_c
                else:
                    color = self.text_c

                # Dibujar el botón
                draw_text(btn["text"], self.font_menu, color,
                          btn["rect"].centerx,
                          btn["rect"].centery,
                          self.screen)

        # Dibujar botones del submenú Note Breaker
        elif self.game_state == 4:
            self.screen.fill((0, 0, 0))
            draw_text('NOTE BREAKER', self.font_title, self.text_c, self.screen_width // 2, self.screen_height // 4,
                      self.screen)

            for btn in self.note_breaker_buttons:
                # Verificar si el mouse está sobre el botón
                if btn["rect"].collidepoint(mouse_pos):
                    color = self.hover_c
                else:
                    color = self.text_c

                # Dibujar el botón
                draw_text(btn["text"], self.font_menu, color,
                          btn["rect"].centerx,
                          btn["rect"].centery,
                          self.screen)

        pygame.display.update()

    def handle_events(self, event):
        """Maneja los eventos del menú principal."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Verificar clicks en el menú principal
            if self.game_state == 0:
                for btn in self.main_menu_buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        if btn["text"] == "Note Breaker":
                            self.game_state = 4  # Cambiar al submenú de Note Breaker
                        elif btn["text"] == "Penta Breaker":
                            self.game_state = 5  # Cambiar al menú de Penta Breaker
                        elif btn["text"] == "Music Pong":
                            self.game_state = 6  # Cambiar al menu de Music Pong

            # Verificar clicks en el submenú Note Breaker
            elif self.game_state == 4:
                for btn in self.note_breaker_buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        if btn["text"] == "Jugar":
                            self.game_state = 1  # Cambiar al estado de juego
                        elif btn["text"] == "Tutorial":
                            self.game_state = 2  # Cambiar al estado de tutorial
                        elif btn["text"] == "Configuración":
                            self.game_state = 3  # Cambiar al estado de configuración
                        elif btn["text"] == "Volver":
                            self.game_state = 0  # Volver al menú principal
    def run(self):
        """Loop principal del juego."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.handle_events(event)

            if self.game_state == 0 or self.game_state == 4:
                self.show_menu()
            elif self.game_state == 1:
                self.brick_breaker.reset()
                self.brick_breaker.play()
            elif self.game_state == 2:
                self.tutorial.reset()
                self.tutorial.play()
            elif self.game_state == 3:
                self.config.run()
                # Al salir de la configuración, volver al submenú
                self.game_state = 4
            elif self.game_state == 5:
                # Ejecutar el menú de PentaBreaker
                tipo_clave = self.penta_menu.run()
                if tipo_clave:
                    # Iniciar PentaBreaker con la clave seleccionada
                    penta_game = PentaBreaker(self.screen, self.surface, self.screen_width, self.screen_height,
                                              self.change_game_state, tipo_clave)
                    penta_game.ejecutar()
                self.game_state = 0  # Volver al menú principal al salir
            elif self.game_state == 6:
                # Ejecutar el menú de MusicPong
                modo_juego = self.musicpong_menu.run()
                if modo_juego:
                    # Iniciar MusicPong con el modo seleccionado
                    pong_game = MusicPong(self.screen, self.surface, self.screen_width, self.screen_height,
                                          self.change_game_state, modo_juego)
                    pong_game.play()
                self.game_state = 0  # Volver al menú principal al salir

        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()