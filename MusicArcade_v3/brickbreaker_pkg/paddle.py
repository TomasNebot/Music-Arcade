import pygame
from utils import draw_text, draw_outline




# Paddle class
class paddle():
    def __init__(self, screen_width, screen_height, scale_notes, notas_progresivas, ball):
        self.reset(screen_width, screen_height, notas_progresivas)
        self.section_notes = [notas_progresivas[0]]
        self. previous_section_notes = [notas_progresivas[0]]
        self.sections = [(i * self.width // len(self.section_notes), (i + 1) * self.width // len(self.section_notes)) for i in range(len(self.section_notes))]
        self.alpha_values = [0 for _ in range(len(self.section_notes))]  # Lista para almacenar los valores de alpha para cada sección
        self.banda_error = 0.6
        self.scale_notes = scale_notes
        self.notas_progresivas = notas_progresivas
        self.font = pygame.font.SysFont('Roboto', 30)
        self.font2 = pygame.font.SysFont('Roboto', 33)
        self.negro = (0, 0, 0)
        self.blanco = (255, 255, 255)
        self.azul = (153, 204, 255)
        self.azul_osc = (50, 100, 150)
        self.ball = ball

    def draw_section_notes(self, screen):
        for i, (start, end) in enumerate(self.sections):
            note_index = self.notas_progresivas.index(self.section_notes[i])
            note_text = str(self.scale_notes[note_index])  # Convertir el número de nota a texto
            if self.ball.proyecX != 0:
                if start <= self.ball.proyecX <= end:
                    draw_outline(note_text, self.font2, self.azul_osc, (start + end) // 2, self.y + self.height + 10, screen)
                    draw_text(note_text, self.font, self.azul, (start + end) // 2, self.y + self.height + 10, screen)
                else:
                    draw_text(note_text, self.font, self.azul_osc, (start + end) // 2, self.y + self.height + 10, screen)
            else:
                draw_text(note_text, self.font, self.azul_osc, (start+end)//2, self.y + self.height + 10, screen)

    def draw(self, surface, pitch):
        # Asegurar que la longitud de alpha_values coincida con la cantidad de secciones
        while len(self.alpha_values) < len(self.sections):
            self.alpha_values.append(0)

        # Actualizar alpha_values basado en pitch
        for i, note_value in enumerate(self.section_notes):
            if i < len(self.alpha_values):
                if note_value - self.banda_error < pitch < note_value + self.banda_error:
                    self.alpha_values[i] = min(self.alpha_values[i] + 10, 255)
                else:
                    self.alpha_values[i] = max(self.alpha_values[i] - 10, 20)

        # Dibujar cada sección con su respectivo alpha
        for i, (start, end) in enumerate(self.sections):
            if i < len(self.alpha_values):
                pygame.draw.rect(surface, (142, 135, 123, self.alpha_values[i]), (start, self.y, end - start, self.height))
                pygame.draw.rect(surface, (100, 100, 100, self.alpha_values[i]), (start, self.y, end - start, self.height), 3)

    # Añade secciones cada x tiempo
    def add(self, notas_progresivas, clock, tiempo_agrega_seccion):
        global tiempo_transcurrido
        tiempo_transcurrido += clock.get_time()
        # Verificar si es el momento de agregar una nueva sección
        if tiempo_transcurrido >= tiempo_agrega_seccion:
            tiempo_transcurrido = 0  # Reiniciar el contador de tiempo

            # Verificar si hay más notas por agregar
            if len(self.section_notes) < len(notas_progresivas):
                # Agregar la siguiente nota progresiva a la lista de notas de la pala
                nueva_nota = notas_progresivas[len(self.section_notes)]
                self.section_notes.append(nueva_nota)
                # Actualizar las secciones de la pala
                self.sections = [(i * self.width // len(self.section_notes), (i + 1) * self.width // len(self.section_notes)) for i in range(len(self.section_notes))]

    # Añade seccion cuando rompo una nota
    def add_section(self, new_note):
        # Buscamos indice y lo asignamos
        indice_nota = self.scale_notes.index(new_note)
        nota = self.notas_progresivas[indice_nota]
        # Agregar la nueva nota a la lista de notas de la pala
        self.section_notes.append(nota)
        # Ordenar las notas de la pala de menor a mayor
        self.section_notes.sort()
        # Actualizar las secciones de la pala
        self.sections = [(i * self.width // len(self.section_notes), (i + 1) * self.width // len(self.section_notes))
                         for i in range(len(self.section_notes))]
        # Actualizar la lista de valores alpha
        self.alpha_values.append(0)

    def reset(self, screen_width, screen_height, notas_progresivas):
        # Definir variables
        self.height = 20
        self.width = screen_width
        self.x = int((screen_width / 2) - (self.width / 2))
        self.y = screen_height - (self.height * 4)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.section_notes = [notas_progresivas[0]]
        self.sections = [(i * self.width // len(self.section_notes), (i + 1) * self.width // len(self.section_notes)) for i in range(len(self.section_notes))]
        self.alpha_values = [0 for _ in range(len(self.section_notes))]  # Lista para almacenar los valores de alpha para cada sección
