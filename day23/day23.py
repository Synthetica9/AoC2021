from argparse import ArgumentParser, FileType
from sys import stdin

import itertools
import heapq

from functools import cache

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(arg, **kwargs):
        return arg


def parse(file):
    """
    Parses a file into a set of open spaces, and a starting configuration.

    Example input:

    #############
    #...........#
    ###B#C#B#D###
      #A#D#C#A#
      #########
    """
    spaces = set()
    start = dict()
    for x, line in enumerate(file):
        for y, c in enumerate(line):
            if c == ".":
                spaces.add((x, y))
            elif c in "ABCD":
                spaces.add((x, y))
                start[(x, y)] = c
    return spaces, start


def neighbors(point):
    x, y = point
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


ENERGY_COSTS = {
    "A": 1,
    "B": 10,
    "C": 100,
    "D": 1000,
}


@cache
def dist_to_target(c, p, spaces):
    if p in FINAL_LOCATIONS[c]:
        return 0

    return distance(p, FINAL_LOCATIONS[c][0], spaces)


def reachable_squares(p, spaces, configuration, seen=None):
    if seen is None:
        seen = set()

    for n in neighbors(p):
        if n not in spaces or n in configuration or n in seen:
            continue
        seen.add(n)
        yield n
        yield from reachable_squares(n, spaces, configuration, seen)


def connected_group(p, configuration, seen=None):
    if seen is None:
        seen = set()

    seen.add(p)
    yield p
    for p2 in neighbors(p):
        if p2 not in seen and p2 in configuration:
            yield from connected_group(p2, configuration, seen)


@cache
def is_hallway(p):
    return p[0] == 1


@cache
def is_resting_place(p):
    return is_hallway(p) and p[1] not in (c[0][1] for c in FINAL_LOCATIONS.values())


def step(spaces, configuration):
    """
    Returns all configurations that follow on from the current configuration.
    """

    for point, c in configuration.items():
        if point in FINAL_LOCATIONS[c] and not any(
            p2 > point and configuration.get(p2) != c
            for p2 in FINAL_LOCATIONS[c]
            if p2 in spaces
        ):
            continue

        reachable = list(reachable_squares(point, spaces, configuration))

        for p in reachable:
            if p == point:
                continue

            # Can't move into a foreign space!
            if not is_resting_place(p) and p not in FINAL_LOCATIONS[c]:
                continue

            # Can't move into a tube if there are foreign occupants!
            if p in FINAL_LOCATIONS[c] and not all(
                configuration.get(p2, c) == c
                for p2 in FINAL_LOCATIONS[c]
                if p2 in spaces
            ):
                continue

            # Can't wiggle around in the hallways!
            if is_hallway(p) and is_hallway(point):
                continue

            # Only move into the last spot of a room
            if p in FINAL_LOCATIONS[c] and any(
                p2 > p and p2 not in configuration
                for p2 in FINAL_LOCATIONS[c]
                if p2 in spaces
            ):
                continue

            conf_copy = configuration.copy()
            del conf_copy[point]
            conf_copy[p] = c
            yield conf_copy, distance(p, point, spaces) * ENERGY_COSTS[c]


FINAL_LOCATIONS = {
    "A": [(2, 3), (3, 3), (4, 3), (5, 3)],
    "B": [(2, 5), (3, 5), (4, 5), (5, 5)],
    "C": [(2, 7), (3, 7), (4, 7), (5, 7)],
    "D": [(2, 9), (3, 9), (4, 9), (5, 9)],
}
# FINAL_LOCATIONS = {
#     "A": [(2, 3), (3, 3)],
#     "B": [(2, 5), (3, 5)],
#     "C": [(2, 7), (3, 7)],
#     "D": [(2, 9), (3, 9)],
# }


def is_final(configuration):
    for p, c in configuration.items():
        if p not in FINAL_LOCATIONS[c]:
            return False
    # assert heuristic(configuration) == 0
    return True


DISTANCE_PAIRS = None


@cache
def path_find(a, b, spaces):
    seen = set()

    def do_find(a, b):
        if a in seen:
            return
        seen.add(a)
        if a == b:
            yield []
        for n in neighbors(a):
            if n not in spaces:
                continue
            for path in do_find(n, b):
                yield [n] + path

    return min(do_find(a, b), key=len)


def heuristic(configuration, spaces):
    cost = 0

    for c in "ABCD":
        c_locs = [p for p, c2 in configuration.items() if c2 == c]
        cost += min(
            sum(
                sum(
                    ENERGY_COSTS[configuration[c2]]
                    for c2 in path_find(a, b, spaces)
                    if c2 in configuration
                )
                + distance(a, b, spaces) * ENERGY_COSTS[c]
                for a, b in zip(perm, FINAL_LOCATIONS[c])
            )
            for perm in itertools.permutations(c_locs)
        )

    return cost


def to_hashable(configuration):
    return tuple(sorted(configuration.items()))


def from_hashable(configuration):
    return dict(configuration)


@cache
def distance(a, b, spaces):
    return len(path_find(a, b, spaces))


def to_string(configuration, spaces):
    s = ""
    for x in range(max(x for x, y in spaces) + 2):
        for y in range(max(y for x, y in spaces) + 2):
            p = (x, y)
            s += configuration.get(p, "." if p in spaces else "#")
        s += "\n"
    return s.strip()


def a_star(configuration, spaces):
    """
    A* search.
    """
    best = heuristic(configuration, spaces)
    open = [(best, 0, to_hashable(configuration))]
    closed = set()

    for i in tqdm(itertools.count()):
        if not open:
            print("\n\noptions exhausted after {} steps".format(i))
            return None

        # To get accurate tqdm stats:
        _, real_cost, configuration = heapq.heappop(open)

        configuration = from_hashable(configuration)

        if heuristic(configuration, spaces) < best:
            print()
            print(to_string(configuration, spaces))
            print(len(open), len(closed), real_cost)
            best = heuristic(configuration, spaces)

        # if count_finals(configuration) > best_finals:
        #     print()
        #     print(to_string(configuration, spaces))
        #     best_finals = count_finals(configuration)

        # if i % 10000 == 0:
        #     print(configuration)
        #     print(len(closed), len(open))

        #     # Cleanup...
        #     # open = sorted(c for c in open if c[2] not in closed)
        #     # print(len(closed), len(open))

        if is_final(configuration):
            # c_plus_h is the cost plus heuristic, so it's the total cost because the heuristic is 0
            return real_cost

        for config, cost in step(spaces, configuration):
            if to_hashable(config) not in closed:
                heapq.heappush(
                    open,
                    (
                        (
                            real_cost + cost + heuristic(config, spaces),
                            real_cost + cost,
                            to_hashable(config),
                        )
                    ),
                )

        closed.add(to_hashable(configuration))

    return None


def solve(file):
    spaces, start = parse(file)
    spaces = frozenset(spaces)
    print(spaces)

    for k in start:
        print(k, *reachable_squares(k, spaces, start))

    # print(spaces, start)
    # print(is_final(start))
    # print(heuristic(start))
    # print(DISTANCE_PAIRS[(3, 3), (3, 9)])

    return a_star(start, spaces)


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
