from argparse import ArgumentParser, FileType
from sys import stdin
import heapq
from pprint import pprint


def parse(file):
    grid = []
    for line in file:
        line = line.strip()
        if not line:
            continue

        grid.append([int(x) for x in line])
    return grid


def extend(grid, factor):
    new_grid = []
    for line in grid:
        new_grid.append([])
        for i in range(factor):
            new_grid[-1].extend([(n + i - 1) % 9 + 1 for n in line])

    template = new_grid.copy()
    for i in range(1, factor):
        for line in template:
            new_grid.append([(n + i - 1) % 9 + 1 for n in line])
    return new_grid


def is_index(xs, i, j):
    return 0 <= i < len(xs) and 0 <= j < len(xs[i])


def neighbor_indexes(xs, p):
    i, j = p
    return (
        (i + dx, j + dy)
        for (dx, dy) in [(0, 1), (1, 0), (-1, 0), (0, -1)]
        if is_index(xs, i + dx, j + dy)
    )


def search(dest, grid):
    frontier = []
    heapq.heappush(frontier, (0, (0, 0)))
    visited = set()
    while frontier:
        danger, curr = heapq.heappop(frontier)
        if curr in visited:
            continue
        visited.add(curr)
        if curr == dest:
            return danger

        for neighbor in neighbor_indexes(grid, curr):
            if neighbor in visited:
                continue
            x, y = neighbor
            heapq.heappush(frontier, (danger + grid[y][x], neighbor))
    assert False


def solve(file, factor=1):
    grid = parse(file)
    grid = extend(grid, factor)
    dest = len(grid) - 1, len(grid[0]) - 1
    return search(dest, grid)


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    opts.add_argument("--extend", type=int, default=1)
    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        print(solve(file, opts.extend))


if __name__ == "__main__":
    main()
