import itertools
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.string.SuffixArray import (
    SuffixArray,
    lcp_array,
    sa_is,
    suffix_array,
    suffix_array_with_empty,
)


def brute_lcp(left, right):
    result = 0
    while result < len(left) and result < len(right) and left[result] == right[result]:
        result += 1
    return result


def validate(sequence):
    n = len(sequence)
    expected_sa = sorted(range(n), key=lambda i: sequence[i:])
    expected_lcp = [
        brute_lcp(sequence[expected_sa[i]:], sequence[expected_sa[i + 1]:])
        for i in range(max(0, n - 1))
    ]
    assert suffix_array(sequence) == expected_sa
    assert suffix_array_with_empty(sequence) == [n] + expected_sa
    assert lcp_array(sequence, expected_sa) == expected_lcp
    result = SuffixArray(sequence)
    assert result.sa == expected_sa
    assert result.lcp == expected_lcp
    assert result.distinct_substrings() == len({
        tuple(sequence[i:j]) if not isinstance(sequence, str) else sequence[i:j]
        for i in range(n) for j in range(i + 1, n + 1)
    })
    for i in range(n):
        for j in range(n):
            expected = brute_lcp(sequence[i:], sequence[j:])
            assert result.lcp_suffix(i, j) == expected
            comparison = (sequence[i:] > sequence[j:]) - (sequence[i:] < sequence[j:])
            assert result.compare_suffix(i, j) == comparison
            right_i = i + (n - i) // 2
            right_j = j + (n - j) // 2
            left_value = sequence[i:right_i]
            right_value = sequence[j:right_j]
            expected_limited = brute_lcp(left_value, right_value)
            assert result.lcp_substring(i, right_i, j, right_j) == expected_limited
            comparison = (left_value > right_value) - (left_value < right_value)
            assert result.compare_substring(i, right_i, j, right_j) == comparison


def test_all_small_strings():
    alphabet = "abc"
    for n in range(9):
        for value in itertools.product(alphabet, repeat=n):
            validate("".join(value))


def test_integer_and_unicode_sequences():
    rng = random.Random(0)
    for _ in range(5000):
        n = rng.randrange(30)
        sequence = [rng.randrange(-10, 11) for _ in range(n)]
        validate(sequence)
    for value in ("αββα🙂", "漢字かな漢字", "🙂🙃🙂🙃"):
        validate(value)
    assert sa_is([2, 1, 2, 0], 2) == [3, 1, 2, 0]


def test_sais_random_and_adversarial():
    for pattern_length in range(1, 10):
        for pattern in itertools.product(range(2), repeat=pattern_length):
            n = 40 + pattern_length
            sequence = (pattern * ((n + pattern_length - 1) // pattern_length))[:n]
            expected = sorted(range(n), key=lambda i: sequence[i:])
            assert sa_is(sequence, 1) == expected
    rng = random.Random(2)
    for _ in range(5000):
        n = rng.randrange(40, 201)
        upper = rng.randrange(1, 20)
        sequence = [rng.randrange(upper + 1) for _ in range(n)]
        expected = sorted(range(n), key=lambda i: sequence[i:])
        assert sa_is(sequence, upper) == expected


def test_search_and_static_substrings():
    rng = random.Random(1)
    for _ in range(2000):
        n = rng.randrange(30)
        text = "".join(rng.choice("abc") for _ in range(n))
        result = SuffixArray(text)
        for _ in range(20):
            m = rng.randrange(8)
            pattern = "".join(rng.choice("abcd") for _ in range(m))
            expected = [i for i in range(n) if text.startswith(pattern, i)]
            left, right = result.search(pattern)
            assert all(text[result.sa[i]:].startswith(pattern) for i in range(left, right))
            assert result.count(pattern) == len(expected)
            assert result.occurrences(pattern, True) == expected
        if n:
            a = rng.randrange(n + 1)
            b = rng.randrange(a, n + 1)
            c = rng.randrange(n + 1)
            d = rng.randrange(c, n + 1)
            first = result.substring(a, b)
            second = result.substring(c, d)
            assert first.lcp(second) == brute_lcp(text[a:b], text[c:d])
            assert first.compare(second) == ((text[a:b] > text[c:d]) - (text[a:b] < text[c:d]))
            assert (first < second) == (text[a:b] < text[c:d])


def test_large_repetitive_without_recursion():
    n = 300000
    text = "a" * n
    result = SuffixArray(text)
    assert result.sa == list(range(n - 1, -1, -1))
    assert result.lcp[0] == 1 and result.lcp[-1] == n - 1
    assert result.search("a" * 1000) == (999, n)


if __name__ == "__main__":
    test_all_small_strings()
    test_integer_and_unicode_sequences()
    test_sais_random_and_adversarial()
    test_search_and_static_substrings()
    test_large_repetitive_without_recursion()
