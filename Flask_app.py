import heapq
from flask import Flask, send_file, render_template
from PIL import Image, ImageDraw
import io
import random

# Constants
WHITE, BLACK, GREEN, RED, BLUE, YELLOW = (255, 255, 255), (0, 0, 0), (0, 255, 0), (255, 0, 0), (0, 0, 255), (
    255, 255, 0)
WIDTH, HEIGHT, ROWS, COLS = 500, 500, 50, 50
CELL_WIDTH, CELL_HEIGHT = WIDTH // COLS, HEIGHT // ROWS
START, GOAL = (0, 0), (ROWS - 1, COLS - 1)


class Maze:
    global col, cell_type

    def __init__(self):
        self.img = None
        self.path = None
        self.visited = set ()
        self.walls = set ()
        self.start = START
        self.goal = GOAL
        self.rows = ROWS
        self.cols = COLS
        self.generate_maze ()

    def generate_maze(self):
        self.walls = {(row, col) for row in range (self.rows) for col in range (self.cols)}
        stack = [self.start]
        while stack:
            cell = stack [-1]
            if cell not in self.walls:
                stack.pop ()
                continue
            self.walls.remove (cell)
            neighbors = [neighbor for neighbor in self.get_neighbors (cell) if neighbor in self.walls]
            if neighbors:
                stack.append (random.choice (neighbors))
            else:
                stack.pop ()

    def get_neighbors(self, cell):
        neighbors = []
        row, col = cell
        if row > 0:
            neighbors.append ((row - 1, col))
        if row < self.rows - 1:
            neighbors.append ((row + 1, col))
        if col > 0:
            neighbors.append ((row, col - 1))
        if col < self.cols - 1:
            neighbors.append ((row, col + 1))
        return neighbors

    def a_star(self):
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
                    self.draw ()
        if self.goal not in came_from:
            return None
        return self.reconstruct_path (came_from)

    def heuristic(self, a):
        return abs (a [0] - self.goal [0]) + abs (a [1] - self.goal [1])

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

    def draw(self):
        self.img = Image.new ('RGB', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw (self.img)
    for wall in self.walls:
        draw.rectangle (
            (wall [1] * CELL_WIDTH, wall [0] * CELL_HEIGHT, (wall [1] + 1) * CELL_WIDTH,
             (wall [0] + 1) * CELL_HEIGHT),
            fill=BLACK)
    for cell in self.visited:
        draw.rectangle (
            (cell [1] * CELL_WIDTH, cell [0] * CELL_HEIGHT, (cell [1] + 1) * CELL_WIDTH,
             (cell [0] + 1) * CELL_HEIGHT),
            fill=BLUE)
    if self.path:
        for cell in self.path:
            draw.rectangle (
                (cell [1] * CELL_WIDTH, cell [0] * CELL_HEIGHT, (cell [1] + 1) * CELL_WIDTH,
                 (cell [0] + 1) * CELL_HEIGHT),
                fill=YELLOW)
    draw.rectangle (
        (self.start [1] * CELL_WIDTH, self.start [0] * CELL_HEIGHT, (self.start [1] + 1) * CELL_WIDTH,
         (self.start [0] + 1) * CELL_HEIGHT), fill=GREEN)
    draw.rectangle (
        (self.goal [1] * CELL_WIDTH, self.goal [0] * CELL_HEIGHT, (self.goal [1] + 1) * CELL_WIDTH,
         (self.goal [0] + 1) * CELL_HEIGHT), fill=RED)

    if self.path:
        for cell in self.path:
            draw.rectangle (
                (cell [1] * CELL_WIDTH, cell [0] * CELL_HEIGHT, (cell [1] + 1) * CELL_WIDTH,
                 (cell [0] + 1) * CELL_HEIGHT),
                fill=YELLOW)

    self.img.save ('maze.jpg')


app = Flask (__name__)


@app.route ('/')
def index():
    return render_template ('index.html')


@app.route ('/run-pathfinder', methods=['GET'])
def run_pathfinder():
    maze = Maze ()
    maze.a_star ()
    maze.draw ()
    img_io = io.BytesIO ()
    maze.img.save (img_io, 'JPEG', quality=70)
    img_io.seek (0)
    return send_file (img_io, mimetype='image/jpeg')


@app.route ('/reset-maze', methods=['GET'])
def reset_maze():
    maze = Maze ()
    maze.path = None
    maze.visited = set ()
    maze.draw ()
    img_io = io.BytesIO ()
    maze.img.save (img_io, 'JPEG', quality=70)
    img_io.seek (0)
    return send_file (img_io, mimetype='image/jpeg')


if __name__ == '__main__':
    app.run (debug=False)
