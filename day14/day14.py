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

        (a, c), b = line.split(" -> ")
        replacements[(a, c)] = Counter([(a, b), (b, c)])

    return initial, replacements, last_elem


def scalar_mult(n, c):
    return Counter({k: n * v for (k, v) in c.items()})


def double(replacements):
    new_replacements = {}
    for k, v in replacements.items():
        ctr = Counter()
        for p, count in v.items():
            ctr.update(scalar_mult(count, replacements[p]))
        new_replacements[k] = ctr
    return new_replacements


def step(sequence, replacements):
    new_sequence = Counter()
    for k, v in sequence.items():
        new_sequence.update(scalar_mult(v, replacements[k]))
    return new_sequence


def bits(n):
    return [bool(int(x)) for x in bin(n)[2:]][::-1]


def solve(file, n=40):
    pairs, replacements, last_elem = parse(file)
    print(bits(n))
    for b in bits(n):
        # print(pairs)
        if b:
            pairs = step(pairs, replacements)
        replacements = double(replacements)

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
