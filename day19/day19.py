from argparse import ArgumentParser, FileType
from sys import stdin

from itertools import product, permutations, combinations
import numpy as np
from collections import defaultdict
from pprint import pprint

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(arg, **kwargs):
        return arg


def parse(file):
    scanners = []
    for line in file:
        line = line.strip()
        if not line:
            continue
        if line.startswith("---"):
            scanners.append([])
        else:
            scanners[-1].append(tuple(int(x) for x in line.split(",")))

    return [frozenset(s) for s in scanners]


ROTATIONS = [
    mat
    for mat in (np.array(xs).reshape((3, 3)) for xs in product((-1, 0, 1), repeat=9))
    if np.linalg.det(mat) == 1 and np.abs(mat).sum() == 3
]

EYE = np.eye(3, dtype=int)


def apply(transformation, scanner):
    return frozenset(tuple(p @ transformation) for p in scanner)


def translate(point, scanner):
    dx, dy, dz = point
    return frozenset((x - dx, y - dy, z - dz) for x, y, z in scanner)


def match(s1, s2, n=12):
    points = {tuple(b - a for a, b in zip(p1, p2)) for p1 in s1 for p2 in s2}
    # print(len(s1), len(s2), len(s1) * len(s2), len(points))

    if len(points) == len(s1) * len(s2):
        return

    for p in points:
        s2t = translate(p, s2)
        # assert p1 in s2t

        intersection = s2t.intersection(s1)
        if len(intersection) >= n:
            # Found a possible match.
            assert len(s1) * len(s2) >= len(points) - n + 1

            return p

    return None


def assemble(scanners, d, index=0, seen=None):
    if seen is None:
        seen = frozenset()

    if index in seen:
        return set()

    res = scanners[index]
    seen |= {index}

    for (i2, ir, p) in d[index]:
        res |= translate(p, apply(ROTATIONS[ir], assemble(scanners, d, i2, seen)))

    return res


def actual_locs(scanners, d, index=0, seen=None):
    if seen is None:
        seen = frozenset()

    if index in seen:
        return {}

    res = {index: (0, 0, 0)}
    seen |= {index}

    for (i2, ir, p) in d[index]:
        for (k, v) in actual_locs(scanners, d, i2, seen).items():
            (p2,) = translate(p, apply(ROTATIONS[ir], {v}))
            res[k] = p2
    return res


def inverse(ir):
    rot = ROTATIONS[ir]
    inv = np.linalg.inv(rot)

    for i, a in enumerate(ROTATIONS):
        if (inv == a).all():
            return i

    assert False


def search(scanners):
    d = defaultdict(list)
    for (i1, s1), (i2, s2) in tqdm(
        product(enumerate(scanners), repeat=2), total=len(scanners) ** 2):
        if i1 == i2:
            continue

        for ir, rotation in enumerate(ROTATIONS):
            s2t = apply(rotation, s2)
            p = match(s1, s2t)
            if p is None:
                continue

            assert match(s2t, s1)


            # inv = inverse(ir)
            # inv_p, = apply(ROTATIONS[inv], {p})
            d[i1].append((i2, ir, p))
            # d[i2].append((i1, inv, p @ ))

    return dict(d)


def manhattan_distance(p1, p2):
    return sum(abs(a - b) for (a, b) in zip(p1, p2))


def solve(file):
    xs = parse(file)
    network = search(xs)
    assembled = assemble(xs, network)
    pprint(network)
    # for p in assembled:
    #     x, y, z = p
    #     print(f"{x},{y},{z}")
    print(len(assembled))
    scanner_locs = actual_locs(xs, network)
    max_pts = max(
        product(scanner_locs.values(), repeat=2),
        key=lambda x: manhattan_distance(*x),
    )
    print(max_pts)
    print(manhattan_distance(*max_pts))


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
