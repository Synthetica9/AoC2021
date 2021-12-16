from argparse import ArgumentParser, FileType
from sys import stdin

from string import hexdigits
from itertools import islice
from more_itertools import peekable
import operator
from functools import reduce, wraps


def to_bitstream(hex_stream):
    for char in hex_stream:
        for bit in f"{int(char, 16):04b}":
            yield int(bit)


def take_int(n_bits, bitstream):
    try:
        bits = (next(bitstream) for _ in range(n_bits))
        return int("".join(str(b) for b in bits), 2)
    except RuntimeError as e:
        raise ValueError("Not enough bits to take.") from e


def is_empty(peekable):
    try:
        peekable.peek()
    except StopIteration:
        return True
    return False


def parse_packet(bitstream):
    def bits(n):
        return take_int(n, bitstream)

    try:
        version = bits(3)
        type_id = bits(3)
    except ValueError:
        return None

    common = {"version": version, "type_id": type_id}

    if type_id == 4:
        # Literal
        xs = []
        keep_going = True
        while keep_going:
            keep_going = bits(1)
            xs.append(bits(4))
        n = int("".join(hexdigits[i] for i in xs), 16)
        return {**common, "value": n}
    else:
        length_type_id = bits(1)
        if length_type_id == 0:
            # Number of bits
            n_bits = bits(15)
            packets = []
            sliced_stream = peekable(islice(bitstream, None, n_bits))

            while not is_empty(sliced_stream):
                pack = parse_packet(sliced_stream)
                packets.append(pack)

            return {**common, "packets": packets}

        elif length_type_id == 1:
            # Number of packets
            n_packets = bits(11)
            return {
                **common,
                "packets": [parse_packet(bitstream) for _ in range(n_packets)],
            }

    # There should've been a return at this point:
    assert False


def parse(source):
    if not isinstance(source, str):
        source = source.read().strip()

    hex_stream = iter(source)

    while True:
        packet = parse_packet(to_bitstream(hex_stream))

        if packet is None:
            break
        yield packet


def product(xs):
    return reduce(operator.mul, xs)


def fail(xs):
    assert False


def make_star(op):
    return wraps(op)(lambda xs: op(*xs))


OPCODES = {
    0: sum,
    1: product,
    2: min,
    3: max,
    4: fail,  # Unique case
    5: make_star(operator.gt),
    6: make_star(operator.lt),
    7: make_star(operator.eq),
}


def execute(packet):
    assert packet["type_id"] in OPCODES

    if packet["type_id"] == 4:
        return packet["value"]

    subpackets = map(execute, packet["packets"])
    value = OPCODES[packet["type_id"]](subpackets)

    return value


def version_sum(packets):
    if isinstance(packets, dict):
        n = packets["version"]
        n += version_sum(packets.get("packets", []))
        return n
    else:
        return sum(map(version_sum, packets))


def solve(file):
    packets = parse(file)

    return sum(map(execute, packets))


def getopts():
    opts = ArgumentParser()
    opts.add_argument("files", nargs="*", default=[stdin], type=FileType("r"))
    opts.add_argument("--version-sum", action="store_true")

    return opts.parse_args()


def main():
    opts = getopts()
    for file in opts.files:
        packets = parse(file)
        if opts.version_sum:
            print(version_sum(packets))
        else:
            print(sum(map(execute, packets)))


if __name__ == "__main__":
    main()
