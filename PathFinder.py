import pygame
import sys
import random

# Define colors
WHITE, BLACK, GREEN, RED, BLUE = (255, 255, 255), (0, 0, 0), (0, 255, 0), (255, 0, 0), (0, 0, 255)

# Define grid dimensions
WIDTH, HEIGHT, ROWS, COLS = 300, 300, 5, 5
CELL_WIDTH, CELL_HEIGHT = WIDTH // COLS, HEIGHT // ROWS

# Initialize Pygame
pygame.init ()


class Maze:
    def __init__(self, rows, cols, start, goal):
        self.rows, self.cols, self.start, self.goal, self.agent_position = rows, cols, start, goal, start

    def reset_agent(self):
        self.agent_position = self.start

    def move_agent(self, action):
        row, col = self.agent_position
        if action == "UP" and row > 0:
            self.agent_position = (row - 1, col)
        elif action == "DOWN" and row < self.rows - 1:
            self.agent_position = (row + 1, col)
        elif action == "LEFT" and col > 0:
            self.agent_position = (row, col - 1)
        elif action == "RIGHT" and col < self.cols - 1:
            self.agent_position = (row, col + 1)

    def is_goal_reached(self):
        return self.agent_position == self.goal

    def distance_to_goal(self):
        return abs (self.agent_position [0] - self.goal [0]) + abs (self.agent_position [1] - self.goal [1])

    def draw(self, screen):
        for i in range (self.rows):
            for j in range (self.cols):
                rect = pygame.Rect (j * CELL_WIDTH, i * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
                color = WHITE
                if (i, j) == self.start:
                    color = BLUE
                elif (i, j) == self.goal:
                    color = RED
                elif (i, j) == self.agent_position:
                    color = GREEN
                pygame.draw.rect (screen, color, rect)
                pygame.draw.rect (screen, BLACK, rect, 1)


class QLearningAgent:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0):
        self.actions, self.learning_rate, self.discount_factor, self.exploration_rate, self.q_values = actions, learning_rate, discount_factor, exploration_rate, {}

    def get_q_value(self, state, action):
        return self.q_values.get ((state, action), 0.0)

    def choose_action(self, state):
        return random.choice (self.actions) if random.uniform (0, 1) < self.exploration_rate else max (self.actions,
                                                                                                       key=lambda
                                                                                                           a: self.get_q_value (
                                                                                                           state, a))

    def update_q_value(self, state, action, reward, next_state):
        best_next_action = max (self.actions, key=lambda a: self.get_q_value (next_state, a))
        current_q_value = self.get_q_value (state, action)
        next_q_value = self.get_q_value (next_state, best_next_action)
        self.q_values [(state, action)] = (1 - self.learning_rate) * current_q_value + self.learning_rate * (
                reward + self.discount_factor * next_q_value)

    def decay_exploration_rate(self, decay_rate):
        self.exploration_rate *= decay_rate


maze = Maze (ROWS, COLS, (0, 0), (ROWS - 1, COLS - 1))
actions = ["UP", "DOWN", "LEFT", "RIGHT"]
agent = QLearningAgent (actions)
screen = pygame.display.set_mode ((WIDTH, HEIGHT))
pygame.display.set_caption ("Q-Learning Maze Solver")

running = True
while running:
    for event in pygame.event.get ():
        if event.type == pygame.QUIT:
            running = False

    screen.fill (WHITE)
    maze.draw (screen)

    current_state = maze.agent_position
    action = agent.choose_action (current_state)
    maze.move_agent (action)
    reward = 1.0 / (maze.distance_to_goal () + 1)
    agent.update_q_value (current_state, action, reward, maze.agent_position)
    agent.decay_exploration_rate (0.99)

    pygame.display.flip ()
    pygame.time.delay (500)

    if maze.is_goal_reached ():
        maze.reset_agent ()

pygame.quit ()
sys.exit ()
