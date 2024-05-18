import pygame
import random
import heapq

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 40, 40
CELL_SIZE = WIDTH // COLS

# Colors
WHITE, GREEN, RED, BLUE, YELLOW = (255, 255, 255), (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)


class Cell:
    def __init__(self, x, y):
        self.x, self.y, self.visited = x, y, False
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}

    def get_neighbors(self, grid):
        neighbors = [grid[self.x + dx][self.y + dy] for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                     if 0 <= self.x + dx < ROWS and 0 <= self.y + dy < COLS]
        return [neighbor for neighbor in neighbors if not neighbor.visited]

    def draw(self, screen):
        x, y = self.x * CELL_SIZE, self.y * CELL_SIZE
        if self.visited:
            pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))
        if self.walls['top']:
            pygame.draw.line(screen, WHITE, (x, y), (x + CELL_SIZE, y), 1)
        if self.walls['right']:
            pygame.draw.line(screen, WHITE, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 1)
        if self.walls['bottom']:
            pygame.draw.line(screen, WHITE, (x + CELL_SIZE, y + CELL_SIZE), (x, y + CELL_SIZE), 1)
        if self.walls['left']:
            pygame.draw.line(screen, WHITE, (x, y + CELL_SIZE), (x, y), 1)

    def remove_walls(self, next_cell):
        dx, dy = self.x - next_cell.x, self.y - next_cell.y
        if dx == 1:
            self.walls['left'], next_cell.walls['right'] = False, False
        elif dx == -1:
            self.walls['right'], next_cell.walls['left'] = False, False
        if dy == 1:
            self.walls['top'], next_cell.walls['bottom'] = False, False
        elif dy == -1:
            self.walls['bottom'], next_cell.walls['top'] = False, False


def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    return path


def heuristic(cell1, cell2):
    return abs(cell1.x - cell2.x) + abs(cell1.y - cell2.y)


class Maze:
    def __init__(self):
        self.grid = [[Cell(i, j) for j in range(COLS)] for i in range(ROWS)]
        self.current = self.grid[0][0]
        self.stack = []
        self.path = []
        self.open_set = set()  # Cells that are being considered
        self.closed_set = set()  # Cells that have already been considered

    def generate_maze(self):
        self.current.visited = True
        self.stack.append(self.current)
        while self.stack:
            self.current = self.stack[-1]
            if not self.current.get_neighbors(self.grid):
                self.stack.pop()
                continue
            next_cell = random.choice(self.current.get_neighbors(self.grid))
            next_cell.visited = True
            self.current.remove_walls(next_cell)
            self.stack.append(next_cell)

    def draw(self, screen):
        for row in self.grid:
            for cell in row:
                cell.draw(screen)
        for cell in self.open_set:
            pygame.draw.rect(screen, BLUE, (cell.x * CELL_SIZE, cell.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        for cell in self.closed_set:
            pygame.draw.rect(screen, RED, (cell.x * CELL_SIZE, cell.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        for cell in self.path:
            pygame.draw.rect(screen, YELLOW, (cell.x * CELL_SIZE, cell.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def a_star(self, start, goal):
        open_set = []
        open_set_hash = set()  # This set will keep track of the nodes in the open set
        heapq.heappush(open_set, (0, start))
        open_set_hash.add(start)
        came_from = {}
        g_score = {cell: float("inf") for row in self.grid for cell in row}
        g_score[start] = 0
        f_score = {cell: float("inf") for row in self.grid for cell in row}
        f_score[start] = heuristic(start, goal)

        while open_set:
            current = heapq.heappop(open_set)[1]
            open_set_hash.remove(current)

            if current == goal:
                self.path = reconstruct_path(came_from, goal)
                print("Path found!")  # Add this line
                return True

            for neighbor in current.get_neighbors(self.grid):
                temp_g_score = g_score[current] + 1

                if temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + heuristic(neighbor, goal)

                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)

            self.closed_set.add(current)

        print("No path found.")  # Add this line
        return False


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    maze = Maze()
    maze.generate_maze()
    start, goal = maze.grid[0][0], maze.grid[-1][-1]
    path_found = maze.a_star(start, goal)
    print('path Found', path_found)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        screen.fill((0, 0, 0))
        maze.draw(screen)
        pygame.display.update()
        if not path_found:
            print('No path found!')
            break
        clock.tick(60)


if __name__ == "__main__":
    main()
