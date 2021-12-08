from argparse import ArgumentParser, FileType
from sys import stdin

from collections import defaultdict

digits = [
    "abcefg",
    "cf",
    "acdeg",
    "acdfg",
    "bcdf",
    "abdfg",
    "abdefg",
    "acf",
    "abcdefg",
    "abcdfg",
]


def parse(file):
    for line in file:
        line = line.strip()
        if not line:
            continue
        signals, segments = line.split(" | ", 1)
        signals = signals.split(" ")
        segments = segments.split(" ")
        yield signals, segments


def isValid(signals, bt):
    tbl = defaultdict(lambda: None)
    tbl.update({ord(k): v for k, v in bt.items()})
    for signal in signals:
        translated = signal.translate(tbl)
        for digit in digits:
            if len(digit) != len(signal):
                continue

            if set(translated) <= set(digit):
                break
        else:
            return False

    return True


assert isValid(["ab"], {"a": "c"})


def backtrack(signals, bt=None):
    if bt is None:
        bt = {}

    for char in "abcdefg":
        if char not in bt:
            break
    else:
        yield bt.copy()

    for translation in "abcdefg":
        if translation in bt.values():
            continue

        bt[char] = translation
        if isValid(signals, bt):
            yield from backtrack(signals, bt)
        del bt[char]


def apply(segments, bt):
    bt = {ord(k): v for k, v in bt.items()}
    n = 0
    for seg in segments:
        seg = "".join(sorted(seg.translate(bt)))
        n *= 10
        n += digits.index(seg)
    return n


def part2(file):
    n = 0
    for signals, segments in parse(file):
        signals = sorted(signals, key=len)
        # (sol,) = backtrack(signals)
        sol = next(backtrack(signals))
        n += apply(segments, sol)
    return n


def part1(file):
    n = 0
    for signals, segments in parse(file):
        for seg in segments:
            print(seg)
            if len(seg) in {2, 4, 3, 7}:
                n += 1
    return n


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    opts.add_argument("--part2", action="store_true")
    return opts.parse_args()


def main():
    opts = getopts()
    solve = part2 if opts.part2 else part1
    for file in opts.files:
        print(solve(file))


if __name__ == "__main__":
    main()
