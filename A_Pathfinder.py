import pygame
import sys
import heapq
import random
import numpy as np
from numba import jit
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

# Constants
WINDOW_SIZE = 800
CELL_SIZE = 16
GRID_SIZE = WINDOW_SIZE // CELL_SIZE
ANIMATION_SPEED = 10
MAX_THREADS = 4
SEARCH_BATCH_SIZE = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (147, 0, 211)
VISITED_COLOR = (180, 180, 250)
PATH_COLOR = (255, 165, 0)
SECONDARY_PATH_COLOR = (100, 200, 100)


@dataclass (order=True)
class PrioritizedCell:
    priority: float
    cell: Any = field (compare=False)
    cost: float = field (compare=False)


@jit (nopython=True)
def calculate_heuristic(current_pos, goal_pos, weight=1.0):
    dx = abs (current_pos [0] - goal_pos [0])
    dy = abs (current_pos [1] - goal_pos [1])
    return weight * (dx + dy) + (1.414 - 2) * min (dx, dy)


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False
        self.in_path = False
        self.in_secondary_path = False
        self.is_start = False
        self.is_goal = False
        self.being_explored = False

    def __eq__(self, other):
        if not isinstance (other, Cell):
            return False
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash ((self.row, self.col))


class Maze:
    def __init__(self):
        self.grid = [[Cell (i, j) for j in range (GRID_SIZE)] for i in range (GRID_SIZE)]
        self.start = self.grid [1] [1]
        self.goal = self.grid [GRID_SIZE - 2] [GRID_SIZE - 2]
        self.start.is_start = True
        self.goal.is_goal = True
        self.path = []
        self.explored = set ()
        self.lock = threading.Lock ()

    def _get_valid_neighbors(self, row, col):
        """Get valid neighbors for maze generation"""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dy, dx in directions:
            new_row, new_col = row + dy, col + dx
            if (0 <= new_row < GRID_SIZE and
                    0 <= new_col < GRID_SIZE and
                    not self.grid [new_row] [new_col].visited):
                neighbors.append ((new_row, new_col))
        return neighbors

    def generate_section(self, start_row, start_col, end_row, end_col):
        """Generate a section of the maze using iterative DFS"""
        stack = [(start_row, start_col)]
        self.grid [start_row] [start_col].visited = True

        while stack:
            current_row, current_col = stack [-1]
            neighbors = self._get_valid_neighbors (current_row, current_col)

            if not neighbors:
                stack.pop ()
                continue

            next_row, next_col = random.choice (neighbors)

            # Remove walls between current and next cell
            with self.lock:
                if next_row > current_row:  # Moving down
                    self.grid [current_row] [current_col].walls ['bottom'] = False
                    self.grid [next_row] [next_col].walls ['top'] = False
                elif next_row < current_row:  # Moving up
                    self.grid [current_row] [current_col].walls ['top'] = False
                    self.grid [next_row] [next_col].walls ['bottom'] = False
                elif next_col > current_col:  # Moving right
                    self.grid [current_row] [current_col].walls ['right'] = False
                    self.grid [next_row] [next_col].walls ['left'] = False
                else:  # Moving left
                    self.grid [current_row] [current_col].walls ['left'] = False
                    self.grid [next_row] [next_col].walls ['right'] = False

                self.grid [next_row] [next_col].visited = True
                stack.append ((next_row, next_col))

    def generate_maze_parallel(self, screen):
        """Generate maze using multiple threads"""
        # Reset visited states
        for row in self.grid:
            for cell in row:
                cell.visited = False

        # Define sections for parallel generation
        sections = []
        section_size = GRID_SIZE // 2

        for i in range (0, GRID_SIZE - 1, section_size):
            for j in range (0, GRID_SIZE - 1, section_size):
                sections.append ((
                    i, j,
                    min (i + section_size, GRID_SIZE - 1),
                    min (j + section_size, GRID_SIZE - 1)
                ))

        # Generate sections in parallel
        with ThreadPoolExecutor (max_workers=MAX_THREADS) as executor:
            futures = []
            for start_row, start_col, end_row, end_col in sections:
                futures.append (
                    executor.submit (self.generate_section, start_row, start_col, end_row, end_col)
                )

            for future in futures:
                future.result ()

        # Connect sections
        self._connect_sections (sections)

        # Reset visited states for pathfinding
        for row in self.grid:
            for cell in row:
                cell.visited = False

        self.draw (screen)

    def _connect_sections(self, sections):
        """Connect different sections of the maze"""
        for i in range (len (sections) - 1):
            section1 = sections [i]
            section2 = sections [i + 1]

            # Create random connections
            connection_points = random.randint (1, 3)
            for _ in range (connection_points):
                if section1 [2] == section2 [0]:  # Vertical connection
                    col = random.randint (section1 [1], section1 [3])
                    self.grid [section1 [2]] [col].walls ['bottom'] = False
                    self.grid [section2 [0]] [col].walls ['top'] = False
                else:  # Horizontal connection
                    row = random.randint (section1 [0], section1 [2])
                    self.grid [row] [section1 [3]].walls ['right'] = False
                    self.grid [row] [section2 [1]].walls ['left'] = False

    def bidirectional_a_star(self, screen):
        """Improved A* search with bidirectional search"""
        forward_queue = []
        backward_queue = []

        heapq.heappush (forward_queue, PrioritizedCell (0, self.start, 0))
        heapq.heappush (backward_queue, PrioritizedCell (0, self.goal, 0))

        forward_visited = {self.start: (None, 0)}
        backward_visited = {self.goal: (None, 0)}

        while forward_queue and backward_queue:
            # Process forward search
            current = self._process_search_batch (
                forward_queue, forward_visited, backward_visited,
                self.goal, screen, True
            )

            if current:
                self._reconstruct_bidirectional_path (
                    current, forward_visited, backward_visited, screen
                )
                return

            # Process backward search
            current = self._process_search_batch (
                backward_queue, backward_visited, forward_visited,
                self.start, screen, False
            )

            if current:
                self._reconstruct_bidirectional_path (
                    current, forward_visited, backward_visited, screen
                )
                return

    def _process_search_batch(self, queue, visited, other_visited, goal, screen, is_forward):
        """Process a batch of cells in the search"""
        for _ in range (SEARCH_BATCH_SIZE):
            if not queue:
                return None

            current = heapq.heappop (queue).cell
            current_cost = visited [current] [1]

            if current in other_visited:
                return current

            current.being_explored = True
            self.draw (screen)
            pygame.display.flip ()
            pygame.time.delay (ANIMATION_SPEED)
            current.being_explored = False

            for neighbor in self.get_valid_neighbors (current):
                new_cost = current_cost + 1
                if neighbor not in visited or new_cost < visited [neighbor] [1]:
                    visited [neighbor] = (current, new_cost)
                    priority = new_cost + calculate_heuristic (
                        (neighbor.row, neighbor.col),
                        (goal.row, goal.col)
                    )
                    heapq.heappush (queue, PrioritizedCell (priority, neighbor, new_cost))
                    neighbor.visited = True
                    self.explored.add (neighbor)

        return None

    def _reconstruct_bidirectional_path(self, meeting_point, forward_visited, backward_visited, screen):
        """Reconstruct the path from both directions"""
        # Forward path
        current = meeting_point
        while current in forward_visited and forward_visited [current] [0] is not None:
            current.in_path = True
            current = forward_visited [current] [0]
            self.path.append (current)
            self.draw (screen)
            pygame.display.flip ()
            pygame.time.delay (ANIMATION_SPEED)

        # Backward path
        current = meeting_point
        while current in backward_visited and backward_visited [current] [0] is not None:
            current.in_secondary_path = True
            current = backward_visited [current] [0]
            self.path.append (current)
            self.draw (screen)
            pygame.display.flip ()
            pygame.time.delay (ANIMATION_SPEED)

    def get_valid_neighbors(self, cell):
        """Get valid neighbors considering walls"""
        neighbors = []
        if not cell.walls ['top'] and cell.row > 0:
            neighbors.append (self.grid [cell.row - 1] [cell.col])
        if not cell.walls ['right'] and cell.col < GRID_SIZE - 1:
            neighbors.append (self.grid [cell.row] [cell.col + 1])
        if not cell.walls ['bottom'] and cell.row < GRID_SIZE - 1:
            neighbors.append (self.grid [cell.row + 1] [cell.col])
        if not cell.walls ['left'] and cell.col > 0:
            neighbors.append (self.grid [cell.row] [cell.col - 1])
        return neighbors

    def draw(self, screen):
        """Draw the maze with improved visuals"""
        screen.fill (WHITE)

        for row in self.grid:
            for cell in row:
                x = cell.col * CELL_SIZE
                y = cell.row * CELL_SIZE

                # Draw a cell background
                if cell.is_start:
                    pygame.draw.rect (screen, BLUE, (x, y, CELL_SIZE, CELL_SIZE))
                elif cell.is_goal:
                    pygame.draw.rect (screen, RED, (x, y, CELL_SIZE, CELL_SIZE))
                elif cell.in_path:
                    pygame.draw.rect (screen, PATH_COLOR, (x, y, CELL_SIZE, CELL_SIZE))
                elif cell.in_secondary_path:
                    pygame.draw.rect (screen, SECONDARY_PATH_COLOR, (x, y, CELL_SIZE, CELL_SIZE))
                elif cell.being_explored:
                    pygame.draw.rect (screen, PURPLE, (x, y, CELL_SIZE, CELL_SIZE))
                elif cell in self.explored:
                    pygame.draw.rect (screen, VISITED_COLOR, (x, y, CELL_SIZE, CELL_SIZE))

                # Draw walls
                if cell.walls ['top']:
                    pygame.draw.line (screen, BLACK, (x, y), (x + CELL_SIZE, y), 2)
                if cell.walls ['right']:
                    pygame.draw.line (screen, BLACK, (x + CELL_SIZE, y),
                                      (x + CELL_SIZE, y + CELL_SIZE), 2)
                if cell.walls ['bottom']:
                    pygame.draw.line (screen, BLACK, (x, y + CELL_SIZE),
                                      (x + CELL_SIZE, y + CELL_SIZE), 2)
                if cell.walls ['left']:
                    pygame.draw.line (screen, BLACK, (x, y), (x, y + CELL_SIZE), 2)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Advanced Maze Solver with Bidirectional A*")

    maze = Maze()
    maze_generated = False
    path_found = False

    # Initialize font
    font = pygame.font.SysFont(None, 24)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not maze_generated:
                    maze.generate_maze_parallel(screen)
                    maze_generated = True
                elif event.key == pygame.K_RETURN and maze_generated and not path_found:
                    maze.bidirectional_a_star(screen)
                    path_found = True
                elif event.key == pygame.K_r:
                    maze = Maze()
                    maze_generated = False
                    path_found = False

        maze.draw(screen)

        # Render tooltips
        tooltips = [
            "Press SPACE to generate the maze",
            "Press ENTER to run the pathfinder",
            "Press R to reset"
        ]
        box_width = 300
        box_height = 100
        box_x = (WINDOW_SIZE - box_width) // 2
        box_y = WINDOW_SIZE - box_height - 10

        # Draw the tooltip box
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 2)

        for i, tooltip in enumerate(tooltips):
            text_surface = font.render(tooltip, True, BLACK)
            screen.blit(text_surface, (box_x + 10, box_y + 10 + i * 30))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main ()
