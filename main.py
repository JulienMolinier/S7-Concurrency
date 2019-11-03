import os
import random
import sys
import time
from statistics import mean

import pygame

field = [512, 128]  # Field size
exits = [[0, 0], [0, 1], [1, 0]]  # Cells where people can get out
obstacles = [[50, 50, 60, 60],
             [100, 100, 110, 105]]  # Coordinates of obstacles [xmin, ymin, xmax, ymax]
grid = []
people = []  # Coordinates of people
powPeople = 0  # 2^powPeople is the number of people on the field
measure = False  # True to compute execution time False otherwise
display = False
modifiedCell = []
scenario = 0  # Scenario chosen

space_on_left = 50
space_above = 200

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (space_on_left, space_above)


def getargs():
    global powPeople, measure, scenario, display
    i = 0
    for i in range(0, len(sys.argv)):
        arg = sys.argv[i]
        if arg == "-p":
            powPeople = int(sys.argv[i + 1])
        if arg == "-m":
            measure = True
        if arg == "-v":
            display = True
        if arg == "-t":
            scenario = sys.argv[i + 1]


def initialization():
    global people, powPeople, field
    x = random.randint(0, field[0] - 1)
    y = random.randint(0, field[1] - 1)
    for i in range(0, pow(2, powPeople)):
        while not canGoHere(x, y):
            x = random.randint(0, field[0] - 1)
            y = random.randint(0, field[1] - 1)
        people.append([x, y])
    for x in range(512):
        grid.append([])
        for y in range(128):
            grid[x].append(0)
            if [x, y] in people:
                grid[x][y] = 1
            for o in obstacles:
                if o[0] <= x <= o[2] and o[1] <= y <= o[3]:
                    grid[x][y] = 2


def canGoHere(x, y):
    global obstacles, people
    if x < 0 or y < 0:
        return False
    if [x, y] in people:
        return False
    for o in obstacles:
        if o[0] <= x <= o[2] and o[1] <= y <= o[3]:
            return False
    return True


def doOneStep():
    global people, exits, field
    # Sort people by the distance as the crow flies from the exit
    people = sorted(people, key=lambda x: (pow(x[0], 2) + pow(x[1], 2)))

    for p in people:
        if p[0] == 0 and p[1] == 0:  # in front of the exit
            grid[0][0] = 0
            modifiedCell.append([0, 0])
            people.pop(0)
        if canGoHere(p[0] - 1, p[1] - 1):  # can do a diagonal movement
            grid[p[0]][p[1]] = 0
            modifiedCell.append([p[0], p[1]])
            p[0], p[1] = p[0] - 1, p[1] - 1
            grid[p[0]][p[1]] = 1
            modifiedCell.append([p[0], p[1]])
        elif canGoHere(p[0] - 1, p[1]):  # can do an horizontal movement
            grid[p[0]][p[1]] = 0
            modifiedCell.append([p[0], p[1]])
            p[0], p[1] = p[0] - 1, p[1]
            grid[p[0]][p[1]] = 1
            modifiedCell.append([p[0], p[1]])
        elif canGoHere(p[0], p[1] - 1):  # can do a vertical movement
            grid[p[0]][p[1]] = 0
            modifiedCell.append([p[0], p[1]])
            p[0], p[1] = p[0], p[1] - 1
            grid[p[0]][p[1]] = 1
            modifiedCell.append([p[0], p[1]])


def algorithm0():
    global people, exits, field
    while len(people) != 0:
        doOneStep()


def draw(window):
    global modifiedCell
    cell_size = 3
    window.fill((0, 0, 0))
    start_time = time.time()
    color = (0, 0, 0)
    for changedCells in modifiedCell:
        if grid[changedCells[0]][changedCells[1]] == 1:
            color = (0, 255, 0)
        if grid[changedCells[0]][changedCells[1]] == 0:
            color = (0, 0, 0)
        pygame.draw.rect(window, color, (changedCells[0] * cell_size, changedCells[1] * cell_size, cell_size, cell_size), 0)
    modifiedCell = []
    for o in obstacles:
        pygame.draw.rect(window, (255, 0, 0),
                         (o[0] * cell_size, o[1] * cell_size, (o[2] - o[0]) * cell_size, (o[3] - o[1]) * cell_size), 0)
    # for x in range(512):
    #     for y in range(128):
    #         color = (0, 0, 0)
    #         if grid[x][y] == 1:
    #             color = (0, 255, 0)
    #         elif grid[x][y] == 2:
    #             color = (255, 0, 0)
    #         pygame.draw.rect(window, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)
    end_time = time.time()
    print("Execution time: %ss" % (end_time - start_time))
    pygame.display.update()


def main():
    # Get command line arguments
    getargs()
    if display:
        initialization()
        pygame.init()
        window = pygame.display.set_mode((1536, 384), 0, 32)
        pygame.display.set_caption("Display")
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            doOneStep()
            draw(window)
            clock.tick(60)

    if measure:
        i = 0
        timeval = []
        for i in range(0, 5):

            # Initialize field
            initialization()

            start_time = time.time()
            if scenario == 0:
                algorithm0()
            end_time = time.time()
            timeval.append(end_time - start_time)

        timeval.sort()
        timeval.pop(0)
        timeval.pop()
        print("Execution time: %ss" % (mean(timeval)))

    exit(0)


if __name__ == "__main__":
    main()
