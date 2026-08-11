import math

from library_codex.number_theory.DigitFrequency import digit_frequency
from library_codex.number_theory.PythagoreanTriples import pythagorean_triples


def _digits(value, base):
    if value == 0:
        return [0]
    result = []
    while value:
        result.append(value % base)
        value //= base
    return result


def test_digit_frequency_against_formatting():
    for base in range(2, 17):
        for lower in range(35):
            for upper in range(lower, 80):
                expected = [0] * base
                for value in range(lower, upper):
                    for digit in _digits(value, base):
                        expected[digit] += 1
                assert digit_frequency(lower, upper, base) == expected


def test_pythagorean_triples_against_bruteforce():
    for limit in range(80):
        expected = {
            (first, second, hypotenuse)
            for first in range(1, limit + 1)
            for second in range(first + 1, limit + 1)
            for hypotenuse in range(second + 1, limit + 1)
            if first * first + second * second == hypotenuse * hypotenuse
        }
        actual = set(pythagorean_triples(limit))
        assert actual == expected
        primitive = set(pythagorean_triples(limit, True))
        assert primitive == {triple for triple in expected if math.gcd(triple[0], triple[1]) == 1}
