import random
import sys

import pytest

from library_codex.number_theory.BigIntegerDivision import divide_hex, divide_decimal


def test_division():
    rng = random.Random(6519)
    for bits in (1, 31, 2048, 2049, 4096, 8193, 16001):
        for quotient_bits in (0, 1, 2048, 2049, 4097, 17001):
            for _ in range(3):
                divisor = rng.getrandbits(bits) | (1 << (bits - 1))
                quotient = rng.getrandbits(quotient_bits)
                for remainder in (0, 1, divisor - 1):
                    first = divisor * quotient + remainder
                    for a, b in ((first, divisor), (-first, divisor), (first, -divisor), (-first, -divisor)):
                        assert divide_hex(format(a, "X"), format(b, "X")) == tuple(format(value, "X") for value in divmod(a, b))


def test_hex_and_zero():
    assert divide_hex("-FF", "10") == ("-10", "1")
    assert divide_hex("000ff", "-0010") == ("-10", "-1")
    assert divide_hex("0", "F") == ("0", "0")
    with pytest.raises(ZeroDivisionError):
        divide_hex("1", "0")


def test_large_constructed_division():
    rng = random.Random(87511)
    for divisor_bits, quotient_bits in ((300001, 250003), (10007, 900001), (900001, 2100)):
        divisor = rng.getrandbits(divisor_bits) | (1 << (divisor_bits - 1))
        quotient = rng.getrandbits(quotient_bits) | (1 << (quotient_bits - 1))
        for remainder in (0, 1, divisor - 1):
            assert divide_hex(format(divisor * quotient + remainder, "X"), format(divisor, "X")) == (format(quotient, "X"), format(remainder, "X"))


def test_small_signed_division():
    for first in range(-100, 101):
        for second in range(-25, 26):
            if second:
                assert divide_decimal(str(first), str(second)) == tuple(map(str, divmod(first, second)))


def test_decimal():
    rng = random.Random(651978)
    old = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(12000)
        for size in (1, 31, 511, 512, 513, 1023, 1024, 1025, 4097, 8193):
            for other in (1, size // 2 + 1, size):
                first = "".join(str(rng.randrange(10)) for _ in range(size))
                second = "1" + "".join(str(rng.randrange(10)) for _ in range(other - 1))
                for a, b in ((first, second), ("-" + first, second), (first, "-" + second)):
                    assert divide_decimal(a, b) == tuple(map(str, divmod(int(a), int(b))))
    finally:
        sys.set_int_max_str_digits(old)


def test_validation_and_digit_limit():
    for function in (divide_decimal, divide_hex):
        for value in ("", "+", "-", " 1", "1 ", "1_0", "0x10", "１２", "--1", "G"):
            with pytest.raises(ValueError):
                function(value, "2")
            with pytest.raises(ValueError):
                function("2", value)
        with pytest.raises(ZeroDivisionError):
            function("1", "-000")
        assert function("-000", "-123") == ("0", "0")
    old = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(640)
        assert divide_decimal("1" + "0" * 10000, "1" + "0" * 5000) == ("1" + "0" * 5000, "0")
        assert divide_decimal("9" * 9000, "1") == ("9" * 9000, "0")
        assert sys.get_int_max_str_digits() == 640
    finally:
        sys.set_int_max_str_digits(old)
