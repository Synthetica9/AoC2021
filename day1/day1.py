#!/usr/bin/env nix-shell
#!nix-shell --pure -p python310 -i python3

from itertools import pairwise, starmap
from operator import lt
from collections import deque

from sys import stdin
from argparse import ArgumentParser
import argparse


def window(it, size=3, op=sum):
    d = deque(maxlen=size)
    for i in it:
        d.append(i)
        if len(d) == size:
            yield op(d)


def solve(it):
    return sum(starmap(lt, pairwise(it)))


def parse(file):
    return (int(x.strip()) for x in file if x.strip())


def getopts():
    parser = ArgumentParser()
    parser.add_argument("-w", "--window", type=int, dest="window")
    parser.add_argument(
        "files", metavar="FILE", type=argparse.FileType("r"), default=[stdin], nargs="*"
    )
    return parser.parse_args()


def main(options):
    for filename in options.files:
        it = parse(filename)
        if options.window is not None:
            it = window(it, options.window)
        sol = solve(it)
        print(sol)


if __name__ == "__main__":
    opts = getopts()
    main(opts)
