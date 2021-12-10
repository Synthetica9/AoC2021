from argparse import ArgumentParser, FileType
from sys import stdin


parens = {
    "[": "]",
    "<": ">",
    "(": ")",
    "{": "}",
}

error_scores = {
    ")": 3,
    "]": 57,
    "}": 1197,
    ">": 25137,
}

completion_scores = {
    ")": 1,
    "]": 2,
    "}": 3,
    ">": 4,
}


def parse_line(line):
    stack = []
    for char in line:
        if char in parens.keys():
            stack.append(parens[char])
        elif stack.pop() != char:
            return char

    return stack


def parse(file, first_errors=False):
    for line in file:
        line = line.strip()
        if not line:
            continue

        res = parse_line(line)
        if isinstance(res, list) ^ first_errors:
            yield res


def part1(file):
    return sum(error_scores[res] for res in parse(file, first_errors=True))


def median(xs):
    return sorted(xs)[len(xs) // 2]


def part2(file):
    scores = []
    for res in parse(file, first_errors=False):
        score = 0
        for char in res[::-1]:
            score *= 5
            score += completion_scores[char]
        # print(res, score)
        scores.append(score)
    return median(scores)


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
