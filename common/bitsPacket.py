import enum
from dataclasses import dataclass
import operator
from functools import wraps
from string import hexdigits
from itertools import islice

from typing import Optional, Tuple

from math import prod


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


class Type(enum.IntEnum):
    SUM = 0
    PROD = 1
    MIN = 2
    MAX = 3
    CONST = 4
    GT = 5
    LT = 6
    EQ = 7


@dataclass(frozen=True)
class BITSPacket:
    version: int
    type: Type
    _value: Optional[int] = None
    packets: Optional[Tuple["BITSPacket"]] = None

    @property
    def value(self):
        if self._value is not None:
            return self._value
        print(self.code)
        return eval(self.code)

    @property
    def version_sum(self):
        return sum(p.version for p in self.descendants)

    @property
    def descendants(self):
        yield self
        if self.packets is not None:
            for packet in self.packets:
                yield from packet.descendants

    @property
    def needs_parentheses(self):
        return self.type not in [Type.CONST, Type.MIN, Type.MAX]

    @property
    def code(self):
        def op(op, nargs=None):
            if self.type == Type.CONST:
                return str(self.value)

            if nargs is not None:
                assert nargs == len(self.packets)

            subs = (f'({p.code})' if p.needs_parentheses else p.code for p in self.packets)

            if op.isalpha():
                args = ', '.join(subs)
                if len(self.packets) <= 1:
                    args = f'[{args}]'

                return f"{op}({args})"


            return f" {op} ".join(subs)

        match self.type:
            case Type.SUM:
                return op("+")
            case Type.PROD:
                return op("*")
            case Type.MIN:
                return op("min")
            case Type.MAX:
                return op("max")
            case Type.CONST:
                return str(self.value)
            case Type.GT:
                return op(">", 2)
            case Type.LT:
                return op("<", 2)
            case Type.EQ:
                return op("==", 2)

    @classmethod
    def from_hex(cls, hex_stream):
        return cls.from_bitstream(to_bitstream(hex_stream))

    @classmethod
    def from_bitstream(cls, bitstream):
        def bits(n):
            return take_int(n, bitstream)

        version = bits(3)
        type_id = Type(bits(3))

        if type_id == Type.CONST:
            # Literal
            xs = []
            keep_going = True
            while keep_going:
                keep_going = bits(1)
                xs.append(bits(4))
            n = int("".join(hexdigits[i] for i in xs), 16)
            return cls(version, type_id, _value=n)
        else:
            length_type_id = bits(1)
            if length_type_id == 0:
                # Number of bits
                n_bits = bits(15)
                packets = []
                sliced_stream = islice(bitstream, n_bits)
                try:
                    while True:
                        packet = cls.from_bitstream(sliced_stream)
                        packets.append(packet)
                except ValueError:
                    pass

            elif length_type_id == 1:
                # Number of packets
                n_packets = bits(11)
                packets = [cls.from_bitstream(bitstream) for _ in range(n_packets)]

            else:
                assert False  # How would this even happen?

            assert all(packet is not None for packet in packets)

            return cls(version, type_id, packets=tuple(packets))

        # There should've been a return at this point:
        assert False


if __name__ == "__main__":
    examples = {
        "C200B40A82": 3,
        "04005AC33890": 54,
        "880086C3E88112": 7,
        "CE00C43D881120": 9,
        "D8005AC2A8F0": 1,
        "F600BC2D8F": 0,
        "9C005AC2F8F0": 0,
        "9C0141080250320F1802104A08": 1,
    }

    for example, answer in examples.items():
        packet = BITSPacket.from_hex(example)
        print(example, packet.code, packet.value, sep=" -> ")
        assert packet.value == answer
