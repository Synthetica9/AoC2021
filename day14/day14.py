from argparse import ArgumentParser, FileType
from sys import stdin

from itertools import pairwise

from collections import Counter
from math import ceil


def parse(file):
    first_line = next(file).strip()
    initial = Counter(pairwise(first_line))
    last_elem = first_line[-1]

    replacements = {}
    for line in file:
        line = line.strip()
        if not line:
            continue

        a, b = line.split(" -> ")
        replacements[tuple(a)] = b

    return initial, replacements, last_elem


def step(sequence, replacements):
    new_sequence = Counter()
    for (a, c), v in sequence.items():
        b = replacements[(a, c)]
        new_sequence[(a, b)] += v
        new_sequence[(b, c)] += v
    return new_sequence


def solve(file, n=40):
    pairs, replacements, last_elem = parse(file)

    for i in range(n):
        # print(pairs)
        pairs = step(pairs, replacements)

    elements = Counter()
    for (a, b), v in pairs.items():
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
