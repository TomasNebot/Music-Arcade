# Brick wall class
import pygame
import random
from utils import draw_text

class wall():
    def __init__(self, screen_width, cols):
        self.width = screen_width // cols
        self.height = 30
        # Colores ladrillos
        self.red = (255, 165, 0)
        self.green = (86, 174, 87)
        self.blue = (69, 177, 233)
        # Letra y color
        self.font = pygame.font.SysFont('Constantia', 20)
        self.text_c = (78, 81, 139)

    def create_wall(self, rows, cols, scale_notes):
        self.blocks = []
        # Inicializar indice de nota
        index_notas_progresivas = 1

        for row in range(rows -1, -1, -1):
            # Resetea la lista de ladrillos por filas
            block_row = []
            # Seleccionar aleatoriamente una columna con nota
            note_column = random.randint(0, cols -1)
            # Iterar por cada columna
            for col in range(cols):
                # Generar posicion x e y para cada ladrillo y crear rectangulo
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                # Assign block stenght based on row
                if row < rows:
                    strength = 1 # 3
                elif row < 4:
                    strength = 2
                elif row < 6:
                    strength = 1
                # Asignar nota solo si hay suficientes disponibles
                if index_notas_progresivas < len(scale_notes) and col == note_column:
                    note = scale_notes[index_notas_progresivas]
                    index_notas_progresivas += 1
                else:
                    note = ""
                # Crear lista para guardar la fuerza y el color de los ladrillos
                block_individual = [rect, strength, note]
                # Añadir ladrillo individual a la fila
                block_row.append(block_individual)
            # Añadir la fila a la lista de todos los bloques
            self.blocks.append(block_row)

    def create_wall_tutorial(self, rows, cols, scale_notes):
        self.blocks = []
        # Inicializar indice de nota
        index_notas_progresivas = 1

        for row in range(rows -1, -1, -1):
            # Resetea la lista de ladrillos por filas
            block_row = []
            if row != rows - 1:
                note_column = random.randint(0, cols - 1)
            else:
                note_column = None
            # Iterar por cada columna
            for col in range(cols):
                # Generar posicion x e y para cada ladrillo y crear rectangulo
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                # Assign block stenght based on row
                if row < rows:
                    strength = 1 # 3
                elif row < 4:
                    strength = 2
                elif row < 6:
                    strength = 1
                # Asignar nota solo si hay suficientes disponibles
                if index_notas_progresivas < len(scale_notes) and col == note_column:
                    note = scale_notes[index_notas_progresivas]
                    index_notas_progresivas += 1
                else:
                    note = ""
                # Crear lista para guardar la fuerza y el color de los ladrillos
                block_individual = [rect, strength, note]
                # Añadir ladrillo individual a la fila
                block_row.append(block_individual)
            # Añadir la fila a la lista de todos los bloques
            self.blocks.append(block_row)

    def draw_wall(self, screen, bg):
        for row in self.blocks:
            for block in row:
                # Asignar los colores y la fuerza
                if block[1] == 3:
                    block_c = self.blue
                elif block[1] == 2:
                    block_c = self.green
                elif block[1] == 1:
                    block_c = self.red
                pygame.draw.rect(screen, block_c, block[0])
                pygame.draw.rect(screen, bg, (block[0]), 2)
                # Dibujar nota
                if block[0] != (0, 0, 0, 0):
                    draw_text(block[2], self.font, self.text_c, block[0].x + block[0].width // 2, block[0].y + block[0].height // 2, screen)

