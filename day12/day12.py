from argparse import ArgumentParser, FileType
from sys import stdin

from collections import defaultdict


def parse(file):
    graph = defaultdict(set)
    for line in file:
        line = line.strip()
        if not line:
            continue
        print(line)
        a, b = line.split("-")
        graph[a].add(b)
        graph[b].add(a)
    return graph


def dfs(graph, x, visited=None, visited_twice=False):
    if visited is None:
        visited = set()

    if x == "end":
        yield [x]
        return

    if x.islower():
        visited = visited | {x}

    for neighbor in graph[x]:
        if neighbor not in visited:
            yield from map(
                lambda xs: [x] + xs,
                dfs(graph, neighbor, visited, visited_twice),
            )
        elif not visited_twice and neighbor != "start":
            yield from map(
                lambda xs: [x] + xs,
                dfs(graph, neighbor, visited, True),
            )


def solve(file):
    graph = parse(file)
    n = 0
    found = set()
    for path in dfs(graph, "start"):
        # print(",".join(path))
        # print(len(found))
        # print(path)
        n += 1
    return n


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
