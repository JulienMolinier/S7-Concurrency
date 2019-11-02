import random
import sys
import time
from statistics import mean

field = [512, 128]  # Field size
exits = [[0, 0], [0, 1], [1, 0]]  # Cells where people can get out
obstacles = [[50, 50, 60, 60],
             [100, 100, 110, 105]]  # Coordinates of obstacles [xmin, ymin, xmax, ymax]
people = []  # Coordinates of people
powPeople = 0  # 2^powPeople is the number of people on the field
measure = False  # True to compute execution time False otherwise
scenario = 0  # Scenario chosen


def getargs():
    global powPeople, measure, scenario
    i = 0
    for i in range(0, len(sys.argv)):
        arg = sys.argv[i]
        if arg == "-p":
            powPeople = int(sys.argv[i + 1])
        if arg == "-m":
            measure = True
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


def algorithm0():
    global people, exits, field

    while len(people) != 0:
        # Sort people by the distance as the crow flies from the exit
        people = sorted(people, key=lambda x: (pow(x[0], 2) + pow(x[1], 2)))

        for p in people:
            if p[0] == 0 and p[1] == 0:  # in front of the exit
                people.pop(0)
            if canGoHere(p[0] - 1, p[1] - 1):  # can do a diagonal movement
                p[0], p[1] = p[0] - 1, p[1] - 1
            elif canGoHere(p[0] - 1, p[1]):  # can do an horizontal movement
                p[0], p[1] = p[0] - 1, p[1]
            elif canGoHere(p[0], p[1] - 1):  # can do a vertical movement
                p[0], p[1] = p[0], p[1] - 1


def main():
    # Get command line arguments
    getargs()

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
