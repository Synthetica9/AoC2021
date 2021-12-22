from argparse import ArgumentParser, FileType
from sys import stdin

from pprint import pprint
from dataclasses import dataclass
import itertools as it
from collections import defaultdict
from math import prod

import networkx as nx


def intersects_1d(l1, l2):
    a1, a2 = l1
    b1, b2 = l2

    return max(a1, b1) <= min(a2, b2)


@dataclass(frozen=True)
class Cuboid:
    x: (int, int)
    y: (int, int)
    z: (int, int)
    fill: bool

    @property
    def dims(self):
        for n in "xyz":
            yield getattr(self, n)

    def fully_encloses(self, other):
        return all(
            a1 <= b1 <= b2 <= a2 for (a1, a2), (b1, b2) in zip(self.dims, other.dims)
        )

    def __contains__(self, pt):
        raise NotImplementedError

    def intersects_edge(self, edge):
        return all(it.starmap(intersects_1d, zip(zip(*edge), self.dims)))

    @property
    def corners(self):
        yield from it.product(*self.dims)

    @property
    def edges(self):
        for c1, c2 in it.combinations(self.corners, 2):
            if sum(a == b for (a, b) in zip(c1, c2)) != 2:
                continue

            yield tuple(sorted([c1, c2]))

    def intersects(self, other):
        return self.fully_encloses(other) or other.fully_encloses(self) or any(
            a.intersects_edge(e)
            for (a, b) in it.permutations([self, other])
            for e in b.edges
        )

    def chop_along(self, axis, value, d):
        assert d in {1, -1}
        d1, d2 = {1: (0, d), -1: (d, 0)}[d]

        assert d1 < d2

        x, y, z = self.dims
        x1, y1, z1 = self.dims
        x2, y2, z2 = self.dims

        if axis == "x":
            assert x[0] <= value + d1 < value + d2 <= x[1], f"{x} {value}"
            x1 = (x[0], value + d1)
            x2 = (value + d2, x[1])

        elif axis == "y":
            assert y[0] <= value + d1 < value + d2 <= y[1]
            y1 = (y[0], value + d1)
            y2 = (value + d2, y[1])

        elif axis == "z":
            assert z[0] <= value + d1 < value + d2 <= z[1]
            z1 = (z[0], value + d1)
            z2 = (value + d2, z[1])

        else:
            raise ValueError(f"Unknown axis {axis}")

        c1 = Cuboid(x1, y1, z1, self.fill)
        c2 = Cuboid(x2, y2, z2, self.fill)

        assert not c1.intersects(c2), f"{c1} intersects with {c2}"
        return [c1, c2]

    def split(self, other):
        if self.fully_encloses(other):
            return []

        # assert not self.fully_encloses(other)
        res = []

        for axis in "xyz":
            for end in [0, 1]:
                a = getattr(self, axis)
                b = getattr(other, axis)

                if not intersects_1d(a, b) or a[0] <= b[0] <= b[1] <= a[1]:
                    continue

                cbs = None
                if end == 0 and a[1] < b[1]:
                    cbs = other.chop_along(axis, a[1], 1)
                elif end == 1 and b[0] < a[0]:
                    cbs = other.chop_along(axis, a[0], -1)

                if cbs is not None:
                    (other,) = (c for c in cbs if self.intersects(c))
                    res.extend(c for c in cbs if not self.intersects(c))
                    assert not any(self.intersects(c) for c in res)

        # res.append(other)
        assert self.fully_encloses(other)
        assert not any(a.intersects(b) for a, b in it.combinations(res, 2))
        assert len(res) <= 6
        return res

    @property
    def volume(self):
        return prod(b - a + 1 for (a, b) in self.dims)

def parse(file):
    for line in file:
        line = line.strip()
        if not line:
            continue

        action, dims = line.split(" ", 1)

        if action == "on":
            action = True
        elif action == "off":
            action = False
        else:
            raise ValueError("Unknown action")

        ns = []
        for s in dims.split(","):
            _, s = s.split("=")
            ns.append(tuple(sorted([int(n) for n in s.split("..")])))

        yield Cuboid(*ns, action)


def parse_dag(file, boundry=None):
    dag = nx.DiGraph()
    for cuboid in parse(file):
        if boundry is not None and not boundry.fully_encloses(cuboid):
            continue
        dag.add_node(cuboid)
        for other in dag.nodes():
            if other == cuboid:
                continue

            if cuboid.intersects(other):
                dag.add_edge(other, cuboid)

    return dag


def to_disjoint(G):
    res = []
    G = G.copy()
    while G.number_of_nodes() > 0:
        print(G.number_of_nodes())
        for node in [n for n, d in G.in_degree() if d == 0]:
            candidates = list(G.neighbors(node))

            G.remove_node(node)
            if len(candidates) == 0:
                res.append(node)
                continue

            split_on = candidates[0]
            # print(split_on)

            new_nodes = split_on.split(node)

            G.add_nodes_from(new_nodes)
            G.add_edges_from(
                (a, b) for a in new_nodes for b in candidates if a.intersects(b)
            )

    # assert not any(a.intersects(b) for (a, b) in it.combinations(res, 2))
    return res


def solve(file, boundry=None):
    if boundry is not None:
        x = boundry
        boundry = Cuboid((-x, x), (-x, x), (-x, x), None)
    g = parse_dag(file, boundry=boundry)
    fills = to_disjoint(g)
    pprint(sorted(fills, key=lambda x: x.volume))

    res = sum(x.volume for x in fills if x.fill)
    print(res)



def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    opts.add_argument("--boundry", default=None, type=int)
    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        print(solve(file, opts.boundry))


if __name__ == "__main__":
    main()
