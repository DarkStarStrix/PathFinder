import heapq
from flask import Flask, send_file, render_template, url_for
from PIL import Image, ImageDraw
import io
import random

# Constants
WHITE, BLACK, GREEN, RED, BLUE, YELLOW = (255, 255, 255), (0, 0, 0), (0, 255, 0), (255, 0, 0), (0, 0, 255), (
    255, 255, 0)
WIDTH, HEIGHT, ROWS, COLS = 500, 500, 25, 25
CELL_WIDTH, CELL_HEIGHT = WIDTH // COLS, HEIGHT // ROWS
START, GOAL, NUM_WALLS = (0, 0), (ROWS - 1, COLS - 1), 100


class Maze:
    def __init__(self):
        self.agent_position = None
        self.img = None
        self.path = None
        self.visited = set ()
        self.walls = set ()
        self.borders = set ()
        self.start = START
        self.goal = GOAL
        self.rows = ROWS
        self.cols = COLS
        self.generate_walls ()

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
                    self.draw ()  # Redraw the maze after each step
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

    def generate_walls(self):
        self.walls = set ()
        self.agent_position = self.start
        self.path = None
        self.visited = set ()

        # Generate a simple path from the start to the goal
        simple_path = set ()
        for row in range (self.start [0], self.goal [0] + 1):
            simple_path.add ((row, self.start [1]))
        for col in range (self.start [1], self.goal [1] + 1):
            simple_path.add ((self.goal [0], col))

        # Generate walls, but avoid placing walls on the simple path
        for _ in range (NUM_WALLS):
            row = random.randint (0, self.rows - 1)
            col = random.randint (0, self.cols - 1)
            if (row, col) not in [self.start, self.goal] and (row, col) not in simple_path:
                self.walls.add ((row, col))

    def draw(self):
        self.img = Image.new ('RGB', (WIDTH, HEIGHT), WHITE)
        draw = ImageDraw.Draw (self.img)
        color_map = {
            "start": GREEN,
            "goal": RED,
            "wall": BLACK,
            "path": YELLOW,
            "visited": BLUE,
            "default": WHITE,
            "border": (128, 128, 128)  # Gray
        }
        for row in range (self.rows):
            for col in range (self.cols):
                cell_type = "default"
                if (row, col) in self.borders:
                    cell_type = "border"
                elif (row, col) in self.walls:
                    cell_type = "wall"
                elif (row, col) in self.visited:
                    cell_type = "visited"
                draw.rectangle ((col * CELL_WIDTH, row * CELL_HEIGHT, (col + 1) * CELL_WIDTH, (row + 1) * CELL_HEIGHT),
                                fill=color_map [cell_type])
        if self.path:
            for cell in self.path:
                draw.rectangle ((cell [1] * CELL_WIDTH, cell [0] * CELL_HEIGHT, (cell [1] + 1) * CELL_WIDTH,
                                 (cell [0] + 1) * CELL_HEIGHT), fill=color_map ["path"])
        draw.rectangle ((self.start [1] * CELL_WIDTH, self.start [0] * CELL_HEIGHT, (self.start [1] + 1) * CELL_WIDTH,
                         (self.start [0] + 1) * CELL_HEIGHT), fill=color_map ["start"])
        draw.rectangle ((self.goal [1] * CELL_WIDTH, self.goal [0] * CELL_HEIGHT, (self.goal [1] + 1) * CELL_WIDTH,
                         (self.goal [0] + 1) * CELL_HEIGHT), fill=color_map ["goal"])

        # Resize the image to 500x500 before saving
        self.img = self.img.resize ((500, 500))
        self.img.save ('maze.jpg', format='JPEG')

    def get_neighbors(self, cell):
        neighbors = []
        if cell [0] > 0 and (cell [0] - 1, cell [1]) not in self.walls and (cell [0] - 1, cell [1]) not in self.borders:
            neighbors.append ((cell [0] - 1, cell [1]))
        if cell [0] < self.rows - 1 and (cell [0] + 1, cell [1]) not in self.walls and (
                cell [0] + 1, cell [1]) not in self.borders:
            neighbors.append ((cell [0] + 1, cell [1]))
        if cell [1] > 0 and (cell [0], cell [1] - 1) not in self.walls and (cell [0], cell [1] - 1) not in self.borders:
            neighbors.append ((cell [0], cell [1] - 1))
        if cell [1] < self.cols - 1 and (cell [0], cell [1] + 1) not in self.walls and (
                cell [0], cell [1] + 1) not in self.borders:
            neighbors.append ((cell [0], cell [1] + 1))
        return neighbors


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


if __name__ == '__main__':
    app.run (debug=True)
