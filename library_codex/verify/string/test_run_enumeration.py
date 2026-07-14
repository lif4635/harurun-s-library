import itertools
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.string.RunEnumeration import run_enumerate
from library_codex.string.ZAlgorithm import z_algorithm


def brute_z(sequence):
    result = []
    for start in range(len(sequence)):
        length = 0
        while (
            start + length < len(sequence)
            and sequence[length] == sequence[start + length]
        ):
            length += 1
        result.append(length)
    return result


def has_period(sequence, left, right, period):
    return all(
        sequence[index] == sequence[index + period]
        for index in range(left, right - period)
    )


def brute_runs(sequence):
    n = len(sequence)
    result = []
    for period in range(1, n // 2 + 1):
        index = 0
        while index < n - period:
            if sequence[index] != sequence[index + period]:
                index += 1
                continue
            left = index
            index += 1
            while (
                index < n - period
                and sequence[index] == sequence[index + period]
            ):
                index += 1
            right = index + period
            if right - left < period << 1:
                continue
            if any(
                has_period(sequence, left, right, smaller)
                for smaller in range(1, period)
            ):
                continue
            result.append((period, left, right))
    return result


def validate_runs(sequence):
    expected = brute_runs(sequence)
    actual = run_enumerate(sequence)
    assert actual == expected
    assert len(actual) <= len(sequence)
    assert len(actual) == len(set(actual))
    assert actual == sorted(actual)
    for period, left, right in actual:
        assert 0 <= left < right <= len(sequence)
        assert right - left >= period << 1
        assert has_period(sequence, left, right, period)
        assert left == 0 or sequence[left - 1] != sequence[left - 1 + period]
        assert right == len(sequence) or sequence[right] != sequence[right - period]
        assert not any(
            has_period(sequence, left, right, smaller)
            for smaller in range(1, period)
        )


def test_z_algorithm_against_brute():
    rng = random.Random(0)
    values = ["", "a", "aaaa", "abacaba", bytes((0, 1, 0, 1, 0))]
    values.extend(
        "".join(rng.choice("abcd") for _ in range(rng.randrange(100)))
        for _ in range(5000)
    )
    values.extend(
        tuple(rng.randrange(-2, 3) for _ in range(rng.randrange(50)))
        for _ in range(1000)
    )
    for sequence in values:
        assert z_algorithm(sequence) == brute_z(sequence)


def test_exhaustive_binary_runs():
    for size in range(14):
        for sequence in itertools.product((0, 1), repeat=size):
            validate_runs(sequence)


def test_random_runs_against_brute():
    rng = random.Random(1)
    for _ in range(10000):
        sequence = "".join(
            rng.choice("abc") for _ in range(rng.randrange(35))
        )
        validate_runs(sequence)


def test_known_and_integer_sequences():
    assert run_enumerate("a" * 100) == [(1, 0, 100)]
    assert run_enumerate("ab" * 100) == [(2, 0, 200)]
    for sequence in (
        "mississippi",
        "abcabcxabcabc",
        (3, -1, 3, -1, 3, 2, 2, 2),
        bytes((0, 1, 0, 1, 0, 2, 2)),
    ):
        validate_runs(sequence)


def test_deep_without_recursion():
    size = 300000
    sequence = "ab" * (size // 2)
    assert run_enumerate(sequence) == [(2, 0, size)]
    z = z_algorithm("a" * size)
    assert z[0] == size
    assert z[-1] == 1


if __name__ == "__main__":
    test_z_algorithm_against_brute()
    test_exhaustive_binary_runs()
    test_random_runs_against_brute()
    test_known_and_integer_sequences()
    test_deep_without_recursion()
