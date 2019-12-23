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

people1, people2, people3, people4 = [], [], [], []
one, two, three, four = Lock(), Lock(), Lock(), Lock()
isFinished1, isFinished2, isFinished3, isFinished4 = False, False, False, False

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


def init4Fields():
    global people1, people2, people3, people4, powPeople, field, people, isFinished1, isFinished2, isFinished3, isFinished4
    isFinished1, isFinished2, isFinished3, isFinished4 = False, False, False, False
    people1, people2, people3, people4 = [], [], [], []
    x = random.randint(0, field[0] - 1)
    y = random.randint(0, field[1] - 1)
    for i in range(0, pow(2, powPeople)):
        while not canGoHere(x, y):
            x = random.randint(0, field[0] - 1)
            y = random.randint(0, field[1] - 1)
        people.append([x, y])
        if x < field[0] / 2:
            if y < field[1] / 2:
                people1.append([x, y])
            else:
                people3.append([x, y])
        else:
            if y < field[1] / 2:
                people2.append([x, y])
            else:
                people4.append([x, y])


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


def canGoHereField(x, y, nbField):
    global obstacles, people1, people2, people3, people4
    if x < 0 or y < 0:
        return False
    if nbField == 1:
        if [x, y] in people1:
            return False
    elif nbField == 2:
        if [x, y] in people2:
            return False
    elif nbField == 3:
        if [x, y] in people3:
            return False
    elif nbField == 4:
        if [x, y] in people4:
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
    while not isOnExit(p[0], p[1]):
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
    print(len(people))
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
        threadsList.append(Thread(target=GoToExit, args=(p, listLock)))
    for t in threadsList:
        t.start()
    for thread in threadsList:
        thread.join()


def getFieldFromPos(x, y):
    global field
    if x < field[0] / 2:
        if y < field[1] / 2:
            return 1
        else:
            return 3
    else:
        if y < field[1] / 2:
            return 2
        else:
            return 4


def getFieldFromPosAndDirection(direction, p):
    global field
    x, y = -1, -1
    if direction == "diagonal":
        x, y = p[0] - 1, p[1] - 1
    if direction == "horizontal":
        x, y = p[0] - 1, p[1]
    if direction == "vertical":
        x, y = p[0], p[1] - 1
    if x < 0 or y < 0:
        return getFieldFromPos(p[0], p[1])
    else:
        return getFieldFromPos(x, y)


def acquireLockFromFieldNumber(x):
    if x == 1:
        one.acquire()
        # print("one is locked")
    elif x == 2:
        two.acquire()
        # print("two is locked")
    elif x == 3:
        three.acquire()
        # print("three is locked")
    elif x == 4:
        four.acquire()
        # print("four is locked")


def releaseLockFromFieldNumber(x):
    if x == 1:
        one.release()
        # print("one is unlocked")
    elif x == 2:
        two.release()
        # print("two is unlocked")
    elif x == 3:
        three.release()
        # print("three is unlocked")
    elif x == 4:
        four.release()
        # print("four is unlocked")


def getListFromFieldNumber(x):
    global people1, people2, people3, people4
    if x == 1:
        return people1
    elif x == 2:
        return people2
    elif x == 3:
        return people3
    else:
        return people4


def doTheJob2(number):
    #print(str(number) + "->" + str(people1) + " " + str(people2) + " " + str(people3) + " " + str(people4))
    if number == 1:
        if len(people1) != 0:

            # print("one is locked")
            for p in people1:
                one.acquire()
                if isOnExit(p[0], p[1]):  # in front of the exit
                    people1.remove(p)
                    # print(str(number) +"->" + str(people1) + " " + str(people2) + " " + str(people3) + " " + str(people4))
                if canGoHereField(p[0] - 1, p[1] - 1, 1):  # can do a diagonal movement
                    # print(str(p) + "moving to [" + str(p[0]-1) + "," + str(p[1] - 1) + "]")
                    p[0], p[1] = p[0] - 1, p[1] - 1
                elif canGoHereField(p[0] - 1, p[1], 1):  # can do an horizontal movement
                    # print(str(p) + "moving to [" + str(p[0]-1) + "," + str(p[1]) + "]")
                    p[0], p[1] = p[0] - 1, p[1]
                elif canGoHereField(p[0], p[1] - 1, 1):  # can do a vertical movement
                    # print(str(p) + "moving to [" + str(p[0]) + "," + str(p[1] - 1) + "]")
                    p[0], p[1] = p[0], p[1] - 1
                one.release()
            # print("one is unlocked")
    else:
        if len(getListFromFieldNumber(number)) != 0:

            for p in getListFromFieldNumber(number):
                acquireLockFromFieldNumber(number)
                diagonalField = getFieldFromPosAndDirection("diagonal", p)
                horizontalField = getFieldFromPosAndDirection("horizontal", p)
                verticalField = getFieldFromPosAndDirection("vertical", p)
                if canGoHereField(p[0] - 1, p[1] - 1, diagonalField):  # can do a diagonal movement
                    if diagonalField == number:
                        # print(str(p) + "moving to [" + str(p[0]-1) + "," + str(p[1] - 1) + "]")
                        p[0], p[1] = p[0] - 1, p[1] - 1
                    else:  # p is changing field
                        acquireLockFromFieldNumber(diagonalField)
                        if canGoHereField(p[0] - 1, p[1] - 1, diagonalField):  # rechecking in case of something changed
                            # print(str(p) + "moving to [" + str(p[0]-1) + "," + str(p[1] - 1) + "] new field " + str(diagonalField))
                            getListFromFieldNumber(diagonalField).append(
                                [p[0] - 1, p[1] - 1])  # adding the person to the new field
                            getListFromFieldNumber(number).remove(p)  # removing the person from the field
                        releaseLockFromFieldNumber(diagonalField)

                elif canGoHereField(p[0] - 1, p[1], horizontalField):  # can do an horizontal movement
                    if horizontalField == number:
                        # print(str(p) + "moving to [" + str(p[0]-1) + "," + str(p[1]) + "]")
                        p[0], p[1] = p[0] - 1, p[1]
                    else:
                        acquireLockFromFieldNumber(horizontalField)
                        if canGoHereField(p[0] - 1, p[1],
                                          horizontalField):  # rechecking in case of something changed
                            # print(str(p) + "moving to [" + str(p[0]-1) + "," + str(p[1]) + "] new field " + str(horizontalField))

                            getListFromFieldNumber(horizontalField).append(
                                [p[0] - 1, p[1]])  # adding the person to the new field
                            getListFromFieldNumber(number).remove(p)  # removing the person from the field
                        releaseLockFromFieldNumber(horizontalField)

                elif canGoHereField(p[0], p[1] - 1, verticalField):  # can do a vertical movement
                    if verticalField == number:
                        # print(str(p) + "moving to [" + str(p[0]) + "," + str(p[1] - 1) + "]")
                        p[0], p[1] = p[0], p[1] - 1
                    else:
                        acquireLockFromFieldNumber(verticalField)
                        if canGoHereField(p[0], p[1] - 1, verticalField):  # rechecking in case of something changed
                            # print(str(p) + "moving to [" + str(p[0]) + "," + str(p[1] - 1) + "] new field " + str(verticalField))

                            getListFromFieldNumber(verticalField).append(
                                [p[0], p[1] - 1])  # adding the person to the new field
                            getListFromFieldNumber(number).remove(p)  # removing the person from the field
                        releaseLockFromFieldNumber(verticalField)
                releaseLockFromFieldNumber(number)


def subAlgorithm2(number):
    global people, people1, people2, people3, people4, one, two, three, four, exits, field, isFinished1, isFinished2, isFinished3, isFinished4
    # # Sort people by the distance as the crow flies from the exit
    if number == 4:
        while len(people4) != 0:
            doTheJob2(number)
        isFinished4 = True
    elif number == 3:
        while len(people3) != 0 or not isFinished4:
            doTheJob2(number)
        isFinished3 = True
    elif number == 2:
        while len(people2) != 0 or not isFinished4:
            doTheJob2(number)
        isFinished2 = True
    else:
        while len(people1) != 0 or not isFinished2 or not isFinished3 or not isFinished4:
            doTheJob2(number)
        isFinished1 = True
    #print(str(number) + "->" + str(people1) + " " + str(people2) + " " + str(people3) + " " + str(people4))
    #print(str(number) + " Finished " + str(isFinished1) + " " + str(isFinished2) + " " + str(isFinished3) + " " + str(isFinished4))

def algorithm2():
    t1 = Thread(target=subAlgorithm2, args=(1,))
    t2 = Thread(target=subAlgorithm2, args=(2,))
    t3 = Thread(target=subAlgorithm2, args=(3,))
    t4 = Thread(target=subAlgorithm2, args=(4,))

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    print("Fin hors thread" + str(people1) + " " + str(people2) + " " + str(people3) + " " + str(people4))


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
            if (scenario != 2):
                initialization()
            else:
                init4Fields()
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
    else:
        if (scenario != 2):
            initialization()
        else:
            init4Fields()
        if scenario == 0:
            algorithm0()
        if scenario == 1:
            algorithm1()
        if scenario == 2:
            algorithm2()
    exit(0)


if __name__ == "__main__":
    main()
