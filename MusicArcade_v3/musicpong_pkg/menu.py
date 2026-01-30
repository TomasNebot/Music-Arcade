
import pygame
import sys
import time

class MenuMusicPong:
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
        # Valores por defecto para el rango de pitch
        self.pitch_min = 45
        self.pitch_max = 80
        
    def mostrar_menu_modo_juego(self):
        """Muestra un menú para seleccionar el modo de juego"""
        self.screen.fill((0, 0, 0))
        
        # Título
        titulo = self.font_titulo.render("MUSIC PONG", True, (255, 255, 0))
        self.screen.blit(titulo, (self.screen_width//2 - titulo.get_width()//2, 100))

        # Opciones de modo de juego
        opciones = [
            {"texto": "1 Jugador (vs IA)", "modo": 1, "y": 300},
            {"texto": "2 Jugadores", "modo": 2, "y": 380},
            {"texto": "Configurar Rango de Pitch", "modo": "config", "y": 460}
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for opcion in opciones:
            # Rectángulo para la opción
            rect = pygame.Rect(self.screen_width//2 - 200, opcion["y"], 400, 60)
            
            # Verificar si el mouse está sobre esta opción
            hover = rect.collidepoint(mouse_pos)
            color_rect = (50, 50, 80) if hover else (30, 30, 50)
            
            # Dibujar rectángulo de fondo
            pygame.draw.rect(self.screen, color_rect, rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 100, 150), rect, 2, border_radius=5)
            
            # Dibujar texto de la opción
            texto = self.font.render(opcion["texto"], True, (255, 255, 255))
            self.screen.blit(texto, (rect.x + (rect.width - texto.get_width())//2, rect.y + 15))
        
        pygame.display.flip()
        
        return opciones
    
    def mostrar_instrucciones(self, modo_juego):
        """Muestra las instrucciones del juego"""
        self.screen.fill((0, 0, 0))

        if isinstance(modo_juego, tuple):
            modo_juego = modo_juego[0]

        instructions = [
            f"Modo seleccionado: {'1 Jugador' if modo_juego == 1 else '2 Jugadores'}",
            "",
            "Controles:",
            "- Jugador izquierdo: Control por tono de voz (pitch)",
            f"- Jugador derecho: {'IA' if modo_juego == 1 else 'Control por tono de voz (pitch)'}",
            f"Rango de pitch configurado: {self.pitch_min} - {self.pitch_max}",
            "Canta/haz sonidos con tonos más graves para mover hacia abajo",
            "",
            "y más agudos para mover hacia arriba.",
            "",
            "Objetivo:",
            "- Golpea la pelota con tu paddle",
            "- El primer jugador en alcanzar 10 puntos gana",
            "",
            "ESC - Salir al menú principal",
            "",
            "Haz clic o presiona cualquier tecla para comenzar..."
        ]
        
        for i, line in enumerate(instructions):
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, 150 + i*30))
        
        pygame.display.flip()
        
        # Esperar a que el usuario presione una tecla o haga clic
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.state_callback:
                        self.state_callback(0)
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    else:
                        waiting = False
                        return modo_juego
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    return modo_juego
            
            pygame.time.wait(10)  # Pequeña pausa para no saturar la CPU

    def configurar_pitch_range(self):
        """Muestra pantalla de configuración del rango de pitch"""
        configurando = True

        # Sliders para min y max pitch
        slider_min_x = self.screen_width // 2 - 200
        slider_max_x = self.screen_width // 2 + 200
        slider_y = self.screen_height // 2

        # Valores mínimos y máximos permitidos
        pitch_valor_minimo = 45
        pitch_valor_maximo = 80

        # Asegurarse de que los valores actuales estén dentro del rango permitido
        if self.pitch_min < pitch_valor_minimo:
            self.pitch_min = pitch_valor_minimo
        if self.pitch_max > pitch_valor_maximo:
            self.pitch_max = pitch_valor_maximo

        # Posiciones iniciales de los botones deslizantes (mapeados al nuevo rango)
        min_pos = int(slider_min_x + ((slider_max_x - slider_min_x) * (self.pitch_min - pitch_valor_minimo) / (
                    pitch_valor_maximo - pitch_valor_minimo)))
        max_pos = int(slider_min_x + ((slider_max_x - slider_min_x) * (self.pitch_max - pitch_valor_minimo) / (
                    pitch_valor_maximo - pitch_valor_minimo)))

        # Variables para controlar los sliders
        dragging_min = False
        dragging_max = False

        while configurando:
            self.screen.fill((0, 0, 0))

            # Título
            titulo = self.font_titulo.render("Configuración de Pitch", True, (255, 255, 0))
            self.screen.blit(titulo, (self.screen_width // 2 - titulo.get_width() // 2, 100))

            # Instrucciones
            instruccion = self.font.render("Ajusta el rango de pitch que controla las palas", True, (255, 255, 255))
            self.screen.blit(instruccion, (self.screen_width // 2 - instruccion.get_width() // 2, 170))

            # Dibujar línea del slider
            pygame.draw.line(self.screen, (100, 100, 100), (slider_min_x, slider_y), (slider_max_x, slider_y), 2)

            # Dibujar botones deslizantes
            min_button = pygame.Rect(min_pos - 10, slider_y - 15, 20, 30)
            max_button = pygame.Rect(max_pos - 10, slider_y - 15, 20, 30)

            pygame.draw.rect(self.screen, (100, 100, 255), min_button, border_radius=5)
            pygame.draw.rect(self.screen, (255, 100, 100), max_button, border_radius=5)

            # Mostrar valores actuales
            min_text = self.font.render(f"Pitch Mínimo: {self.pitch_min}", True, (255, 255, 255))
            max_text = self.font.render(f"Pitch Máximo: {self.pitch_max}", True, (255, 255, 255))

            self.screen.blit(min_text, (self.screen_width // 2 - 200, slider_y + 50))
            self.screen.blit(max_text, (self.screen_width // 2 + 50, slider_y + 50))

            # Botón para guardar y volver
            guardar_rect = pygame.Rect(self.screen_width // 2 - 150, self.screen_height - 150, 300, 60)
            pygame.draw.rect(self.screen, (30, 100, 30), guardar_rect, border_radius=5)
            pygame.draw.rect(self.screen, (100, 200, 100), guardar_rect, 2, border_radius=5)

            guardar_text = self.font.render("Guardar y Volver", True, (255, 255, 255))
            self.screen.blit(guardar_text, (
            guardar_rect.x + (guardar_rect.width - guardar_text.get_width()) // 2, guardar_rect.y + 15))

            # Manejar eventos
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    if self.state_callback:
                        self.state_callback(0)
                    return None

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if min_button.collidepoint(mouse_pos):
                        dragging_min = True
                    elif max_button.collidepoint(mouse_pos):
                        dragging_max = True
                    elif guardar_rect.collidepoint(mouse_pos):
                        configurando = False

                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging_min = False
                    dragging_max = False

                elif event.type == pygame.MOUSEMOTION:
                    if dragging_min:
                        min_pos = max(slider_min_x, min(mouse_pos[0], max_pos - 20))
                        self.pitch_min = int(45 + (min_pos - slider_min_x) * (80 - 45) / (slider_max_x - slider_min_x))
                        # Asegurar que no sea menor que 45
                        self.pitch_min = max(45, self.pitch_min)

                    if dragging_max:
                        max_pos = min(slider_max_x, max(mouse_pos[0], min_pos + 20))
                        self.pitch_max = int(45 + (max_pos - slider_min_x) * (80 - 45) / (slider_max_x - slider_min_x))
                        # Asegurar que no sea mayor que 80
                        self.pitch_max = min(80, self.pitch_max)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        configurando = False

            pygame.display.flip()
            pygame.time.wait(10)  # Pequeña pausa para no saturar la CPU

    def run(self):
        """Ejecuta el menú y devuelve el modo de juego seleccionado"""
        modo_juego_seleccionado = None
        
        # Esperar selección de modo de juego
        esperando_modo = True
        while esperando_modo and self.running:
            opciones_modo = self.mostrar_menu_modo_juego()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    if self.state_callback:
                        self.state_callback(0)
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic izquierdo
                        mouse_pos = pygame.mouse.get_pos()
                        for opcion in opciones_modo:
                            rect = pygame.Rect(self.screen_width//2 - 200, opcion["y"], 400, 60)
                            if rect.collidepoint(mouse_pos):
                                if opcion["modo"] == "config":
                                    self.configurar_pitch_range()
                                else:
                                    modo_juego_seleccionado = opcion["modo"]
                                    esperando_modo = False
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
        if modo_juego_seleccionado:
            return (modo_juego_seleccionado, self.pitch_min, self.pitch_max)
        return None

