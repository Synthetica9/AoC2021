from argparse import ArgumentParser, FileType
from sys import stdin

from math import ceil, floor
from functools import partial
from collections import deque
from itertools import chain, repeat
import json
from itertools import product

from typing import Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class SnailFishNum:
    value: Union[int, Tuple["SnailFishNum", "SnailFishNum"]]
    parent: Optional["SnailFishNum"] = None

    @property
    def is_leaf(self):
        return isinstance(self.value, int)

    @property
    def depth(self):
        if self.is_root:
            return 0

        return 1 + self.parent.depth

    @property
    def is_root(self):
        return self.parent is None

    @property
    def root(self):
        return self if self.is_root else self.parent.root

    @property
    def has_children(self):
        return not isinstance(self.value, int)

    @property
    def is_simple(self):
        return self.has_children and self.left.is_leaf and self.right.is_leaf

    @property
    def leftmost(self):
        return self if self.is_leaf else self.left

    @property
    def rightmost(self):
        return self if self.is_leaf else self.right

    @property
    def ancestors(self):
        a = self
        while not a.is_root:
            a = a.parent
            yield a

    def is_ancestor(self, other):
        return any(self is x for x in other.ancestors)

    @property
    def left_cousin(self):
        found = False
        for x in self.root.inorder(reverse=True):
            if x is self:
                found = True
            elif found and x.is_leaf and not self.is_ancestor(x):
                return x

    @property
    def right_cousin(self):
        found = False
        for x in self.root.inorder(reverse=False):
            if x is self:
                found = True
            elif found and x.is_leaf and not self.is_ancestor(x):
                assert x is not self
                return x

    @property
    def left(self):
        return self.value[0]

    @property
    def right(self):
        return self.value[1]

    def inorder(self, reverse=False):
        if self.has_children:
            f, l = self.left, self.right
            if reverse:
                f, l = l, f

            yield from f.inorder(reverse)
            yield self
            yield from l.inorder(reverse)
        else:
            yield self

    @classmethod
    def from_list(cls, xs, parent=None):
        if isinstance(xs, int):
            return cls(xs, parent)

        assert len(xs) == 2
        l, r = xs

        self = cls(None, parent)
        self.value = (cls.from_list(l, self), cls.from_list(r, self))
        return self

    def to_list(self):
        if self.is_leaf:
            return self.value
        l, r = self.value
        return [l.to_list(), r.to_list()]

    @property
    def magnitude(self):
        if self.is_leaf:
            return self.value

        l, r = self.value
        return 3 * l.magnitude + 2 * r.magnitude


def explode(t):
    for st in t.inorder():
        if not st.is_simple or st.depth < 4:
            continue

        l, r = st.left.value, st.right.value

        lc = st.left_cousin
        rc = st.right_cousin

        assert lc is not None or rc is not None

        if lc is not None:
            lc.value += l

        if rc is not None:
            rc.value += r

        st.value = 0

        return True
    return False


def split(t):
    for st in t.inorder():
        if not st.is_leaf or st.value < 10:
            continue

        n = st.value / 2
        l = st.from_list(floor(n), st)
        r = st.from_list(ceil(n), st)
        st.value = (l, r)
        return True
    return False


def run(xs):
    n = SnailFishNum.from_list(xs)

    while True:
        if explode(n):
            continue
        if split(n):
            continue
        break

    return n.to_list()


examples = [
    (
        [[[[[4, 3], 4], 4], [7, [[8, 4], 9]]], [1, 1]],
        [[[[0, 7], 4], [[7, 8], [6, 0]]], [8, 1]],
    )
]

for a, b in examples:
    assert run(a) == b


def solve(file):
    parsed = parse(file)

    curr, *xs = parsed
    while xs:
        new, *xs = xs
        curr = [curr, new]
        curr = run(curr)
        print(curr)

    print(SnailFishNum.from_list(curr).magnitude)

    mm = max(
        ([x, y] for x, y in product(parsed, repeat=2) if x != y),
        key=lambda p: SnailFishNum.from_list(run(p)).magnitude,
    )

    print(*mm, sep="\n")
    print(SnailFishNum.from_list(run(mm)).magnitude)


def parse(file):
    xs = []
    for line in file:
        line = line.strip()
        if not line:
            continue
        xs.append(json.loads(line))
    return xs


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
