from argparse import ArgumentParser, FileType
from sys import stdin


def solve(file):
    raise NotImplementedError


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        solve(file)


if __name__ == "__main__":
    main()
