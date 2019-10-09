import time

field = [512, 512]  # Field size
exits = [[0, 0], [0, 1], [1, 0]]  # Cells where people can get out
obstacles = [[50, 50, 60, 60],
             [100, 100, 110, 105]]  # Coordinates of obstacles [xmin, ymin, xmax, ymax]
people = []  # Coordinates of people


def main():
    # Start timer
    start_time = time.time()

    # End timer
    end_time = time.time()

    # Print execution time
    print("Execution time: %s s ---" % (end_time - start_time))
    exit(0)


if __name__ == "__main__":
    main()
