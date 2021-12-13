from argparse import ArgumentParser, FileType
from sys import stdin


def fold(dots, axis, value):
    new_dots = set()
    for dot in dots:
        if axis == "y":
            dot = (dot[0], value - abs(dot[1] - value))
        elif axis == "x":
            dot = (value - abs(dot[0] - value), dot[1])
        else:
            assert False
        new_dots.add(dot)
    return new_dots


def solve(file):
    dots = set()
    for line in file:
        line = line.strip()
        if not line:
            break
        x, y = line.split(",")
        dots.add((int(x), int(y)))

    for line in file:
        line = line.strip()
        if not line:
            continue
        _, instr = line.rsplit(" ", 1)
        assert _ == "fold along"

        axis, value = instr.split("=")
        value = int(value)
        dots = fold(dots, axis, value)
        print(len(dots))

    max_x = max(p[0] for p in dots)
    max_y = max(p[1] for p in dots)
    for y in range(max_y):
        print("".join("#" if (x, y) in dots else " " for x in range(max_x)))

    return len(dots)


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        print(solve(file))


if __name__ == "__main__":
    main()
