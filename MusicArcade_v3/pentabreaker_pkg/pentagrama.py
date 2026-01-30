import pygame
import pygame.freetype
import random
from pentabreaker_pkg.nota import Nota

COLOR_BLUE = (0,255,255)
COLOR_VIOLET = (111, 0, 255)

# Constantes para los tipos de clave
CLAVE_SOL = "sol"
CLAVE_DO = "do"
CLAVE_FA = "fa"

# Mapeo de posición de las notas en el pentagrama según la clave
# Los valores representan la posición relativa en el pentagrama (líneas y espacios)
# donde valores más altos están más abajo en el pentagrama
MIDI_POSICIONES = {
    # Clave de Sol
    CLAVE_SOL: {
        60: -1,    # C4 (Do) - Primera línea adicional inferior
        62: -0.5,    # D4 (Re) - Espacio debajo de la primera línea
        64: 0,    # E4 (Mi) - Primera línea
        65: 0.5,  # F4 (Fa) - Primer espacio
        67: 1,    # G4 (Sol) - Segunda línea
        69: 1.5,  # A4 (La) - Segundo espacio
        71: 2,    # B4 (Si) - Tercera línea
        72: 2.5,  # C5 (Do) - Tercer espacio
    },
    # Clave de Do en tercera línea
    CLAVE_DO: {
        57: 1,    # A3 (La) - Cuarta línea
        59: 1.5,  # B3 (Si) - Entre tercera y cuarta línea
        60: 2,    # C4 (Do) - En la tercera línea
        62: 2.5,  # D4 (Re) - Entre la segunda y tercera línea
        64: 3,    # E4 (Mi) - Segunda línea
        65: 3.5,  # F4 (Fa) - Entre la primera y segunda línea
        67: 4,    # G4 (Sol) - Primera línea
    },
    # Clave de Fa en cuarta línea
    CLAVE_FA: {
        48: 2.5,    # C3 (Do) - Entre segunda y tercera
        50: 3,  # D3 (Re) - En tercera
        52: 3.5,    # E3 (Mi) - Entre tercera y scuarta
        53: 4,  # F3 (Fa) - En cuarta linea
        55: 4.5,    # G3 (Sol) - Entre cuarta y quinta
        57: 5, # A3 (La) - Quinta linea
        59: 5.5,   # B3 (Si) - Espacio encima de la ultima línea
        60: 6,    # C4 (Do) - Linea adicional superior
    }
}

# Mapeo de notas disponibles según la clave
NOTAS_POR_CLAVE = {
    CLAVE_SOL: [60, 62, 64, 65, 67, 69, 71, 72],  # Do4 a Do5
    CLAVE_DO: [57, 59, 60, 62, 64, 65, 67],       # La3 a Sol4
    CLAVE_FA: [48, 50, 52, 53, 55, 57, 59, 60]    # Do3 a Do4
}

class Pentagrama:
    def __init__(self, screen_width, screen_height, tipo_clave=CLAVE_DO):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.y = 0
        self.velocidad = float(0.5)
        self.color_pent = (255, 255, 255)
        self.color_notas = (0, 255, 0)
        self.espaciado = 20
        self.num_lineas = 5
        self.tipo_clave = tipo_clave
        self.notas_disponibles = NOTAS_POR_CLAVE[tipo_clave]  # Notas posibles
        self.notas = []
        self.generar_nuevo_pentagrama()

        # Generar imagenes de clave
        # Clave Do
        imagen_clave_do = pygame.image.load("pentabreaker_pkg/clave_do.png")
        self.imag_clave_do = pygame.transform.scale(imagen_clave_do, (50, 90))  # Ratio 0.56
        # Clave Sol
        imagen_clave_sol = pygame.image.load("pentabreaker_pkg/clave_sol.png")
        self.imag_clave_sol = pygame.transform.scale(imagen_clave_sol, (112, 150))  # Ratio 0.75
        # Clave Fa
        imagen_clave_fa = pygame.image.load("pentabreaker_pkg/clave_fa.png")
        self.imag_clave_fa = pygame.transform.scale(imagen_clave_fa, (52, 65))  # Ratio 0.81

    def generar_nuevo_pentagrama(self):
        # Reiniciar la posición del pentagrama
        self.y = 0
        """Genera una nueva secuencia aleatoria de notas para el pentagrama."""
        num_notas = random.randint(3, 5)  # Definir cuántas notas tendrá el pentagrama
        self.notas = [Nota(random.choice(self.notas_disponibles), 0, 0) for _ in range(num_notas)]
        
        # Definir posicion notas
        separacion_horizontal = 200  # Espacio horizontal entre notas
        total_ancho_notas = (len(self.notas) - 1) * separacion_horizontal  # Ancho total de las notas
        inicio_x = (self.screen_width // 2) - (total_ancho_notas // 2)  # Centrado dinámico

        for i, nota in enumerate(self.notas):
            pos_relativa = MIDI_POSICIONES[self.tipo_clave].get(nota.midi)

            if pos_relativa is not None:
                note_y_position = self.y + (self.num_lineas - 1 - pos_relativa) * self.espaciado
                note_x_position = inicio_x + i * separacion_horizontal  # Distribuir horizontalmente
                self.notas[i].x = note_x_position
                self.notas[i].y = note_y_position
        print(f"Generado pentagrama con clave {self.tipo_clave}")

    def actualizar(self):
        self.y += self.velocidad
        for nota in self.notas:
            nota.y += self.velocidad
        if self.y >= self.screen_height - 50:
            return False  # Retornar False indica que se perdió una vida
        return True  # El juego continúa normal

    def verificar_colision(self, pitch_detectado):
        for nota in self.notas:
            if not nota.impactado and pitch_detectado:
                if nota.midi == pitch_detectado:  # Comparación directa en MIDI
                    nota.impactado = True
                    print(f"Impactaste la nota {nota.midi} correctamente!")

                    # Verificar si todas las notas fueron impactadas
                    if all(n.impactado for n in self.notas):
                        print("Pentagrama completado! Generando uno nuevo...")
                        self.generar_nuevo_pentagrama()
                    return True
        return False

    def dibujar(self, screen, mostrar_texto=False):
        # Dibujar las líneas del pentagrama
        for i in range(self.num_lineas):
            y_pos = self.y + i * self.espaciado
            pygame.draw.line(screen, self.color_pent, (50, y_pos), (self.screen_width - 50, y_pos), 2)
        
        for nota in self.notas:
            color = self.color_notas if nota.impactado else self.color_pent
            pygame.draw.circle(screen, color, (nota.x, nota.y), 10)
            pos_relativa = MIDI_POSICIONES[self.tipo_clave].get(nota.midi)

            # Dibujar línea auxiliar si la nota está fuera del pentagrama
            if pos_relativa is not None:
                if pos_relativa >= 5 or pos_relativa <= -1:
                    pygame.draw.line(screen, self.color_pent, (nota.x - 15, nota.y), (nota.x + 14, nota.y), 2)

            # Mostrar nombre de la nota si estamos en nivel 1 o se solicita
            if mostrar_texto:
                from pentabreaker_pkg.nota import NOMBRE_NOTAS
                nombre_nota = NOMBRE_NOTAS.get(nota.midi, "")
                if nombre_nota:
                    font = pygame.font.SysFont('Constantia', 16)
                    texto = font.render(nombre_nota, True, COLOR_BLUE)
                    screen.blit(texto, (nota.x + 15, nota.y - 8))  # Mostrar texto a la derecha de la nota
        # Dibujar la clave
        if self.tipo_clave == CLAVE_DO:
            # Dibujar claves
            self.rect_clave_do = self.imag_clave_do.get_rect(center=(self.screen_width // 2 - 470, self.y + 40))
            screen.blit(self.imag_clave_do, self.rect_clave_do)
        if self.tipo_clave == CLAVE_SOL:
            # Dibujar claves
            self.rect_clave_sol = self.imag_clave_sol.get_rect(
                center=(self.screen_width // 2 - 470, self.y + 45))
            screen.blit(self.imag_clave_sol, self.rect_clave_sol)
        if self.tipo_clave == CLAVE_FA:
            # Dibujar claves
            self.rect_clave_fa = self.imag_clave_fa.get_rect(center=(self.screen_width // 2 - 470, self.y + 32))
            screen.blit(self.imag_clave_fa, self.rect_clave_fa)