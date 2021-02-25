import os


def output(filename, cost, assignment):
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    with open("outputs/{}".format(filename), "w+") as f:
        f.write(str(cost) + "\n")
        for num in assignment:
            f.write(str(num) + "\n")


def read(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = [int(x[:-1]) for x in f.readlines()]

            return data[0], data[1:]
