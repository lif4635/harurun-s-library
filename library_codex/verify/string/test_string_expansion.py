import random

from library_codex.string_sequence.EditDistance import (
    edit_distance,
    edit_distance_with_path,
)
from library_codex.string_sequence.LongestCommonSubstring import longest_common_substring
from library_codex.string_sequence.LyndonFactorization import lyndon_factorization
from library_codex.string_sequence.MinimumCyclicShift import minimum_cyclic_shift


def test_edit_distance_and_reconstructed_path():
    examples = [
        ("kitten", "sitting", 3),
        ("", "abc", 3),
        ("same", "same", 0),
        ([1, 2, 3], [1, 4, 3, 5], 2),
    ]
    for first, second, expected in examples:
        assert edit_distance(first, second) == expected
        distance, steps = edit_distance_with_path(first, second)
        assert distance == expected
        assert sum(step[0] != "match" for step in steps) == expected


def test_minimum_cyclic_shift_against_all_rotations():
    random.seed(20260821)
    for n in range(16):
        for _ in range(300):
            values = [random.randrange(4) for _ in range(n)]
            index = minimum_cyclic_shift(values)
            rotations = [values[i:] + values[:i] for i in range(n)] or [[]]
            assert values[index:] + values[:index] == min(rotations)


def test_lyndon_factorization_reconstructs_and_is_nonincreasing():
    for value in ("", "a", "ababbab", "banana", "zzxyxyx"):
        intervals = lyndon_factorization(value)
        factors = [value[left:right] for left, right in intervals]
        assert "".join(factors) == value
        assert all(factors[i] >= factors[i + 1]
                   for i in range(len(factors) - 1))
        for factor in factors:
            assert all(factor < factor[i:] + factor[:i]
                       for i in range(1, len(factor)))


def test_longest_common_substring_random_against_bruteforce():
    random.seed(20260822)
    for n in range(9):
        for m in range(9):
            for _ in range(80):
                first = "".join(str(random.randrange(3)) for _ in range(n))
                second = "".join(str(random.randrange(3)) for _ in range(m))
                length, first_range, second_range = longest_common_substring(
                    first, second
                )
                expected = max(
                    (size for size in range(min(n, m) + 1)
                     if any(first[i:i + size] == second[j:j + size]
                            for i in range(n - size + 1)
                            for j in range(m - size + 1))),
                    default=0,
                )
                assert length == expected
                assert first[first_range[0]:first_range[1]] == second[
                    second_range[0]:second_range[1]
                ]
