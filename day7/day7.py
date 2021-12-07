from argparse import ArgumentParser, FileType
from sys import stdin


def parse(file):
    return list(map(int, file.read().strip().split(",")))


def triangle(n):
    return (n * (n + 1)) // 2


def value(x, xs, quadratic):
    op = triangle if quadratic else lambda x: x
    return sum(op(abs(x - xn)) for xn in xs)


def solve(file, quadratic=False):
    xs = parse(file)
    guess = int(sum(xs) / len(xs))
    while True:
        val = value(guess, xs, quadratic)
        if value(guess + 1, xs, quadratic) < val:
            guess += 1
        elif value(guess - 1, xs, quadratic) < val:
            guess -= 1
        else:
            return val


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    opts.add_argument("--quadratic", action="store_true")
    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        print(solve(file, opts.quadratic))


if __name__ == "__main__":
    main()
