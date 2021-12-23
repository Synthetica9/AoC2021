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
def dist_to_target(c, p):
    if p in FINAL_LOCATIONS[c]:
        return 0

    return DISTANCE_PAIRS[p, FINAL_LOCATIONS[c][0]]


def step(spaces, configuration):
    """
    Returns all configurations that follow on from the current configuration.
    """

    for point, c in configuration.items():
        for n in neighbors(point):
            # You never need to move to the second space of a tunnel if you don't belong there...
            if n in [FINAL_LOCATIONS[o][-1] for o in "ABCD" if o != c]:
                continue

            # In the main cavern, don't ever move away from your destination unless someone is pushing you...
            # TODO

            if n not in spaces:
                continue

            if dist_to_target(c, n) >= dist_to_target(c, point):
                group = list(connected_group(point, configuration))
                for a in group:
                    ca = configuration[a]
                    if dist_to_target(ca, point) < dist_to_target(ca, a):
                        break
                else:
                    continue

            if n not in configuration:
                s = configuration.copy()
                del s[point]
                s[n] = c
                yield s, ENERGY_COSTS[c]


FINAL_LOCATIONS = {
    "A": [(2, 3), (3, 3), (4, 3), (5, 3)],
    "B": [(2, 5), (3, 5), (4, 5), (5, 5)],
    "C": [(2, 7), (3, 7), (4, 7), (5, 7)],
    "D": [(2, 9), (3, 9), (4, 9), (5, 9)],
}


def is_final(configuration):
    for p, c in configuration.items():
        if p not in FINAL_LOCATIONS[c]:
            return False
    assert heuristic(configuration) == 0
    return True


DISTANCE_PAIRS = None


def heuristic(configuration):
    cost = 0
    for c, ps in FINAL_LOCATIONS.items():
        throat = ps[0]
        throat = (throat[0] - 1, throat[1])

        for i, p in enumerate([throat] + ps):
            present = []
            if p not in configuration:
                continue
            if configuration[p] == c:
                present.append(p)
            else:
                # Everything above has to migrate out again...
                for p0 in present:
                    cost += ENERGY_COSTS[c] * (DISTANCE_PAIRS[p0, throat] + 1)
                break

    for c in "ABCD":
        c_locs = [p for p, c2 in configuration.items() if c2 == c]
        cost += ENERGY_COSTS[c] * min(
            sum(DISTANCE_PAIRS[a, b] for a, b in zip(perm, FINAL_LOCATIONS[c]))
            for perm in itertools.permutations(c_locs)
        )

    return cost


def to_hashable(configuration):
    return tuple(sorted(configuration.items()))


def from_hashable(configuration):
    return dict(configuration)


def distances(spaces):
    d = {}
    for point in spaces:
        d[(point, point)] = 0
        for n in neighbors(point):
            if n not in spaces:
                continue
            d[(point, n)] = 1

    def dist(a, b):
        return d.get((a, b), float("inf"))

    changed = True
    while changed:
        changed = False
        for abc in itertools.combinations(spaces, 3):
            for a, b, c in itertools.permutations(abc):
                if dist(a, b) + dist(b, c) < dist(a, c):
                    d[a, c] = dist(a, b) + dist(b, c)
                    changed = True
    return d


def to_string(configuration, spaces):
    s = ""
    for x in range(max(x for x, y in spaces) + 2):
        for y in range(max(y for x, y in spaces) + 2):
            p = (x, y)
            s += configuration.get(p, "." if p in spaces else "#")
        s += "\n"
    return s.strip()


def connected_group(p, configuration, seen=None):
    if seen is None:
        seen = set()

    seen.add(p)
    yield p
    for p2 in neighbors(p):
        if p2 not in seen and p2 in configuration:
            yield from connected_group(p2, configuration, seen)


def a_star(configuration, spaces):
    """
    A* search.
    """
    best = heuristic(configuration)
    open = [(best, 0, to_hashable(configuration))]
    closed = set()

    for i in tqdm(itertools.count()):
        if not open:
            return None

        # To get accurate tqdm stats:
        _, real_cost, configuration = heapq.heappop(open)
        while configuration in closed:
            _, real_cost, configuration = heapq.heappop(open)

        configuration = from_hashable(configuration)

        if heuristic(configuration) < best:
            print()
            print(to_string(configuration, spaces))
            print(len(open), len(closed), real_cost)
            best = heuristic(configuration)

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
                            real_cost + cost + heuristic(config),
                            real_cost + cost,
                            to_hashable(config),
                        )
                    ),
                )

        closed.add(to_hashable(configuration))
    return None


def solve(file):
    spaces, start = parse(file)
    global DISTANCE_PAIRS
    DISTANCE_PAIRS = distances(spaces)

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
