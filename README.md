# A* Maze Solver

This project is an implementation of A* pathfinding algorithm to solve a maze. The maze is represented as a grid of cells, where each self can either be open or a wall. The goal of the algorithm is to find the shortest path from a start self to a goal self.

## How it works

The* algorithm works by maintaining a priority queue of paths based on their cost and heuristic value. 
The heuristic value is an estimate of the cost from the current node to the goal. In this case, it's calculated as the Manhattan distance to the goal.

At each step, the algorithm chooses the path with the lowest total cost (path cost + heuristic value) and explores its neighbors. 
If a neighbor is the goal, it returns the path. If a neighbor is not the goal, it calculates the cost of the path to that neighbor and adds it to the queue. If it encounters a neighbor that it has seen before, it only updates the path if the new path is less expensive.

This process continues until the algorithm finds the goal or explores all reachable nodes. The result is the shortest path from the start to the goal, taking into account the cost of moving between nodes.

## Visualization

The program visualizes the maze and the pathfinding process using Pygame. The start self, goal self, walls, and path are all represented with different colors. The program also animates the pathfinding process, showing all the nodes that the algorithm explores.

## Usage

To run the program, execute the main Python script:

```bash
python A_Pathfinder.py
```

You can adjust the size of the maze, the number of walls, and the start and goal cells by modifying the constants at the top of the script.


# PathFinder
Pathfinder Algorithms 

# Maze Solver with an* Algorithm

This project implements a maze solver using an* algorithm.
The goal is to find the shortest path from the start to the goal in a maze with obstacles.

## Features

- **Maze Generation**: The maze is generated with random walls (obstacles) to create a challenging environment.

- **An* Algorithm**: The* algorithm is employed to find the optimal path from the start to the goal, considering the maze's layout.

- **Visualization**: The Pygame library is used to visualize the maze, pathfinding process, and the final solution.

## Requirements

- Python 3.x
- Pygame library (install with `pip install pygame`)

## Usage
Here is a short tutorial on how to run the A* Pathfinder algorithm using Git Bash:

### Running A* Pathfinder with Git Bash

1. **Clone the Repository**:
   First, you need to clone the repository to your local machine. Open Git Bash and run the following command:
   ```bash
   git clone https://github.com/DarkStarStrix/PathFinder.git
   cd PathFinder
   ```

2. **Ensure the Script is Executable**:
   Make sure the `run_a_pathfinder.sh` script is executable. You can use the following command in Git Bash:
   ```bash
   chmod +x run_a_pathfinder.sh
   ```

3. **Run the Script**:
   Execute the script to install the necessary dependencies and run the A* Pathfinder algorithm:
   ```bash
   ./run_a_pathfinder.sh
   ```

### Prerequisites

- **Python**: Ensure you have Python installed on your system.
- **pip**: Python package installer should be available.

This script will install the required Python packages and run the A* Pathfinder script, displaying the results using Pygame. Enjoy visualizing the pathfinding algorithm!

