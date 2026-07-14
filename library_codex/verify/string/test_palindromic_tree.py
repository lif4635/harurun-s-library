import itertools
import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.string.Manacher import (
    Manacher,
    enumerate_leftmost_palindromes,
    enumerate_palindrome_lengths,
    enumerate_palindromes,
    get_palindromes,
    manacher,
    manacher_even,
    palindrome_radii,
)
from library_codex.string.PalindromicTree import PalindromicTree


def is_palindrome(sequence):
    return sequence == sequence[::-1]


def endswith(sequence, suffix):
    return sequence[len(sequence) - len(suffix):] == suffix


def brute_palindromes(sequence):
    result = {}
    for left in range(len(sequence)):
        for right in range(left + 1, len(sequence) + 1):
            value = sequence[left:right]
            if is_palindrome(value):
                result.setdefault(value, []).append(left)
    return result


def brute_radii(sequence):
    n = len(sequence)
    odd = [0] * n
    even = [0] * n
    for center in range(n):
        while (
            center - odd[center] >= 0
            and center + odd[center] < n
            and sequence[center - odd[center]]
            == sequence[center + odd[center]]
        ):
            odd[center] += 1
        while (
            center - even[center] - 1 >= 0
            and center + even[center] < n
            and sequence[center - even[center] - 1]
            == sequence[center + even[center]]
        ):
            even[center] += 1
    return odd, even


def validate_manacher(sequence):
    odd, even = brute_radii(sequence)
    assert manacher(sequence) == odd
    assert manacher_even(sequence) == even
    assert palindrome_radii(sequence) == (odd, even)
    lengths = []
    intervals = []
    invalid_empty = []
    for center in range(len(sequence)):
        lengths.append(2 * odd[center] - 1)
        intervals.append((center - odd[center] + 1, center + odd[center]))
        invalid_empty.append(intervals[-1])
        if center + 1 < len(sequence):
            radius = even[center + 1]
            lengths.append(2 * radius)
            intervals.append((center + 1 - radius, center + 1 + radius))
            invalid_empty.append(intervals[-1] if radius else (-1, -1))
    assert enumerate_palindrome_lengths(sequence) == lengths
    assert Manacher(sequence) == lengths
    assert enumerate_palindromes(sequence) == intervals
    assert get_palindromes(sequence) == invalid_empty

    expected_leftmost = []
    for right in range(1, len(sequence) + 1):
        expected_leftmost.append(min(
            left for left in range(right)
            if is_palindrome(sequence[left:right])
        ))
    assert enumerate_leftmost_palindromes(sequence) == expected_leftmost


def validate_tree(sequence, alphabet=None):
    expected = brute_palindromes(sequence)
    tree = PalindromicTree(sequence, alphabet)
    assert tree.text() == sequence
    assert tree.size() == len(tree) == tree.node_count
    assert tree.distinct_count == len(expected)
    assert tree.node_count == len(expected) + 2
    assert sum(tree.direct_count) == len(sequence)
    assert tree.total_count == sum(map(len, expected.values()))
    assert set(tree.distinct_palindromes()) == set(expected)
    assert tree.count(sequence[:0]) == len(sequence) + 1
    assert tree.occurrences(sequence[:0], True) == list(range(len(sequence) + 1))

    occurrence = tree.occurrence_counts()
    records = {}
    for length, first, count in tree.frequencies():
        records[sequence[first:first + length]] = count
    assert records == {value: len(positions) for value, positions in expected.items()}

    for value, positions in expected.items():
        node = tree.find(value)
        assert node >= 2
        assert tree.contains(value)
        assert value in tree
        assert tree.palindrome(node) == value
        assert tree.get_palindrome(node) == value
        assert tree.length[node] == len(value)
        assert tree.first_pos[node] == positions[0]
        assert tree.first_occurrence(value) == positions[0]
        assert tree.count(value) == len(positions) == occurrence[node]
        assert tree.occurrences(value, True) == positions
        assert sorted(tree.occurrences(value)) == positions

    for node in range(2, len(tree)):
        value = tree.palindrome(node)
        suffix = tree.link[node]
        suffix_value = tree.palindrome(suffix)
        assert tree.length[suffix] < tree.length[node]
        assert endswith(value, suffix_value)
        assert not any(
            len(candidate) > len(suffix_value)
            and len(candidate) < len(value)
            and endswith(value, candidate)
            for candidate in expected
        )
        parent = tree.parent[node]
        symbol = tree.parent_symbol[node]
        assert tree.transition(parent, symbol) == node
        if parent == 0:
            assert len(value) == 1 and value[0] == symbol
        else:
            assert value[0] == value[-1] == symbol
            assert value[1:-1] == tree.palindrome(parent)

    link_tree = tree.suffix_link_tree()
    assert sum(map(len, link_tree)) == len(tree) - 1
    for node in range(1, len(tree)):
        assert node in link_tree[tree.link[node]]

    for end in range(len(sequence)):
        suffix_values = [
            tree.palindrome(node)
            for node in tree.palindromic_suffixes(end)
        ]
        expected_suffixes = sorted(
            (
                value for value in expected
                if len(value) <= end + 1 and endswith(sequence[:end + 1], value)
            ),
            key=len,
            reverse=True,
        )
        assert suffix_values == expected_suffixes
        state = tree.longest_suffix_state(end)
        assert tree.palindrome(state) == expected_suffixes[0]
        assert tree.suffix_depth[state] == len(expected_suffixes)

    expected_longest = max(map(len, expected), default=0)
    longest = tree.longest_palindrome()
    assert len(longest) == expected_longest
    assert not longest or longest in expected

    if isinstance(sequence, str):
        missing = sequence + "!"
    elif isinstance(sequence, bytes):
        missing = sequence + bytes((254, 253))
    else:
        missing = sequence + (1000, 1001)
    if not is_palindrome(missing):
        assert tree.find(missing) == -1
        assert tree.count(missing) == 0
        assert tree.first_occurrence(missing) == -1
    return tree


def test_exhaustive_binary():
    for size in range(13):
        for values in itertools.product(("a", "b"), repeat=size):
            sequence = "".join(values)
            validate_manacher(sequence)
            validate_tree(sequence)
            validate_tree(sequence, "ab")


def test_random_against_brute():
    rng = random.Random(0)
    for _ in range(5000):
        sequence = "".join(
            rng.choice("abc") for _ in range(rng.randrange(25))
        )
        validate_manacher(sequence)
        validate_tree(sequence, "abc")


def test_online_and_atomic_failure():
    sequence = "abacabadabacaba"
    tree = PalindromicTree(alphabet="abcd")
    prefix = ""
    for symbol in sequence:
        prefix += symbol
        assert tree.push(symbol) == tree.last
        tree.occurrence_counts()
        tree.occurrences(symbol)
        expected = brute_palindromes(prefix)
        assert tree.distinct_count == len(expected)
        assert tree.total_count == sum(map(len, expected.values()))
    assert tree.text() == tuple(sequence)
    before = tree.node_count, len(tree.sequence), tree.total_count
    with pytest.raises(ValueError):
        tree.extend("z")
    assert (tree.node_count, len(tree.sequence), tree.total_count) == before

    generic = PalindromicTree("aba")
    with pytest.raises(TypeError):
        generic.extend([])
    assert generic.text() == "aba"


def test_integer_and_bytes_sequences():
    integers = (2, -1, 2, 2, -1, 2)
    validate_manacher(integers)
    validate_tree(integers)
    validate_tree(integers, (-1, 2))
    data = bytes((0, 2, 0, 255, 0, 2, 0))
    validate_manacher(data)
    validate_tree(data)
    validate_tree(data, range(256))


def test_deep_without_recursion():
    size = 400000
    sequence = "a" * size
    tree = PalindromicTree(sequence, "ab")
    assert tree.node_count == size + 2
    assert tree.distinct_count == size
    assert tree.total_count == size * (size + 1) // 2
    assert tree.count("a" * 1000) == size - 999
    assert tree.occurrences("a" * (size - 1), True) == [0, 1]
    assert len(tree.longest_palindrome()) == size
    odd, even = palindrome_radii(sequence)
    assert odd[size // 2] == size // 2
    assert even[size // 2] == size // 2


if __name__ == "__main__":
    test_exhaustive_binary()
    test_random_against_brute()
    test_online_and_atomic_failure()
    test_integer_and_bytes_sequences()
    test_deep_without_recursion()
