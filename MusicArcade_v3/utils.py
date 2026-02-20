import pygame
import math


# Funcion para crear texto
def draw_text(text, font, text_c, x, y, screen):
    """Dibuja texto en la pantalla, centrado en las coordenadas (x, y)."""
    img = font.render(text, True, text_c)
    text_rect = img.get_rect(center=(x, y))
    screen.blit(img, text_rect)


def draw_text_rect(text, font, text_c, rect, screen):
    """Dibuja texto en la pantalla, centrado en el rectángulo proporcionado."""
    img = font.render(text, True, text_c)
    text_rect = img.get_rect(center=rect.center)
    screen.blit(img, text_rect)


def draw_outline(text, font, outline_c, x, y, screen):
    # Dibujar el texto con un pequeño desplazamiento en todas las direcciones
    draw_text(text, font, outline_c, x - 3, y, screen)


# Funciones para dibujar flechas
def map_value(value, start1, stop1, start2, stop2):
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))


def map_range(value, in_min, in_max, out_min, out_max):
    """Mapea un valor de un rango a otro"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def draw_arrow(x, y, length, angle, color, screen):
    pygame.draw.polygon(screen, color, ((x + length * math.cos(math.radians(angle - 20)), y - length * math.sin(math.radians(angle - 20))),
                                        (x + length * math.cos(math.radians(angle + 20)), y - length * math.sin(math.radians(angle + 20))),
                                        (x + (length + 20) * math.cos(math.radians(angle)), y - (length + 20) * math.sin(math.radians(angle)))))


def draw_arrow_indication(pitch, amplitud, paddle, screen_height, screen_width, screen):
    arrow_length = 20
    # Color de las flechas
    roja = (240, 0, 0)
    verde = (0, 230, 0)
    naranja = (255, 128, 0)

    # Definir las coordenadas iniciales de las flechas
    x_left = 20
    y_left = screen_height - 200
    x_right = screen_width - 20
    y_right = screen_height - 200
    x_up = 0
    y_up = screen_height - 10

    # Angulo de las flechas
    angle_left = 0
    angle_right = 180
    angle_up = 90

    if amplitud > 30:
        # Dibujar flecha hacia la izquierda si el pitch es demasiado bajo
        if pitch < paddle.section_notes[0] - paddle.banda_error:
            draw_arrow(x_left, y_left, arrow_length, angle_left, roja, screen)

        # Dibujar flecha hacia la derecha si el pitch es demasiado alto
        elif pitch > paddle.section_notes[-1] + paddle.banda_error:
            draw_arrow(x_right, y_right, arrow_length, angle_right, roja, screen)

        # Dibujar flecha hacia arriba si el pitch está dentro de la sección actual
        else:
            for i, note in enumerate(paddle.section_notes):
                if paddle.section_notes[i] - 0.1 < pitch < paddle.section_notes[i] + 0.1:
                    draw_arrow((paddle.sections[i][0]+paddle.sections[i][1])/2, y_up, arrow_length, angle_up, verde, screen)
                elif note - paddle.banda_error < pitch < note + paddle.banda_error:
                    x_up = map_value(pitch, note - paddle.banda_error, note + paddle.banda_error, paddle.sections[i][0], paddle.sections[i][1])
                    draw_arrow(x_up, y_up, arrow_length, angle_up, naranja, screen)


def draw_multiline_text_in_rect(screen, text, rect, font_color=(0, 0, 0), bg_color=(255, 255, 255), border_width=4, border_color=(155, 155, 155)):
    """
    Dibuja un rectángulo con texto de varias líneas centrado dentro de él en una pantalla de Pygame.

    Args:
        screen (pygame.Surface): La superficie en la que se dibujará el rectángulo y el texto.
        text (str): El texto que se mostrará dentro del rectángulo.
        rect (tuple): Una tupla que contiene las coordenadas (x, y) y las dimensiones (ancho, alto) del rectángulo.
        font_color (tuple): Color del texto (predeterminado: negro).
        bg_color (tuple): Color de fondo del rectángulo (predeterminado: blanco).
        border_width (int): Ancho del borde del rectángulo (predeterminado: 0, sin borde).
        border_color (tuple): Color del borde del rectángulo (predeterminado: negro).
    """
    # Definir el tamaño máximo del texto basado en las dimensiones del rectángulo
    max_text_width = rect[2]
    max_text_height = rect[3]

    # Dividir el texto en líneas basadas en su longitud
    words = text.split(' ')
    lines = []
    line = ''
    for word in words:
        test_line = line + word + ' '
        if len(test_line) <= max_text_width//10:  # Tamaño de la fuente aproximado
            line = test_line
        else:
            lines.append(line)
            line = word + ' '
    lines.append(line)

    # Load the font file
    font_path = "PressStart2P-Regular.ttf"  # Replace this with the actual path to your font file
    font_size = 10  # Adjust the font size as needed
    font = pygame.font.Font(font_path, font_size)

    text_surface = []
    for line in lines:
        text_surface_line = font.render(line, True, font_color)
        text_surface.append(text_surface_line)

    # Volver a renderizar el texto con el tamaño final de la fuente
    text_surfaces = [font.render(line, True, font_color) for line in lines]

    # Obtener el rectángulo del texto y centrarlo dentro del rectángulo principal
    text_rects = [text_surface.get_rect() for text_surface in text_surfaces]
    total_text_height = sum([text_rect.height for text_rect in text_rects])
    y_offset = (max_text_height - total_text_height) // 2 + rect[1] - 20
    for i, text_rect in enumerate(text_rects):
        text_rect.centerx = rect[0] + rect[2] // 2 + 5
        text_rect.y = y_offset + 2
        y_offset += text_rect.height + 10

    pygame.draw.rect(screen, bg_color, rect)
    # Dibujar el rectángulo con el borde si es necesario
    if border_width > 0:
        pygame.draw.rect(screen, border_color, rect, border_width)


    # Dibujar el texto dentro del rectángulo
    for i, text_surface in enumerate(text_surfaces):
        screen.blit(text_surface, text_rects[i].topleft)


class Boton:
    def __init__(self, text, x, y, width, height):
        self.rect = pygame.Rect(x - width/2, y, width, height)
        self.font = pygame.font.SysFont('Constantia', height//2 + 15)
        self.color1 = pygame.Color('lightskyblue3')
        self.color2 = pygame.Color('gray15')
        self.text = text

    def draw(self, screen, text_c, rect_c):
        text_surface = self.font.render(self.text, True, text_c)
        self.rect.w = text_surface.get_width() + 20
        self.rect.h = text_surface.get_height() + 15
        pygame.draw.rect(screen, rect_c, self.rect, 3)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

