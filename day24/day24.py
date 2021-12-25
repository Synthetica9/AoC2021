from argparse import ArgumentParser, FileType
from sys import stdin

from pprint import pprint


def parse_arg(arg):
    try:
        return int(arg)
    except ValueError:
        return arg


def parse(file):
    program = []
    for line in file:
        line = line.strip()
        if not line:
            continue
        cmd, *args = line.split()
        args = [parse_arg(arg) for arg in args]
        program.append((cmd, args))
    return program


def extract_blocks(program):
    blocks = []
    for cmd, args in program:
        if cmd == "inp":
            blocks.append([])
        blocks[-1].append((cmd, args))
    return blocks


def get_arg2(line):
    cmd, args = line
    return args[1]


def extract_values(block):
    div = get_arg2(block[4])
    check = get_arg2(block[5])
    offset = get_arg2(block[15])
    return (div, check, offset)


def solve(file, smallest=False):
    program = parse(file)
    blocks = extract_blocks(program)
    z = []
    d = {}
    for i, block in enumerate(blocks):
        div, check, offset = extract_values(block)
        if div == 1:
            z.append((i, offset))
        elif div == 26:
            i_, offset_ = z.pop()
            d[i_] = (i, check + offset_)
        else:
            assert False

    num = [1 if smallest else 9] * len(blocks)
    for i, (j, offset) in d.items():
        if smallest:
            if offset < 0:
                num[i] = num[j] - offset
            else:
                num[j] = num[i] + offset
        else:
            if offset < 0:
                num[j] = num[i] + offset
            else:
                num[i] = num[j] - offset

    assert all(x in range(1, 10) for x in num)
    return "".join(str(n) for n in num)


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    opts.add_argument("--smallest", action="store_true")
    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        print(solve(file, opts.smallest))


if __name__ == "__main__":
    main()
