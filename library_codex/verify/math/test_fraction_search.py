from math import gcd

from library_codex.math.FractionSearch import stern_brocot_binary_search


def test_stern_brocot_binary_search_against_enumeration():
    for limit in range(1, 80):
        fractions = [(0, 1)]
        for denominator in range(1, limit + 1):
            for numerator in range(1, limit + 1):
                if gcd(numerator, denominator) == 1:
                    fractions.append((numerator, denominator))
        fractions.sort(key=lambda value: value[0] / value[1])
        fractions.append((1, 0))
        expected_true = next(
            value for value in fractions
            if value[1] == 0 or value[0] * value[0] >= 2 * value[1] * value[1]
        )
        true_index = fractions.index(expected_true)
        expected_false = fractions[true_index - 1]
        actual = stern_brocot_binary_search(
            lambda value: value[0] * value[0] >= 2 * value[1] * value[1],
            limit,
        )
        assert actual == (expected_false, expected_true)


def test_stern_brocot_binary_search_boundary_cases():
    assert stern_brocot_binary_search(lambda value: True, 10) == (
        (0, 1), (0, 1)
    )
    assert stern_brocot_binary_search(lambda value: False, 0) == (
        (0, 1), (1, 0)
    )

