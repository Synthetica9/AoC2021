from argparse import ArgumentParser, FileType
from sys import stdin

from itertools import product

from functools import cache

RANGE = 1
N_BITS = (2 * RANGE + 1) ** 2


def parse(file):
    repl = [x == "#" for x in next(file).strip()]
    assert len(repl) == 2 ** N_BITS

    grid = set()
    for x, line in enumerate(file):
        for y, c in enumerate(line):
            if c == "#":
                grid.add((x, y))

    return repl, grid


@cache
def neighbors(p):
    x, y = p
    return [(x + dx, y + dy) for dx, dy in product([-1, 0, 1], repeat=2)]


def bounds(grid):
    x = lambda p: p[0]
    y = lambda p: p[1]

    min_x = min(map(x, grid))
    max_x = max(map(x, grid))

    min_y = min(map(y, grid))
    max_y = max(map(y, grid))

    return (min_x, min_y), (max_x, max_y)


def to_int(grid, points, neg=False):
    bitstring = "".join(str(int((p in grid) ^ neg)) for p in points)
    return int(bitstring, 2)


def solve(file, passes=50):
    repl, grid = parse(file)

    @cache
    def get_point(t, x, y):
        if t == 0:
            return (x, y) in grid

        n = sum(
            1 << c
            for c, p in enumerate(reversed(neighbors((x, y))))
            if get_point(t - 1, *p)
        )

        return repl[n]

    (min_x, min_y), (max_x, max_y) = bounds(grid)
    return sum(
        get_point(passes, x, y)
        for x in range(min_x - passes, max_x + passes + 1)
        for y in range(min_y - passes, max_y + passes + 1)
    )


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    opts.add_argument("--passes", default=2, type=int)
    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        print(solve(file, opts.passes))


if __name__ == "__main__":
    main()
