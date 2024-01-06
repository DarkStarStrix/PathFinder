import pygame
import sys
import heapq
import random

# Constants
WHITE, BLACK, GREEN, RED, BLUE, YELLOW = (255, 255, 255), (0, 0, 0), (0, 255, 0), (255, 0, 0), (0, 0, 255), (
    255, 255, 0)
WIDTH, HEIGHT, ROWS, COLS = 500, 500, 25, 25
CELL_WIDTH, CELL_HEIGHT = WIDTH // COLS, HEIGHT // ROWS
START, GOAL, NUM_WALLS = (0, 0), (ROWS - 1, COLS - 1), 100

pygame.init ()


class Maze:
    def __init__(self):
        self.agent_position = None
        self.path = None
        self.visited = set ()
        self.walls = set ()
        self.start = START
        self.goal = GOAL
        self.rows = ROWS
        self.cols = COLS
        self.generate_walls ()

    def a_star(self, screen):
        frontier = []
        heapq.heappush (frontier, (0, self.start))
        came_from = {}
        cost_so_far = {}
        came_from [self.start] = None
        cost_so_far [self.start] = 0
        while frontier:
            current = heapq.heappop (frontier) [1]
            if current == self.goal:
                break
            for next2 in self.get_neighbors (current):
                new_cost = cost_so_far [current] + 1
                if next2 not in cost_so_far or new_cost < cost_so_far [next2]:
                    cost_so_far [next2] = new_cost
                    priority = new_cost + self.heuristic (next2)
                    heapq.heappush (frontier, (priority, next2))
                    came_from [next2] = current
                    self.visited.add (next2)
                    self.draw (screen)  # Redraw the maze after each step
                    pygame.display.flip ()  # Update the display
                    pygame.time.delay (100)  # Add a delay to slow down the animation
        return self.reconstruct_path (came_from)

    def reconstruct_path(self, came_from):
        current = self.goal
        path = []
        while current != self.start:
            path.append (current)
            current = came_from [current]
        path.append (self.start)
        path.reverse ()
        self.path = path
        return path

    def heuristic(self, a):
        """Calculate the Manhattan distance from a given node to the goal."""
        return abs (a [0] - self.goal [0]) + abs (a [1] - self.goal [1])

    def get_neighbors(self, a):
        """Return the neighbors of a given node."""
        neighbors = []
        row, col = a
        if row > 0 and (row - 1, col) not in self.walls:
            neighbors.append ((row - 1, col))
        if row < self.rows - 1 and (row + 1, col) not in self.walls:
            neighbors.append ((row + 1, col))
        if col > 0 and (row, col - 1) not in self.walls:
            neighbors.append ((row, col - 1))
        if col < self.cols - 1 and (row, col + 1) not in self.walls:
            neighbors.append ((row, col + 1))
        return neighbors

    def generate_walls(self):
        """Generate a random maze."""
        self.walls = set ()
        self.agent_position = self.start
        self.path = None
        self.visited = set ()
        for _ in range (NUM_WALLS):
            row = random.randint (0, self.rows - 1)
            col = random.randint (0, self.cols - 1)
            if (row, col) not in [self.start, self.goal]:
                self.walls.add ((row, col))

    def draw(self, screen):
        color_map = {
            "start": BLUE,
            "goal": RED,
            "wall": BLACK,
            "path": GREEN,
            "visited": YELLOW,  # Change the color for visited nodes to yellow
            "default": WHITE
        }
        for i in range (self.rows):
            for j in range (self.cols):
                rect = pygame.Rect (j * CELL_WIDTH, i * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
                pygame.draw.rect (screen, BLACK, rect)  # Draw a cell border
                rect.inflate_ip (-4, -4)  # Reduce the size of cell for a border
                cell_type = "default"
                if (i, j) == self.start:
                    cell_type = "start"
                elif (i, j) == self.goal:
                    cell_type = "goal"
                elif (i, j) in self.walls:
                    cell_type = "wall"
                elif self.path is not None and (i, j) in self.path:
                    cell_type = "path"
                elif (i, j) in self.visited:
                    cell_type = "visited"
                pygame.draw.rect (screen, color_map [cell_type], rect)


maze = Maze ()
screen = pygame.display.set_mode ((WIDTH, HEIGHT))
pygame.display.set_caption ("A* Solver")

running = True
while running:
    for event in pygame.event.get ():
        if event.type == pygame.QUIT:
            running = False

    screen.fill (WHITE)
    maze.draw (screen)

    if not maze.path:
        maze.a_star (screen)

    pygame.display.flip ()

pygame.quit ()
