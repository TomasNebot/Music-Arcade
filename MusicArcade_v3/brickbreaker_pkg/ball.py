import pygame
import random

# Ball class
class game_ball():

    def __init__(self, x, y):
        self.reset(x, y)
        # Color bola
        self.ball_c = (142, 135, 123)
        self.ball_outline = (100, 100, 100)
        self.brick_bottom = 0
        self.ball_x0 = 0
        self.paddle = None
        self.proyecX = 0
        self.collision_thresh = 10

    def calcular_trayectoria(self, vx, vy, width, paddle):
        if vx < 0:
            xt = abs((vx / vy) * (0 - (self.brick_bottom - paddle.y)) + self.ball_x0)
            n_rebotes = int(xt) // int(width)
            resto = xt % width
            if n_rebotes == 0:
                proyecX = xt
            elif n_rebotes % 2 == 0 or n_rebotes == 1:  # es par o 1
                proyecX = width - resto
            else:
                proyecX = resto
        else:
            xt = abs((vx / vy) * (0 - (self.brick_bottom - paddle.y)) + self.ball_x0)
            n_rebotes = int(xt) // int(width)
            resto = xt % width
            if n_rebotes == 0:
                proyecX = xt
            elif n_rebotes % 2 == 0:  # es par
                proyecX = resto
            else:
                proyecX = width - resto
        return proyecX

    def move(self, screen_height, screen_width, wall, paddle, notas_colisionadas):
        # Defino pala
        self.paddle = paddle

        # Reset nota colisionada
        nota_col = 0

        # Colision ladirllos (asumo que la muralla esta destruida inicialmente)
        wall_destroyed = 1
        row_count = 0
        for row in wall.blocks:
            item_count = 0
            for item in row:
                # check collision
                if self.rect.colliderect(item[0]):
                    # Colision desde arriba
                    if abs(self.rect.bottom - item[0].top) < self.collision_thresh and self.speed_y > 0:
                        self.speed_y *= -1
                    # Colision desde abajo
                    if abs(self.rect.top - item[0].bottom) < self.collision_thresh and self.speed_y < 0:
                        self.speed_y *= -1
                        self.brick_bottom = item[0].bottom + self.collision_thresh
                        self.ball_x0 = self.rect.x
                        self.proyecX = self.calcular_trayectoria(self.speed_x, self.speed_y, screen_width - 2 * self.collision_thresh, paddle)
                        # Colision desde izq
                    if abs(self.rect.right - item[0].left) < self.collision_thresh and self.speed_x > 0:
                        self.speed_x *= -1
                        if self.speed_y > 0:
                            self.brick_bottom = self.y
                            self.ball_x0 = self.rect.x
                            self.proyecX = self.calcular_trayectoria(self.speed_x, self.speed_y, screen_width - 2 * self.collision_thresh, paddle)

                    # Colision desde dcha
                    if abs(self.rect.left - item[0].right) < self.collision_thresh and self.speed_x < 0:
                        self.speed_x *= -1
                        if self.speed_y > 0:
                            self.brick_bottom = self.y
                            self.ball_x0 = self.rect.x
                            self.proyecX = self.calcular_trayectoria(self.speed_x, self.speed_y, screen_width - 2 * self.collision_thresh, paddle)

                    # Hacemos daño al ladrillo
                    if wall.blocks[row_count][item_count][1] > 1:
                        wall.blocks[row_count][item_count][1] -= 1
                    else:
                        wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)
                        if wall.blocks[row_count][item_count][2] != "":
                            paddle.add_section(item[2])

                # Revisar si hay bloques
                if wall.blocks[row_count][item_count][0] != (0, 0, 0, 0):
                    wall_destroyed = 0
                # Aumentamos cont
                item_count += 1
            # Aumentamos cont
            row_count += 1
        # Revisamos si todos los bloques se han destruido
        if wall_destroyed == 1:
            self.game_over = 1

        # Colisiones paredes laterales
        if self.rect.left + self.collision_thresh < 0 or self.rect.right > screen_width - self.collision_thresh:
            self.speed_x *= -1

        # Colisiones arriba y abajo
        if self.rect.top < 0:
            self.speed_y *= -1
            self.brick_bottom = self.rect.top
            self.ball_x0 = self.rect.x
            self.proyecX = self.calcular_trayectoria(self.speed_x, self.speed_y,
                                                     screen_width - 2 * self.collision_thresh, paddle)
        if self.rect.bottom > screen_height:
            self.game_over = -1

        # Colisión con pala
        for i, (start, end) in enumerate(paddle.sections):
            if self.rect.colliderect(pygame.Rect(start, paddle.y, end - start, paddle.height)):
                # Verificar si la pelota colisiona con una sección activa de la pala
                self.proyecX = 0
                if paddle.alpha_values[i] > 20:
                    if abs(self.rect.bottom - paddle.rect.top) < self.collision_thresh and self.speed_y > 0:
                        self.speed_y *= -1
                        relative_position = ((self.rect.x + self.ball_rad) - start) / (end - start)
                        scaled_velocity = (relative_position * 2) - 1  # Escalar el valor entre -1 y 1
                        self.speed_x = int(scaled_velocity * 5)
                        if self.speed_x > self.speed_max:
                            self.speed_x = self.speed_max
                        elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                            self.speed_x = -self.speed_max
                        elif self.speed_x == 0:
                            self.speed_x = random.uniform(-1, 1)
                        notas_colisionadas.append(paddle.section_notes[i])
                        nota_col = paddle.section_notes[i]
                    break

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.game_over, nota_col

    def draw(self, screen):
        pygame.draw.circle(screen, self.ball_c, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
        pygame.draw.circle(screen, self.ball_outline, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad, 3)

    def reset(self, x, y):
        self.ball_rad = 7
        self.x = x - self.ball_rad
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = random.randint(-4, 4)
        self.speed_y = -3
        self.speed_max = 8 # 6
        self.game_over = 0
