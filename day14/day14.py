from argparse import ArgumentParser, FileType
from sys import stdin

from itertools import pairwise

from collections import Counter
from math import ceil

from functools import cache


def parse(file):
    first_line = next(file).strip()
    initial = Counter(pairwise(first_line))
    last_elem = first_line[-1]

    replacements = {}
    for line in file:
        line = line.strip()
        if not line:
            continue

        (a, c), b = line.split(" -> ")
        replacements[(a, c)] = Counter([(a, b), (b, c)])

    return initial, replacements, last_elem


def scalar_mult(n, c):
    return Counter({k: n * v for (k, v) in c.items()})


def multistep(n, pairs, replacements):
    @cache
    def steps(n, pair):
        if n == 0:
            return Counter([pair])

        if n == 1:
            return replacements[pair]

        outer = n // 2
        inner = n - outer
        # print(n, outer, inner)

        ctr = steps(outer, pair)
        res = Counter()
        for p, n in ctr.items():
            other = steps(inner, p)
            res.update(scalar_mult(n, other))
        return res

    res = Counter()

    for pair, count in pairs.items():
        res.update(scalar_mult(count, steps(n, pair)))

    return res


def solve(file, n=40):
    pairs, replacements, last_elem = parse(file)
    res = multistep(n, pairs, replacements)
    elements = Counter()
    for (a, b), v in res.items():
        elements[a] += v
    elements[last_elem] += 1

    c = elements.most_common()
    return c[0][1] - c[-1][1]


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    opts.add_argument("--iterations", type=int, default=10)
    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        print(solve(file, opts.iterations))


if __name__ == "__main__":
    main()
