from argparse import ArgumentParser, FileType
from sys import stdin

import re
from math import copysign

from itertools import count
from dataclasses import dataclass
from typing import Optional

from pprint import pprint


@dataclass(frozen=True)
class IntegerInterval:
    """Integer interval, supports open intervals"""

    _start: Optional[int]
    _end: Optional[int]

    @property
    def start(self):
        return float("-inf") if self._start is None else self._start

    @property
    def end(self):
        return float("+inf") if self._end is None else self._end

    def _check_integrity(self):
        assert self.start <= self.end

    def __contains__(self, value):
        if value is None:
            return False

        assert isinstance(value, int) or abs(value) == float("inf")

        return self.start <= value <= self.end

    def intersects(self, other):
        """If there's at least one integer value in the interval, that is also in the other"""
        self._check_integrity()
        other._check_integrity()

        return any(
            [
                other.start in self,
                other.end in self,
                self.start in other,
                self.end in other,
            ]
        )


def parse(file):
    s = file.read().strip()
    match = re.match(r"^target area: x=(.*)\.\.(.*), y=(.*)\.\.(.*)$", s)
    x1, x2, y1, y2 = (int(x) for x in match.groups())

    return (x1, x2, y1, y2)


def simulate_y(y1, y2, dy):
    assert y1 <= 0 and y2 <= 0

    y = 0
    min_step = None

    for step in count(1):
        y += dy
        dy -= 1

        if y1 <= y <= y2 and min_step is None:
            min_step = step

        elif y < min(y1, y2):
            if min_step is None:
                return None

            return IntegerInterval(min_step, step - 1)


def simulate_x(x1, x2, dx):
    assert x1 >= 0 and x2 >= 0
    min_step = None
    x = 0
    for step in count(1):
        x += dx

        if dx < 0:
            dx += 1
        elif dx > 0:
            dx -= 1

        if x1 <= x <= x2 and min_step is None:
            min_step = step

        elif x > max(x1, x2):
            if min_step is not None:
                return IntegerInterval(min_step, step - 1)
            return None

        if dx == 0:
            # Nothing is gonna change if dx == 0
            if x1 <= x <= x2:
                assert min_step is not None
                return IntegerInterval(min_step, None)
            elif x > max(x1, x2) and min_step is not None:
                return IntegerInterval(min_step, step - 1)
            else:
                assert min_step is None
                return None


def max_y(y1, y2):
    dy = max(
        dy for dy in range(abs(y1) + abs(y2)) if simulate_y(y1, y2, dy) is not None
    )

    return (dy * (dy + 1)) // 2


def count_trajectories(x1, x2, y1, y2):
    all_trajectories = []
    for (p1, p2, f) in [(x1, x2, simulate_x), (y1, y2, simulate_y)]:
        reach = abs(p1) + abs(p2)
        trajectories = {}
        for d in range(-reach, reach):
            interval = f(p1, p2, d)
            if interval is not None:
                trajectories[d] = interval
        all_trajectories.append(trajectories)

    x_trajectories, y_trajectories = all_trajectories

    n = 0
    for dx, x_t in x_trajectories.items():
        for dy, y_t in y_trajectories.items():
            if x_t.intersects(y_t):
                n += 1
    return n


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    opts.add_argument("--find-peak", action="store_true")
    opts.add_argument("--count-trajectories", action="store_true")
    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        x1, x2, y1, y2 = xs = parse(file)
        if opts.find_peak:
            print(f"{max_y(y1, y2)=}")
        if opts.count_trajectories:
            print(f"{count_trajectories(*xs)=}")


assert simulate_x(20, 30, 7) == IntegerInterval(4, None)
assert simulate_x(20, 30, 6) == IntegerInterval(5, None)
assert simulate_x(20, 30, 9) == IntegerInterval(3, 4)
assert simulate_x(20, 30, 17) is None


if __name__ == "__main__":
    main()
