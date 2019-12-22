import os
import random
import sys
import time
from statistics import mean
from threading import Lock
from threading import Thread

import pygame

field = [512, 128]  # Field size
exits = [[0, 0], [0, 1], [1, 0]]  # Cells where people can get out
obstacles = [[50, 50, 60, 60], [20, 20, 45, 45], [80, 20, 95, 126], [200, 5, 300, 50],
             [100, 100, 110, 105]]  # Coordinates of obstacles [xmin, ymin, xmax, ymax]
people = []  # Coordinates of people
powPeople = 0  # 2^powPeople is the number of people on the field
measure = False  # True to compute execution time False otherwise
display = False
scenario = 0  # Scenario chosen

space_on_left = 50
space_above = 200

list1, list2, list3, list4 = [], [], [], []
one, two, three, four = Lock(), Lock(), Lock(), Lock()

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (space_on_left, space_above)


def getargs():
    global powPeople, measure, scenario, display
    for i in range(0, len(sys.argv)):
        arg = sys.argv[i]
        if arg == "-p":
            powPeople = int(sys.argv[i + 1])
        if arg == "-m":
            measure = True
        if arg == "-v":
            display = True
        if arg == "-t":
            scenario = int(sys.argv[i + 1])


def initialization():
    global people, powPeople, field
    x = random.randint(0, field[0] - 1)
    y = random.randint(0, field[1] - 1)
    for i in range(0, pow(2, powPeople)):
        while not canGoHere(x, y):
            x = random.randint(0, field[0] - 1)
            y = random.randint(0, field[1] - 1)
        people.append([x, y])


def canGoHere(x, y):
    global obstacles, people
    if x < 0 or y < 0:
        return False
    if [x, y] in people:
        return False
    for o in obstacles:
        if o[0] <= x < o[2] and o[1] <= y < o[3]:
            return False
    return True


def isOnExit(x, y):
    global exits
    for e in exits:
        if e[0] == x and e[1] == y:
            return True
    return False


def doOneStep():
    global people, exits, field
    for p in people:
        if isOnExit(p[0], p[1]):  # in front of the exit
            people.pop(0)
        if canGoHere(p[0] - 1, p[1] - 1):  # can do a diagonal movement
            p[0], p[1] = p[0] - 1, p[1] - 1
        elif canGoHere(p[0] - 1, p[1]):  # can do an horizontal movement
            p[0], p[1] = p[0] - 1, p[1]
        elif canGoHere(p[0], p[1] - 1):  # can do a vertical movement
            p[0], p[1] = p[0], p[1] - 1

def GoToExit(p, lock):
    global people, exits, field
    while(not isOnExit(p[0],p[1])):
        lock.acquire()
        if canGoHere(p[0] - 1, p[1] - 1):  # can do a diagonal movement
            p[0], p[1] = p[0] - 1, p[1] - 1
        elif canGoHere(p[0] - 1, p[1]):  # can do an horizontal movement
            p[0], p[1] = p[0] - 1, p[1]
        elif canGoHere(p[0], p[1] - 1):  # can do a vertical movement
            p[0], p[1] = p[0], p[1] - 1
        lock.release()
    lock.acquire()
    people.remove(p)
    lock.release()


def algorithm0():
    global people

    # Sort people by the distance as the crow flies from the exit
    people = sorted(people, key=lambda x: (pow(x[0], 2) + pow(x[1], 2)))

    while len(people) != 0:
        doOneStep()


def algorithm1():
    global people
    listLock = Lock()
    threadsList = []
    for p in people:
        threadsList.append(Thread(target=GoToExit, args=(p,listLock)))
    for t in threadsList:
        t.start()
    for thread in threadsList:
        thread.join()


def subAlgorithm2(number):
    global people, list1, list2, list3, list4, one, two, three, four, exits, field

    # # Sort people by the distance as the crow flies from the exit
    # args = sorted(args, key=lambda x: (pow(x[0], 2) + pow(x[1], 2)))


def algorithm2():
    global people, list1, list2, list3, list4

    for p in people:
        if p[0] < 256:
            if p[1] < 64:
                list1.append(p)
            else:
                list3.append(p)
        elif p[1] < 64:
            list2.append(p)
        else:
            list4.append(p)

    t1 = Thread(target=subAlgorithm2, args=[1])
    t2 = Thread(target=subAlgorithm2, args=[2])
    t3 = Thread(target=subAlgorithm2, args=[3])
    t4 = Thread(target=subAlgorithm2, args=[4])

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()


def draw(window):
    cell_size = 3
    window.fill((0, 0, 0))
    for p in people:
        pygame.draw.rect(window, (0, 255, 0),
                         (p[0] * cell_size, p[1] * cell_size, cell_size, cell_size), 0)
    for o in obstacles:
        pygame.draw.rect(window, (255, 0, 0),
                         (o[0] * cell_size, o[1] * cell_size, (o[2] - o[0]) * cell_size, (o[3] - o[1]) * cell_size), 0)
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
        timeCPUval = []
        for i in range(0, 5):

            # Initialize field
            initialization()

            start_time = time.time()
            start_timeCPU = time.process_time()
            if scenario == 0:
                algorithm0()
            if scenario == 1:
                algorithm1()
            if scenario == 2:
                algorithm2()
            end_time = time.time()
            end_timeCPU = time.process_time()
            timeval.append(end_time - start_time)
            timeCPUval.append(end_timeCPU - start_timeCPU)

        timeval.sort()
        timeCPUval.sort()
        timeval.pop(0)
        timeCPUval.pop(0)
        timeval.pop()
        timeCPUval.pop()
        print("Execution time: %ss" % (mean(timeval)))
        print("CPU time: %ss" % (mean(timeCPUval)))

    exit(0)


if __name__ == "__main__":
    main()
