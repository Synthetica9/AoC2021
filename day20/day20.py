from argparse import ArgumentParser, FileType
from sys import stdin

from itertools import product
from functools import cache

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(arg, *args, **kwargs):
        return arg

RANGE = 1
N_BITS = (2 * RANGE + 1) ** 2


def stripped(file):
    for line in file:
        line = line.strip()
        if not line:
            continue
        yield line


def parse(file):
    repl = [x == "#" for x in next(file).strip()]
    assert len(repl) == 2 ** N_BITS

    grid = set()
    for x, line in enumerate(stripped(file)):
        for y, c in enumerate(line):
            if c != ".":
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


def points(grid):
    (min_x, min_y), (max_x, max_y) = bounds(grid)
    yield from (
        (x, y) for x in range(min_x - 5, max_x + 5) for y in range(min_y - 2, max_y + 2)
    )


def to_int(grid, points, neg=False):
    bitstring = "".join(str(int((p in grid) ^ neg)) for p in points)
    return int(bitstring, 2)


def dump_grid(grid, neg=False):
    (min_x, min_y), (max_x, max_y) = bounds(grid)

    for x in range(min_x - 3, max_x + 3):
        for y in range(min_y - 3, max_y + 3):
            print("#" if ((x, y) in grid) ^ neg else ".", end="")
        print()


def solve(file, passes=50):
    repl, grid = parse(file)

    neg = False

    for _ in tqdm(range(passes)):
        # dump_grid(grid, neg)
        prev_neg = neg
        neg = repl[0] if not prev_neg else repl[-1]
        grid = {p for p in points(grid) if neg ^ repl[to_int(grid, neighbors(p), prev_neg)]}


    dump_grid(grid, neg)
    assert not neg
    print(len(grid))


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
