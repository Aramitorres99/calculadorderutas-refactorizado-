import pygame
import heapq
import sys

pygame.init()

window_width = 800
window_height = 600

cell_width = 50
cell_height = 50

start_p = pygame.image.load("punto inicio.jpg")
end_p = pygame.image.load("punto final.png")
car_p = pygame.image.load("auto.png")
water_p = pygame.image.load("agua.jpg")
bache_p = pygame.image.load("bache.jpg")

start_e = pygame.transform.scale(start_p, (cell_height, cell_width))
end_e = pygame.transform.scale(end_p, (cell_height, cell_width))
car_e = pygame.transform.scale(car_p, (cell_height, cell_width))
water_e = pygame.transform.scale(water_p, (cell_height, cell_width))
bache_e = pygame.transform.scale(bache_p, (cell_height, cell_width))


class Map_:
    def __init__(self, rows, cols, cost_obstacles, block_size=2, street_size=1):
        self.rows = rows
        self.cols = cols
        self.map_ = [[0 for _ in range(cols)] for _ in range(rows)]
        self.cost_obstacles = cost_obstacles
        self.start_point = None
        self.end_point = None
        self.block_size = block_size
        self.street_size = street_size
        self.create_grid()

    def create_grid(self):
        for i in range(0, self.rows, self.block_size + self.street_size):
            for j in range(0, self.cols, self.block_size + self.street_size):
                for k in range(self.block_size):
                    for l in range(self.block_size):
                        if i + k < self.rows and j + l < self.cols:
                            self.map_[i + k][j + l] = 'B'  # Cuadra
                for k in range(self.block_size + self.street_size):
                    if i + self.block_size < self.rows and j + k < self.cols:
                        self.map_[i + self.block_size][j + k] = 'S'  # Calle horizontal
                    if j + self.block_size < self.cols and i + k < self.rows:
                        self.map_[i + k][j + self.block_size] = 'S'  # Calle vertical

    def draw_map(self, window):
        for row in range(len(self.map_)):
            for col in range(len(self.map_[row])):
                cell = self.map_[row][col]
                x = col * cell_width
                y = row * cell_height

                if cell == 'B':
                    color = (150, 150, 150)  # Color para las cuadras
                    pygame.draw.rect(window, color, (x, y, cell_width, cell_height))
                elif cell == 'S':
                    color = (100, 100, 100)  # Color para las calles
                    pygame.draw.rect(window, color, (x, y, cell_width, cell_height))
                elif cell == 1:
                    window.blit(water_e, (x, y))  # Obstáculo de agua
                elif cell == 2:
                    window.blit(bache_e, (x, y))  # Obstáculo de bache
                elif cell == 'I':
                    window.blit(start_e, (x, y))  # Punto de inicio
                elif cell == 'F':
                    window.blit(end_e, (x, y))  # Punto final
                elif cell == 'R':
                    window.blit(car_e, (x, y))  # Ruta hecha

    def set_obstacle(self, pos, obstacle_type):
        if self.map_[pos[0]][pos[1]] == 'S':
            self.map_[pos[0]][pos[1]] = obstacle_type

    def set_start_point(self, pos):
        if self.map_[pos[0]][pos[1]] != 'B':  # Permitir sobre obstáculos, pero no sobre cuadras
            if self.start_point:
                if self.map_[self.start_point[0]][self.start_point[1]] not in [1, 2]:  # Si no es obstáculo
                    self.map_[self.start_point[0]][self.start_point[1]] = 'S'
            self.map_[pos[0]][pos[1]] = 'I'
            self.start_point = pos

    def set_end_point(self, pos):
        if self.map_[pos[0]][pos[1]] == 'S':
            if self.end_point:
                self.map_[self.end_point[0]][self.end_point[1]] = 'S'
            self.map_[pos[0]][pos[1]] = 'F'
            self.end_point = pos


class Route_calculator:
    def __init__(self, cost_obstacles):
        self.cost_obstacles = cost_obstacles

    def heuristic_function(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, pos, map_):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for d in directions:
            neighbor = (pos[0] + d[0], pos[1] + d[1])
            if 0 <= neighbor[0] < len(map_) and 0 <= neighbor[1] < len(map_[0]):
                if map_[neighbor[0]][neighbor[1]] != 'B':  # Evitar cuadras
                    neighbors.append(neighbor)
        return neighbors

    def get_cost(self, pos, map_):
        if map_[pos[0]][pos[1]] in self.cost_obstacles:
            return self.cost_obstacles[map_[pos[0]][pos[1]]]
        return 1  # Camino libre

    def a_star(self, map_, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic_function(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for neighbor in self.get_neighbors(current, map_):
                tentative_g_score = g_score[current] + self.get_cost(neighbor, map_)

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic_function(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None


class Game:
    def __init__(self):
        self.window = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Calculador de rutas")
        self.rows = window_height // cell_height
        self.cols = window_width // cell_width
        self.cost_obstacles = {
            1: 2,  # Obstáculo de agua
            2: 5   # Obstáculo de bache
        }
        self.block_size = 2  # Tamaño de las cuadras en celdas
        self.street_size = 1  # Tamaño de las calles en celdas
        self.map_instance = Map_(self.rows, self.cols, self.cost_obstacles, self.block_size, self.street_size)
        self.route_calculator = Route_calculator(self.cost_obstacles)
        self.selection_mode = 0  # Modo de selección (0: obstáculo de agua, 1: inicio, 2: fin, 3: obstáculo de bache)
        self.font = pygame.font.Font(None, 36)
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    row = y // cell_height
                    col = x // cell_width
                    if self.selection_mode == 0:
                        self.map_instance.set_obstacle((row, col), 1)
                    elif self.selection_mode == 1:
                        self.map_instance.set_start_point((row, col))
                    elif self.selection_mode == 2:
                        self.map_instance.set_end_point((row, col))
                    elif self.selection_mode == 3:
                        self.map_instance.set_obstacle((row, col), 2)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_o:
                        self.selection_mode = 0
                    elif event.key == pygame.K_i:
                        self.selection_mode = 1
                    elif event.key == pygame.K_f:
                        self.selection_mode = 2
                    elif event.key == pygame.K_b:
                        self.selection_mode = 3
                    elif event.key == pygame.K_SPACE and self.map_instance.start_point and self.map_instance.end_point:
                        path = self.route_calculator.a_star(self.map_instance.map_, self.map_instance.start_point, self.map_instance.end_point)
                        if path:
                            for paso in path:
                                if self.map_instance.map_[paso[0]][paso[1]] == 'S':
                                    self.map_instance.map_[paso[0]][paso[1]] = 'R'
                            self.window.fill((0, 0, 0))
                            self.map_instance.draw_map(self.window)
                            pygame.display.flip()
                            
                            victory_text = self.font.render("¡Esta es la ruta mas rapida!", True, (255, 255, 255)) #le da un mensaje al ganador
                            text_rect = victory_text.get_rect(center=(window_height // 2, window_width // 2)) #esto es donde muestra el mensaje ganador
                            self.window.blit(victory_text, text_rect) 
                            pygame.display.flip()
                            
                            pygame.time.delay(2000)  # Esperar 2 segundos antes de cerrar el juego
                            pygame.quit() #sale del juego
                            sys.exit() #sale del juego 
                        else:
                            print("No se encontró un camino desde el inicio hasta la meta.")

            self.window.fill((0, 0, 0))
            self.map_instance.draw_map(self.window)
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
