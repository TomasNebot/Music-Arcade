# config.py
import pygame
from utils import *


class Config:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Configuracion
        self.tempo_text = ''
        self.notas_text = ''
        self.tempo_input_rect = pygame.Rect(self.screen_width // 2 + 200, 300, 140, 35)
        self.notas_input_rect = pygame.Rect(self.screen_width // 2 + 100, 400, 140, 35)
        self.color_active = pygame.Color('lightskyblue3')
        self.color_passive = pygame.Color('gray15')
        self.color1 = self.color_passive
        self.color2 = self.color_passive
        self.hover_c = (128, 131, 189)  # Color para el hover
        self.boton_c = (78, 81, 139)
        self.font_conf = pygame.font.SysFont('Arial', 30)
        self.active_input = 0
        self.font_title = pygame.font.SysFont('Constantia', 60)
        self.font_menu = pygame.font.SysFont('Constantia', 40)
        self.text_c = (78, 81, 139)

        # Botón de volver
        self.back_button = pygame.Rect(self.screen_width // 2 - 80, self.screen_height - 80, 160, 40)
        self.apply_button = pygame.Rect(self.screen_width // 2 - 80, self.screen_height - 140, 160, 40)
        self.running = True
    
    def run(self):
        self.running = True
        clock = pygame.time.Clock()

        while self.running:
            self.screen.fill((0, 0, 0))

            # Obtener posición del mouse
            mouse_pos = pygame.mouse.get_pos()

            # Dibujar título y texto
            draw_text('OPTIONS', self.font_title, self.text_c, (self.screen_width // 3) + 60, (self.screen_height // 8), self.screen)
            draw_text('Tempo', self.font_menu, self.text_c, 200, 300, self.screen)
            draw_text('Notas', self.font_menu, self.text_c, 200, 400, self.screen)

            # Inputs para definir tempo y notas
            pygame.draw.rect(self.screen, self.color1, self.tempo_input_rect, 2)
            draw_text(self.tempo_text, self.font_conf, self.text_c, self.tempo_input_rect.centerx, self.tempo_input_rect.centery, self.screen)

            pygame.draw.rect(self.screen, self.color2, self.notas_input_rect, 2)
            draw_text(self.notas_text, self.font_conf, self.text_c, self.notas_input_rect.centerx, self.notas_input_rect.centery, self.screen)

            # Botones
            # Verificar si el mouse está sobre los botones
            if self.back_button.collidepoint(mouse_pos):
                back_color = self.hover_c
            else:
                back_color = self.text_c

            if self.apply_button.collidepoint(mouse_pos):
                apply_color = self.hover_c
            else:
                apply_color = self.text_c

            # Dibujar botones
            draw_text_rect('Aplicar', self.font_menu, apply_color, self.apply_button, self.screen)
            draw_text_rect('Volver', self.font_menu, back_color, self.back_button, self.screen)

            # Manejar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Verificar clicks en los inputs
                    if self.tempo_input_rect.collidepoint(event.pos):
                        self.active_input = 1
                        self.color1 = self.color_active
                        self.color2 = self.color_passive
                    elif self.notas_input_rect.collidepoint(event.pos):
                        self.active_input = 2
                        self.color1 = self.color_passive
                        self.color2 = self.color_active
                    elif self.back_button.collidepoint(event.pos):
                        self.running = False
                        return
                    elif self.apply_button.collidepoint(event.pos):
                        # Aplicar configuración
                        # self.scale_notes, self.notas_progresivas = cambiar_notas(self.notas_text)
                        # self.tempo_deseado = float(self.tempo_text)
                        print("Configuración aplicada")
                        pass
                    else:
                        self.active_input = 0
                        self.color1 = self.color_passive
                        self.color2 = self.color_passive

                if event.type == pygame.KEYDOWN:
                    if self.active_input == 1:  # Tempo input activo
                        if event.key == pygame.K_BACKSPACE:
                            self.tempo_text = self.tempo_text[:-1]
                        elif event.key != pygame.K_TAB and event.key != pygame.K_RETURN:
                            self.tempo_text += event.unicode
                    elif self.active_input == 2:  # Notas input activo
                        if event.key == pygame.K_BACKSPACE:
                            self.notas_text = self.notas_text[:-1]
                        elif event.key != pygame.K_TAB and event.key != pygame.K_RETURN:
                            self.notas_text += event.unicode

                    if event.key == pygame.K_TAB:
                        # Cambiar entre los inputs
                        self.active_input = (self.active_input % 2) + 1
                        if self.active_input == 1:
                            self.color1 = self.color_active
                            self.color2 = self.color_passive
                        elif self.active_input == 2:
                            self.color1 = self.color_passive
                            self.color2 = self.color_active

                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return

            pygame.display.update()
            clock.tick(60)