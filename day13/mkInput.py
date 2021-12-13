import numpy
from argparse import ArgumentParser, FileType
from sys import stdin, stdout
import random


def getopts():
    opts = ArgumentParser()
    opts.add_argument("file", nargs="?", default=stdin, type=FileType("r"))
    opts.add_argument("--output", "-o", type=FileType("w"), default=stdout)
    opts.add_argument("--seed", "-s", type=int, default=None)
    opts.add_argument("--folds", "-f", type=int, default=10)
    return opts.parse_args()


def parse(file):
    dots = set()
    for y, row in enumerate(file):
        for x, c in enumerate(row):
            if c != " ":
                dots.add((x, y))
    return dots


def add_fold(dots, axis, value):
    if axis == "x":
        new_dots = set()
        for dot in dots:
            action = random.randint(0, 3)
            if action < 3:
                new_dots.add(dot)
            if action > 1:
                new_dots.add(((2 * value - dot[0]), dot[1]))
        return new_dots

    elif axis == "y":
        return transpose(add_fold(transpose(dots), "x", value))
    else:
        assert False


def transpose(dots):
    return {d[::-1] for d in dots}


def add_folds(dots, n_folds):
    actions = []
    for i in range(n_folds):
        axis = random.randrange(2)
        value = max(p[axis] for p in dots)
        value += random.randint(1, value)
        axis = "xy"[axis]
        actions.append((axis, value))
        dots = add_fold(dots, axis, value)
    return dots, actions[::-1]


def main():
    opts = getopts()

    if opts.seed is not None:
        random.seed(opts.seed)

    dots = parse(opts.file)

    dots, actions = add_folds(dots, opts.folds)

    def out(*args, **kwargs):
        print(*args, file=opts.output, **kwargs)

    for dot in sorted(dots):
        out(f"{dot[0]},{dot[1]}")
    out()
    for action in actions:
        out(f"fold along {action[0]}={action[1]}")


if __name__ == "__main__":
    main()
