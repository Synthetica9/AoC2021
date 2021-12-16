from argparse import ArgumentParser, FileType
from sys import stdin

from itertools import product
from functools import cache, reduce
from operator import mul
from collections import defaultdict
from pprint import pprint


def parse(file):
    xs = []
    for line in file:
        line = line.strip()
        if not line:
            continue
        xs.append([int(x) for x in line])

    return xs


def safe_index(xs, i, j):
    try:
        return xs[i][j]
    except IndexError:
        return None


def neighbor_indexes(xs, i, j):
    return [
        (i + dx, j + dy)
        for (dx, dy) in [(0, 1), (1, 0), (-1, 0), (0, -1), (0, 0)]
        if safe_index(xs, i + dx, j + dy) is not None
    ]


def neighbors(xs, i, j):
    return [xs[a][b] for (a, b) in neighbor_indexes(xs, i, j)]


def part1(file):
    xs = parse(file)
    n = 0
    for i, row in enumerate(xs):
        for j, x in enumerate(row):
            nb = neighbors(xs, i, j)

            local_max = max(nb)
            if local_max == x:
                continue

            local_min = min(nb)

            if x == local_min:
                n += x + 1
                print(i, j, x, local_min)
    return n
    # 1756: too high
    # 566


def part2(file):
    xs = parse(file)
    basins = defaultdict(int)

    @cache
    def basin(i, j):
        if xs[i][j] == 9:
            return None
        this = xs[i][j]
        flow_to = min(neighbors(xs, i, j))
        if this == flow_to:
            return (i, j)

        sink = next(
            (a, b) for (a, b) in neighbor_indexes(xs, i, j) if xs[a][b] == flow_to
        )
        return basin(*sink)

    for i, row in enumerate(xs):
        for j, _ in enumerate(row):
            x = basin(i, j)
            basins[x] += 1

    del basins[None]
    largest = [
        v
        for k, v in sorted(
            basins.items(),
            key=lambda x: x[1],
            reverse=True,
        )
    ][:3]
    return reduce(mul, largest)


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        print(part2(file))


if __name__ == "__main__":
    main()
