import random
import sys

import pytest

from library_codex.number_theory.BigIntegerMultiplication import multiply_decimal, multiply_hex


@pytest.fixture(autouse=True)
def int_oracle_limit():
    old = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(max(old, 7000) if old else 0)
    try:
        yield
    finally:
        sys.set_int_max_str_digits(old)


def test_products_against_int():
    rng = random.Random(164832)
    for radix, product in ((10, multiply_decimal), (16, multiply_hex)):
        alphabet = "0123456789abcdef"[:radix]
        for size in (1, 2, 17, 127, 512, 513, 1000, 3000):
            for _ in range(8):
                a = "".join(rng.choices(alphabet, k=size))
                b = "".join(rng.choices(alphabet, k=rng.randrange(1, size + 1)))
                for sign_a, sign_b in (("", ""), ("-", "+"), ("-", "-")):
                    expected = int(sign_a + a, radix) * int(sign_b + b, radix)
                    expected = str(expected) if radix == 10 else format(expected, "X")
                    assert product(sign_a + a, sign_b + b) == expected


def test_carries_and_square():
    for radix, product, digit in ((10, multiply_decimal, "9"), (16, multiply_hex, "F")):
        for size in (31, 512, 513, 2049, 4097):
            value = digit * size
            assert product(value, value) == digit * (size - 1) + ("8" if radix == 10 else "E") + "0" * (size - 1) + "1"
            assert product(value, "2") == "1" + digit * (size - 1) + ("8" if radix == 10 else "E")
        assert product("-000", "-123") == "0"
        assert product("+00012", "-00010") == "-120"


def test_invalid_strings():
    for product in (multiply_decimal, multiply_hex):
        for value in ("", "+", "-", " 1", "1 ", "1_0", "0x10", "１２", "--1", "G"):
            with pytest.raises(ValueError):
                product(value, "2")
    with pytest.raises(ValueError):
        multiply_decimal("A", "3")


def test_hex_case_and_sparse_values():
    assert multiply_hex("-00aBc", "+00dEf") == format(-0xABC * 0xDEF, "X")
    for product in (multiply_decimal, multiply_hex):
        assert product("1" + "0" * 5000, "1" + "0" * 7000) == "1" + "0" * 12000


def test_decimal_conversion_limit_unchanged():
    sys.set_int_max_str_digits(640)
    for size in (300, 512, 3000):
        value = "9" * size
        assert multiply_decimal(value, value) == "9" * (size - 1) + "8" + "0" * (size - 1) + "1"
        assert sys.get_int_max_str_digits() == 640
