import pygame
import sys
import heapq
import random

# Define colors and grid dimensions
WHITE, BLACK, GREEN, RED, BLUE = (255, 255, 255), (0, 0, 0), (0, 255, 0), (255, 0, 0), (0, 0, 255)
WIDTH, HEIGHT, ROWS, COLS = 500, 500, 25, 25
CELL_WIDTH, CELL_HEIGHT = WIDTH // COLS, HEIGHT // ROWS

pygame.init ()


class Maze:
    def __init__(self, rows, cols, start, goal, num_walls):
        self.rows, self.cols, self.start, self.goal, self.num_walls = rows, cols, start, goal, num_walls
        self.walls, self.path, self.explored = set (), [], set ()
        self.generate_walls ()

    def is_valid(self, node):
        return 0 <= node [0] < self.rows and 0 <= node [1] < self.cols and node not in self.walls

    def generate_walls(self):
        while len (self.walls) < self.num_walls:
            wall = (random.randint (0, self.rows - 1), random.randint (0, self.cols - 1))
            if wall != self.start and wall != self.goal and wall not in self.walls:
                self.walls.add (wall)

    def get_neighbors(self, node):
        return [(node [0] + dx, node [1] + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)] if
                self.is_valid ((node [0] + dx, node [1] + dy))]

    def heuristic(self, node):
        return abs (node [0] - self.goal [0]) + abs (node [1] - self.goal [1])

    def a_star(self):
        open_set = [(self.heuristic (self.start), 0, self.start, [])]

        while open_set:
            _, cost, current_node, path = heapq.heappop (open_set)

            if current_node == self.goal:
                self.path = path
                return True

            if current_node in self.explored:
                continue

            self.explored.add (current_node)

            for neighbor in self.get_neighbors (current_node):
                new_cost = cost + 1
                heapq.heappush (open_set,
                                (new_cost + self.heuristic (neighbor), new_cost, neighbor, path + [current_node]))

        return False

    def draw(self, screen):
        for i in range (self.rows):
            for j in range (self.cols):
                rect = pygame.Rect (j * CELL_WIDTH, i * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
                color = BLUE if (i, j) == self.start else RED if (i, j) == self.goal else BLACK if (i,
                                                                                                    j) in self.walls else GREEN if (
                                                                                                                                   i,
                                                                                                                                   j) in self.path else WHITE if (
                                                                                                                                                                 i,
                                                                                                                                                                 j) in self.explored else WHITE
                pygame.draw.rect (screen, color, rect)


start, goal, num_walls = (0, 0), (ROWS - 1, COLS - 1), 100
maze = Maze (ROWS, COLS, start, goal, num_walls)
screen = pygame.display.set_mode ((WIDTH, HEIGHT))
pygame.display.set_caption ("A* Maze Solver")

running = True
while running:
    for event in pygame.event.get ():
        if event.type == pygame.QUIT:
            running = False

    screen.fill (WHITE)
    maze.draw (screen)

    if not maze.a_star ():
        print ("Goal is not reachable.")
        running = False

    pygame.display.flip ()
    pygame.time.delay (1000)

pygame.quit ()
sys.exit ()
