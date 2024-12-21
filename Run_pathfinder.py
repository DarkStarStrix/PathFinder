import pygame
from A_Pathfinder import Maze


def main():
    pygame.init ()
    window_size = 800
    screen = pygame.display.set_mode ((window_size, window_size))
    pygame.display.set_caption ("A* Pathfinder")

    maze = Maze ()
    maze.generate_maze_parallel (screen)
    maze.bidirectional_a_star (screen)

    running = True
    while running:
        for event in pygame.event.get ():
            if event.type == pygame.QUIT:
                running = False

        screen.fill ((255, 255, 255))
        maze.draw (screen)
        pygame.display.flip ()

    pygame.quit ()


if __name__ == "__main__":
    main ()
