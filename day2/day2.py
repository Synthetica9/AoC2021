#!/usr/bin/env nix-shell
#! nix-shell -p "python3" -i python

from sys import stdin
import argparse

directions = {
    "down": (1, 0),
    "up": (-1, 0),
    "forward": (0, 1),
}


def parse(file):
    for line in file:
        line = line.strip()
        if not line:
            continue
        action, amount = line.split()
        dx, dy = directions[action]
        amount = int(amount)

        yield dx * amount, dy * amount


def solve(file, withAim=True):
    x = y = aim = 0
    for dx, dy in parse(file):
        aim += dx
        y += dy
        x += dy * aim if withAim else dx

    return x * y


def getopts():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-aim",
        dest="withAim",
        action="store_true",
    )
    
    parser.add_argument(
        "files",
        type=argparse.FileType("r"),
        metavar="FILE",
        default=[stdin],
        nargs="*",
    )

    return parser.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        print(solve(file, withAim=opts.withAim))


if __name__ == "__main__":
    main()
