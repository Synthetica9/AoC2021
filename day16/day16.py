from argparse import ArgumentParser, FileType
from sys import stdin

from string import hexdigits
from itertools import islice
import operator
from functools import wraps
from math import prod
from common import timer, BITSPacket


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    opts.add_argument("--version-sum", action="store_true")

    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        with timer("day 16"):
            s = file.read().strip()
            packet = BITSPacket.from_hex(s)
            print(packet)
            xs = {(p.version, p.type) for p in packet.descendants}
            ys = {(a, b) for a in range(8) for b in range(8) if (a, b) not in xs}
            print(ys)
            if opts.version_sum:
                print(packet.version_sum)
            else:
                print(packet.code)
                print(packet.value)


if __name__ == "__main__":
    main()
