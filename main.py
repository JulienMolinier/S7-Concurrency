import sys
import time
from statistics import mean

field = [512, 512]  # Field size
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
            powPeople = sys.argv[i + 1]
        if arg == "-m":
            measure = True
        if arg == "-t":
            scenario = sys.argv[i + 1]


def initialization():
    global people, powPeople


def algorithm():
    global scenario


def main():
    # Get command line arguments
    getargs()
    initialization()

    if measure:
        i = 0
        timevalues = []
        for i in range(0, 5):
            start_time = time.time()
            algorithm()
            end_time = time.time()
            timevalues.append(end_time - start_time)

        timevalues.sort()
        timevalues.pop(0)
        timevalues.pop()
        print("Execution time: %ss" % (mean(timevalues)))

    exit(0)


if __name__ == "__main__":
    main()
