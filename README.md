# A* Maze Solver

This project is an implementation of A* pathfinding algorithm to solve a maze. The maze is represented as a grid of cells, where each cell can either be open or a wall. The goal of the algorithm is to find the shortest path from a start cell to a goal cell.

## How it works

The* algorithm works by maintaining a priority queue of paths based on their cost and heuristic value. 
The heuristic value is an estimate of the cost from the current node to the goal. In this case, it's calculated as the Manhattan distance to the goal.

At each step, the algorithm chooses the path with the lowest total cost (path cost + heuristic value) and explores its neighbors. 
If a neighbor is the goal, it returns the path. If a neighbor is not the goal, it calculates the cost of the path to that neighbor and adds it to the queue. If it encounters a neighbor that it has seen before, it only updates the path if the new path is cheaper.

This process continues until the algorithm finds the goal or explores all reachable nodes. The result is the shortest path from the start to the goal, taking into account the cost of moving between nodes.

## Visualization

The program visualizes the maze and the pathfinding process using Pygame. The start cell, goal cell, walls, and path are all represented with different colors. The program also animates the pathfinding process, showing all the nodes that the algorithm explores.

## Usage

To run the program, execute the main Python script:

```bash
python A_Pathfinder.py
```

You can adjust the size of the maze, the number of walls, and the start and goal cells by modifying the constants at the top of the script.