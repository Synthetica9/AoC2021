from argparse import ArgumentParser, FileType
from sys import stdin
from collections import Counter


def parse(file):
    return [int(x) for x in next(file).strip().split(",")]


def solve(file, days=80):
    xs = parse(file)
    c = Counter(xs)
    for day in range(days):
        it = list(c.items())
        c = Counter()
        for (n, x) in it:
            if n == 0:
                c[6] += x
                c[8] += x
            else:
                c[n - 1] += x

    return sum(c.values())


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    opts.add_argument("-d", "--days", default=80, type=int)
    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        print(solve(file, days=opts.days))


if __name__ == "__main__":
    main()
