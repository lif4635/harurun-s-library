import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.string.DynamicRollingHash import DynamicRollingHash
from library_codex.string.RollingHash import (
    DoubleRollingHash,
    HashString,
    ReversibleRollingHash,
    RollingHash,
    hash_sequence,
)
from library_codex.string.RollingHash2D import RollingHash2D


BASE1 = 911382323
BASE2 = 972663749


def brute_lcp(left, right):
    result = 0
    while result < len(left) and result < len(right) and left[result] == right[result]:
        result += 1
    return result


def test_static_hash_and_views():
    rng = random.Random(0)
    for _ in range(3000):
        n = rng.randrange(50)
        sequence = [rng.randrange(-100, 101) for _ in range(n)]
        first = RollingHash(sequence, BASE1)
        double = DoubleRollingHash(sequence, (BASE1, BASE2))
        reverse = ReversibleRollingHash(sequence, BASE1)
        for _ in range(100):
            left = rng.randrange(n + 1)
            right = rng.randrange(left, n + 1)
            value = sequence[left:right]
            assert first.get(left, right) == hash_sequence(value, BASE1)
            assert double.get(left, right) == hash_sequence(
                value, BASE1, BASE2
            )
            assert reverse.reverse_get(left, right) == hash_sequence(
                value[::-1], BASE1
            )
            view = reverse[left:right]
            assert view.to_hash_string() == HashString.from_sequence(
                value, BASE1, reversible=True
            )
            assert view.is_palindrome() == (value == value[::-1])

            left2 = rng.randrange(n + 1)
            right2 = rng.randrange(left2, n + 1)
            other = reverse[left2:right2]
            assert view.lcp(other) == brute_lcp(value, sequence[left2:right2])
            comparison = (
                (value > sequence[left2:right2])
                - (value < sequence[left2:right2])
            )
            assert view.compare(other) == comparison


def test_hash_string_concat_reverse_repeat():
    rng = random.Random(1)
    for _ in range(10000):
        left = [rng.randrange(20) for _ in range(rng.randrange(20))]
        right = [rng.randrange(20) for _ in range(rng.randrange(20))]
        a = HashString.from_sequence(left, BASE1, reversible=True)
        b = HashString.from_sequence(right, BASE1, reversible=True)
        joined = a + b
        assert joined == HashString.from_sequence(
            left + right, BASE1, reversible=True
        )
        assert joined.reversed() == HashString.from_sequence(
            (left + right)[::-1], BASE1, reversible=True
        )
        count = rng.randrange(20)
        assert a * count == HashString.from_sequence(
            left * count, BASE1, reversible=True
        )
        assert joined.remove_prefix(a).hash == b.hash


def test_incremental_and_find():
    rolling = RollingHash([], BASE1)
    rolling.extend("abracadabra")
    assert rolling.find("abra") == 0
    assert rolling.find("abra", 1) == 7
    assert rolling.find("xyz") == -1
    assert rolling.get() == hash_sequence("abracadabra", BASE1)


def test_dynamic_against_rebuild():
    rng = random.Random(2)
    for _ in range(1000):
        n = rng.randrange(1, 100)
        sequence = [rng.randrange(-100, 101) for _ in range(n)]
        dynamic = DynamicRollingHash(sequence, BASE1)
        for _ in range(200):
            if rng.randrange(3) == 0:
                index = rng.randrange(n)
                value = rng.randrange(-100, 101)
                sequence[index] = value
                dynamic.update(index, value)
            else:
                left = rng.randrange(n + 1)
                right = rng.randrange(left, n + 1)
                value = sequence[left:right]
                assert dynamic.get(left, right) == hash_sequence(value, BASE1)
                assert dynamic.reverse_get(left, right) == hash_sequence(
                    value[::-1], BASE1
                )
                assert dynamic.is_palindrome(left, right) == (
                    value == value[::-1]
                )


def direct_matrix_hash(matrix):
    row_hashes = [hash_sequence(row, BASE2) for row in matrix]
    return hash_sequence(row_hashes, BASE1)


def test_2d_against_direct_hash():
    rng = random.Random(3)
    for _ in range(2000):
        height = rng.randrange(10)
        width = rng.randrange(10)
        if height == 0:
            width = 0
        matrix = [
            [rng.randrange(-10, 11) for _ in range(width)]
            for _ in range(height)
        ]
        rolling = RollingHash2D(matrix, BASE1, BASE2)
        for _ in range(100):
            upper = rng.randrange(height + 1)
            lower = rng.randrange(upper, height + 1)
            left = rng.randrange(width + 1)
            right = rng.randrange(left, width + 1)
            rectangle = [row[left:right] for row in matrix[upper:lower]]
            assert rolling.get(upper, left, lower, right) == direct_matrix_hash(
                rectangle
            )
            view = rolling[upper:lower, left:right]
            assert view.hash == direct_matrix_hash(rectangle)


def test_2d_find():
    matrix = ["ababa", "babab", "ababa", "xxxxx"]
    rolling = RollingHash2D(matrix, BASE1, BASE2)
    assert rolling.find(["aba", "bab"]) == [(0, 0), (0, 2), (1, 1)]


def test_large_without_recursion():
    n = 1000000
    sequence = bytes((i * 1000003 + 97) % 251 for i in range(n))
    rolling = RollingHash(sequence, BASE1)
    assert rolling.get() == hash_sequence(sequence, BASE1)
    assert rolling.lcp(rolling, 0, n, 251, n) == n - 251


if __name__ == "__main__":
    test_static_hash_and_views()
    test_hash_string_concat_reverse_repeat()
    test_incremental_and_find()
    test_dynamic_against_rebuild()
    test_2d_against_direct_hash()
    test_2d_find()
    test_large_without_recursion()
