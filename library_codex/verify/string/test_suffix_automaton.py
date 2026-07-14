import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.string.SuffixAutomaton import SuffixAutomaton


def all_substrings(sequence):
    return {
        sequence[left:right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence) + 1)
    }


def occurrence_positions(sequence, pattern):
    if len(pattern) == 0:
        return list(range(len(sequence) + 1))
    return [
        left
        for left in range(len(sequence) - len(pattern) + 1)
        if sequence[left:left + len(pattern)] == pattern
    ]


def validate(sequence, alphabet=None):
    sam = SuffixAutomaton(sequence, alphabet)
    expected_substrings = all_substrings(sequence)
    assert sam.text() == sequence
    assert sam.size() == len(sam)
    assert sam.state_count <= max(1, 2 * len(sequence))
    assert len(sam.prefix_states) == len(sequence)
    assert sam.distinct_substrings() == len(expected_substrings)
    assert sam.distinct_count == len(expected_substrings)
    assert sam.number_of_substrings() == len(expected_substrings)
    assert sam.sum_distinct_substring_lengths() == sum(
        map(len, expected_substrings)
    )

    order = sam.topological_order()
    assert sorted(order) == list(range(len(sam)))
    assert [sam.length[state] for state in order] == sorted(sam.length)
    assert sam.topological_order(True) == order[::-1]
    assert sam.tsort() == order[::-1]
    assert sam.ord == order[::-1]

    tree = sam.suffix_link_tree()
    assert sum(map(len, tree)) == len(sam) - 1
    for state in range(1, len(sam)):
        assert sam.length[sam.link[state]] < sam.length[state]
        low, high = sam.state_interval(state)
        assert low == sam.length[sam.link[state]] + 1
        assert low <= high == sam.length[state]
        assert state in tree[sam.link[state]]
        assert 0 <= sam.origin[state] < len(sam)
        if sam.is_clone[state]:
            assert sam.base_occurrence[state] == 0
        else:
            assert sam.base_occurrence[state] == 1
        for symbol, child in sam.children(state):
            assert sam.transition(state, symbol) == child
            assert sam.length[state] < sam.length[child]

    expected_terminal = {0}
    for left in range(len(sequence)):
        expected_terminal.add(sam.find(sequence[left:]))
    terminal = sam.terminal_states()
    assert {
        state for state, value in enumerate(terminal) if value
    } == expected_terminal

    counts = sam.occurrence_counts()
    assert counts[0] == len(sequence)
    candidates = list(expected_substrings)
    candidates.append(sequence[:0])
    candidates.extend((sequence + sequence)[:right] for right in range(1, 4))
    for pattern in candidates:
        expected_positions = occurrence_positions(sequence, pattern)
        state = sam.find(pattern)
        assert sam.contains(pattern) == bool(expected_positions)
        assert (pattern in sam) == bool(expected_positions)
        assert sam.count(pattern) == len(expected_positions)
        assert sam.occurrences(pattern, True) == expected_positions
        assert sorted(sam.occurrences(pattern)) == expected_positions
        assert sam.first_occurrence(pattern) == (
            expected_positions[0] if expected_positions else -1
        )
        if pattern and state != -1:
            low, high = sam.state_interval(state)
            assert low <= len(pattern) <= high
            assert counts[state] == len(expected_positions)

    ordered = sorted(expected_substrings)
    for index, substring in enumerate(ordered):
        assert sam.kth_substring(index) == substring
        assert sam.kth_substring(index + 1, True) == substring
    with pytest.raises(IndexError):
        sam.kth_substring(-1)
    with pytest.raises(IndexError):
        sam.kth_substring(len(ordered))

    for minimum in range(1, len(sequence) + 2):
        eligible = [
            substring for substring in expected_substrings
            if len(occurrence_positions(sequence, substring)) >= minimum
        ]
        expected_length = max(map(len, eligible), default=0)
        length, start, state = sam.longest_repeated_substring_info(minimum)
        repeated = sam.longest_repeated_substring(minimum)
        assert length == expected_length == len(repeated)
        assert repeated == sequence[start:start + length]
        if length:
            assert sam.count(repeated) >= minimum
            assert sam.length[state] == length
    return sam


def brute_lcs_length(left, right):
    result = 0
    for i in range(len(left)):
        for j in range(len(right)):
            length = 0
            while (
                i + length < len(left)
                and j + length < len(right)
                and left[i + length] == right[j + length]
            ):
                length += 1
            if length > result:
                result = length
    return result


def test_random_against_brute():
    rng = random.Random(0)
    for _ in range(2000):
        sequence = "".join(
            rng.choice("abc") for _ in range(rng.randrange(13))
        )
        validate(sequence)
        validate(sequence, "abc")


def test_incremental_and_cache_invalidation():
    rng = random.Random(1)
    for _ in range(3000):
        sequence = "".join(
            rng.choice("abc") for _ in range(rng.randrange(30))
        )
        sam = SuffixAutomaton(alphabet="abc")
        prefix = ""
        for symbol in sequence:
            prefix += symbol
            assert sam.push(symbol) == sam.last
            assert sam.distinct_substrings() == len(all_substrings(prefix))
            sam.occurrence_counts()
            sam.topological_order()
            sam.terminal_states()
        assert sam.text() == tuple(sequence)
        assert sam.count("a") == sequence.count("a")
        assert sam.occurrences("ab", True) == occurrence_positions(sequence, "ab")


def test_longest_common_substring():
    rng = random.Random(2)
    for _ in range(5000):
        left = "".join(rng.choice("abc") for _ in range(rng.randrange(16)))
        right = "".join(rng.choice("abcd") for _ in range(rng.randrange(16)))
        for sam in (SuffixAutomaton(left), SuffixAutomaton(left, "abc")):
            length, left_start, right_start = sam.longest_common_substring(right)
            assert length == brute_lcs_length(left, right)
            assert left[left_start:left_start + length] == right[
                right_start:right_start + length
            ]


def test_integer_and_bytes_alphabets():
    sequence = (2, -1, 2, 3, 2, -1)
    validate(sequence)
    validate(sequence, (-1, 2, 3))
    data = bytes((0, 2, 0, 255, 2, 0))
    validate(data)
    validate(data, range(256))

    sam = SuffixAutomaton("ab", "ab")
    with pytest.raises(ValueError):
        sam.extend("c")
    assert sam.text() == "ab"
    assert sam.count("ab") == 1

    generic = SuffixAutomaton("ab")
    with pytest.raises(TypeError):
        generic.extend([])
    assert generic.text() == "ab"


def test_deep_without_recursion():
    size = 400000
    sequence = "a" * size
    sam = SuffixAutomaton(sequence, "ab")
    assert sam.state_count == size + 1
    assert sam.distinct_substrings() == size
    assert sam.count("a" * 1000) == size - 999
    assert sam.occurrences("a" * (size - 1), True) == [0, 1]
    assert sam.longest_repeated_substring_info()[:2] == (size - 1, 0)
    assert len(sam.topological_order()) == size + 1


if __name__ == "__main__":
    test_random_against_brute()
    test_incremental_and_cache_invalidation()
    test_longest_common_substring()
    test_integer_and_bytes_alphabets()
    test_deep_without_recursion()
