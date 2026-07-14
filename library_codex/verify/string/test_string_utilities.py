import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.string.LongestCommonSubsequence import (
    lcs_length,
    restore_lcs,
)
from library_codex.string.PrefixSubstringLCS import (
    PrefixSubstringLCS,
    prefix_substring_lcs,
)
from library_codex.string.RunLengthEncoding import (
    run_length_decode,
    run_length_encode,
)
from library_codex.string.StringSearch import StringSearch, lcp_naive
from library_codex.string.Subsequence import (
    count_distinct_subsequences,
    is_subsequence,
)


def brute_lcs_length(first, second):
    row = [0] * (len(second) + 1)
    for left_value in first:
        diagonal = 0
        for column, right_value in enumerate(second, 1):
            old = row[column]
            if left_value == right_value:
                row[column] = diagonal + 1
            elif row[column - 1] > old:
                row[column] = row[column - 1]
            diagonal = old
    return row[-1]


def brute_distinct_subsequences(sequence):
    result = {()}
    for value in sequence:
        result |= {subsequence + (value,) for subsequence in result}
    return len(result) - 1


def brute_rle(sequence):
    result = []
    for value in sequence:
        if result and result[-1][0] == value:
            result[-1] = value, result[-1][1] + 1
        else:
            result.append((value, 1))
    return result


def compare(first, second):
    return (first > second) - (first < second)


def test_run_length_encoding():
    rng = random.Random(0)
    for _ in range(5000):
        sequence = tuple(
            rng.randrange(5) for _ in range(rng.randrange(100))
        )
        encoded = run_length_encode(sequence)
        assert encoded == brute_rle(sequence)
        assert run_length_decode(encoded, tuple) == sequence
        assert run_length_encode(iter(sequence)) == encoded
    text = "aaabbccccdaa"
    assert run_length_decode(run_length_encode(text), str) == text
    data = bytes((0, 0, 1, 2, 2, 2))
    assert run_length_decode(run_length_encode(data), bytes) == data
    with pytest.raises(ValueError):
        run_length_decode(((1, -1),))


def test_distinct_subsequences_against_brute():
    rng = random.Random(1)
    for _ in range(3000):
        sequence = tuple(
            rng.randrange(5) for _ in range(rng.randrange(16))
        )
        expected = brute_distinct_subsequences(sequence)
        assert count_distinct_subsequences(sequence) == expected
        assert count_distinct_subsequences(sequence, include_empty=True) == expected + 1
        for mod in (2, 7, 998244353):
            assert count_distinct_subsequences(sequence, mod) == expected % mod
    unhashable = [[1], [2], [1], [3]]
    assert count_distinct_subsequences(unhashable) == 13
    assert is_subsequence([1, 3, 5], range(10))
    assert not is_subsequence([3, 2], range(10))


def validate_lcs(first, second):
    expected = brute_lcs_length(first, second)
    assert lcs_length(first, second) == expected
    restored = restore_lcs(first, second)
    assert len(restored) == expected
    assert is_subsequence(restored, first)
    assert is_subsequence(restored, second)


def test_lcs_against_brute():
    rng = random.Random(2)
    for _ in range(5000):
        first = "".join(
            rng.choice("abcd") for _ in range(rng.randrange(30))
        )
        second = "".join(
            rng.choice("abcd") for _ in range(rng.randrange(30))
        )
        validate_lcs(first, second)
    validate_lcs(bytes((0, 2, 1, 2, 3)), bytes((2, 0, 2, 3)))
    validate_lcs((3, -1, 2, 3), (-1, 3, 2, 3))
    first = [[1], [2], [3], [2]]
    second = [[2], [1], [3], [2]]
    validate_lcs(first, second)


def test_prefix_substring_lcs_against_brute():
    rng = random.Random(3)
    for _ in range(2000):
        first = tuple(
            rng.randrange(4) for _ in range(rng.randrange(16))
        )
        second = tuple(
            rng.randrange(4) for _ in range(rng.randrange(16))
        )
        queries = []
        solver = PrefixSubstringLCS(first, second)
        for query_id in range(50):
            prefix = rng.randrange(len(first) + 1)
            left = rng.randrange(len(second) + 1)
            right = rng.randrange(left, len(second) + 1)
            queries.append((prefix, left, right))
            assert solver.add(prefix, left, right) == query_id
        expected = [
            brute_lcs_length(first[:prefix], second[left:right])
            for prefix, left, right in queries
        ]
        assert solver.run() == expected
        assert prefix_substring_lcs(first, second, queries) == expected


def test_string_search_against_brute():
    rng = random.Random(4)
    for _ in range(1000):
        sequence = tuple(
            rng.randrange(5) for _ in range(rng.randrange(1, 50))
        )
        search = StringSearch(sequence)
        for _ in range(50):
            first = rng.randrange(len(sequence))
            second = rng.randrange(len(sequence))
            assert search.lcp(first, second) == lcp_naive(
                sequence[first:], sequence[second:]
            )
            assert search.strcmp(first, second) == compare(
                sequence[first:], sequence[second:]
            )
            left1 = rng.randrange(len(sequence) + 1)
            right1 = rng.randrange(left1, len(sequence) + 1)
            left2 = rng.randrange(len(sequence) + 1)
            right2 = rng.randrange(left2, len(sequence) + 1)
            expected_lcp = lcp_naive(
                sequence[left1:right1], sequence[left2:right2]
            )
            assert search.lcp(left1, right1, left2, right2) == expected_lcp
            assert search.lcp((left1, right1), (left2, right2)) == expected_lcp
            expected_compare = compare(
                sequence[left1:right1], sequence[left2:right2]
            )
            assert search.strcmp(left1, right1, left2, right2) == expected_compare
            assert search.strcmp((left1, right1), (left2, right2)) == expected_compare
        pattern = tuple(rng.randrange(5) for _ in range(rng.randrange(8)))
        limit = len(sequence) if not pattern else len(sequence) - len(pattern) + 1
        positions = [
            index for index in range(limit)
            if sequence[index:index + len(pattern)] == pattern
        ]
        assert search.count(pattern) == len(positions)
        assert search.occurrences(pattern, True) == positions

    empty = StringSearch(())
    assert empty.lcp(0, 0, 0, 0) == 0
    assert empty.strcmp((0, 0), (0, 0)) == 0


def test_deep_and_large_without_recursion():
    size = 20000
    first = "a" * size + "b" * size
    second = "b" * size + "a" * size
    assert lcs_length(first, second) == size
    restored = restore_lcs("ab" * 1500, "ba" * 1500)
    assert len(restored) == 2999
    assert is_subsequence(restored, "ab" * 1500)
    assert is_subsequence(restored, "ba" * 1500)
    assert count_distinct_subsequences("a" * 300000) == 300000


if __name__ == "__main__":
    test_run_length_encoding()
    test_distinct_subsequences_against_brute()
    test_lcs_against_brute()
    test_prefix_substring_lcs_against_brute()
    test_string_search_against_brute()
    test_deep_and_large_without_recursion()
