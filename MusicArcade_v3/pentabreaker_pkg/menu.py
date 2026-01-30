import pygame
import sys
import os

class MenuPentaBreaker:
    def __init__(self, screen, screen_width, screen_height, state_callback=None):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont('Constantia', 30)
        self.font_titulo = pygame.font.SysFont('Constantia', 40)
        self.text_c = (78, 81, 139)
        self.hover_c = (128, 131, 189)
        self.state_callback = state_callback
        self.running = True

    def mostrar_menu_seleccion_clave(self):
        """Muestra un menú para seleccionar el tipo de clave"""
        pygame.init()
        font = pygame.font.SysFont('Constantia', 30)
        font_titulo = pygame.font.SysFont('Constantia', 40)

        self.screen.fill((0, 0, 0))

        titulo = font_titulo.render("Selecciona el tipo de clave", True, (255, 255, 0))
        self.screen.blit(titulo, (self.screen_width//2 - titulo.get_width()//2, 100))

        # Dibujar opciones de clave
        opciones = [
            {"texto": "Clave de Sol (G)", "imagen": "pentabreaker_pkg/clave_sol.png", "clave": "sol", "y": 250},
            {"texto": "Clave de Do (C)", "imagen": "pentabreaker_pkg/clave_do.png", "clave": "do", "y": 350},
            {"texto": "Clave de Fa (F)", "imagen": "pentabreaker_pkg/clave_fa.png", "clave": "fa", "y": 450}
        ]

        mouse_pos = pygame.mouse.get_pos()

        for opcion in opciones:
            # Rectángulo para la opción
            rect = pygame.Rect(self.screen_width//2 - 250, opcion["y"], 500, 60)

            # Verificar si el mouse está sobre esta opción
            hover = rect.collidepoint(mouse_pos)
            color_rect = (50, 50, 80) if hover else (30, 30, 50)

            # Dibujar rectángulo de fondo
            pygame.draw.rect(self.screen, color_rect, rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 150), rect, 2, border_radius=5)

            # Dibujar texto de la opción
            texto = font.render(opcion["texto"], True, (255, 255, 255))
            self.screen.blit(texto, (rect.x + 20, rect.y + 15))

            # Dibujar claves
            try:
                imagen = pygame.image.load(opcion["imagen"])
                imagen = pygame.transform.scale(imagen, (50, 50))
                imagen_rect = imagen.get_rect(center=(self.screen_width // 2 + 200, opcion["y"] + 30))
                self.screen.blit(imagen, imagen_rect)
            except:
                print(f"No se pudo cargar la imagen: {opcion['imagen']}")

        pygame.display.flip()

        return opciones

    def mostrar_instrucciones(self, tipo_clave_seleccionada):
        """Muestra las instrucciones del juego"""
        self.screen.fill((0, 0, 0))

        instructions = [
            f"Has seleccionado: Clave de {'Sol' if tipo_clave_seleccionada == 'sol' else 'Do' if tipo_clave_seleccionada == 'do' else 'Fa'}",
            "",
            "Keyboard Controls:",
            "C - Do",
            "D - Re",
            "E - Mi", 
            "F - Fa",
            "G - Sol",
            "ESC - Exit game",
            "",
            "Click on the game window and press any key to start..."
        ]

        for i, line in enumerate(instructions):
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, 150 + i*40))

        pygame.display.flip()

        # Wait for key press or click to establish focus
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.state_callback:
                        self.state_callback(0)
                    return None
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    return tipo_clave_seleccionada

    def run(self):
        tipo_clave_seleccionada = None

        # Esperar selección de clave
        esperando_clave = True
        while esperando_clave and self.running:
            opciones_clave = self.mostrar_menu_seleccion_clave()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    if self.state_callback:
                        self.state_callback(0)
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic izquierdo
                        mouse_pos = pygame.mouse.get_pos()
                        for opcion in opciones_clave:
                            rect = pygame.Rect(self.screen_width//2 - 250, opcion["y"], 500, 60)
                            if rect.collidepoint(mouse_pos):
                                tipo_clave_seleccionada = opcion["clave"]
                                esperando_clave = False
                                break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        if self.state_callback:
                            self.state_callback(0)
                        return None

            pygame.display.flip()
            pygame.time.wait(10)  # Pequeña pausa para no saturar la CPU

        if not self.running:
            return None

        # Mostrar instrucciones
        return self.mostrar_instrucciones(tipo_clave_seleccionada)