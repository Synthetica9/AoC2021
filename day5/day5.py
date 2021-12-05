from collections import Counter
from sys import stdin
from itertools import permutations
from argparse import ArgumentParser, FileType


def points(begin, end, diagonal=False):
    (x1, y1), (x2, y2) = begin, end
    # assert x1 == x2 or y1 == y2

    if x1 == x2:
        l, h = sorted([y1, y2])
        return {(x1, y) for y in range(l, h + 1)}

    if y1 == y2:
        l, h = sorted([x1, x2])
        return {(x, y1) for x in range(l, h + 1)}

    if not diagonal:
        return set()

    # On the main diagonal
    if not ((x1 < x2) ^ (y1 < y2)):
        xl, xh = sorted([x1, x2])
        yl, yh = sorted([y1, y2])

        n = xh - xl
        res = {(xl + i, yl + i) for i in range(n + 1)}
        assert begin in res
        assert end in res
        return res

    # on the anti-diagonal
    else:
        n = abs(x1 - x2)
        for a, b in permutations([begin, end]):
            (x1, y1), (x2, y2) = a, b
            res = {(x1 - i, y1 + i) for i in range(n + 1)}
            if begin in res and end in res:
                return res

    assert False


def parse(file):
    for line in file:
        if not line.strip():
            continue

        a, b = line.strip().split(" -> ")
        (x1, y1), (x2, y2) = map(int, a.split(",")), map(int, b.split(","))

        yield (x1, y1), (x2, y2)


def solve(file, diagonals=False):
    levels = Counter(pt for tips in parse(file) for pt in points(*tips, diagonals))

    res = sum(1 for x in levels.values() if x >= 2)
    print(res)


def getopts():
    opts = ArgumentParser()
    opts.add_argument("--diagonals", "-d", action="store_true")
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        solve(file, diagonals=opts.diagonals)


if __name__ == "__main__":
    main()
