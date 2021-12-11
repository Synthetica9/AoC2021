from argparse import ArgumentParser, FileType
from sys import stdin

from itertools import product, count


def parse(file):
    grid = {}
    for i, line in enumerate(file):
        line = line.strip()
        if not line:
            continue

        for j, c in enumerate(line):
            grid[(i, j)] = int(c)
    return grid


def step(grid):
    grid = {k: (v + 1) for k, v in grid.items()}

    flashers = set()
    has_flashed = True

    while has_flashed:
        has_flashed = False
        # print(flashers)
        for (x, y), v in grid.items():
            if v > 9 and (x, y) not in flashers:
                has_flashed = True
                flashers.add((x, y))

                for dx, dy in product([-1, 0, 1], repeat=2):
                    if (dx, dy) == (0, 0) or (x + dx, y + dy) not in grid:
                        continue
                    grid[x + dx, y + dy] += 1

    for flasher in flashers:
        grid[flasher] = 0

    return len(flashers), grid


def solve(file):
    grid = parse(file)
    # score = 0
    for s in count(1):
        # print(f"After step {s}:")
        # print_debug(grid)
        # print()

        n, grid = step(grid)
        # score += n
        if n == 100:
            break

    return s


# def print_debug(grid):
#     for i in range(10):
#         for j in range(10):
#             print(grid[i, j], end="")
#         print()


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
