import itertools
import random

import pytest

from library_codex.string_sequence.EditDistance import edit_distance, edit_distance_bounded, edit_distance_with_path


def oracle(a, b):
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        new = [i]
        for j, y in enumerate(b, 1):
            new.append(min(row[j] + 1, new[-1] + 1, row[j - 1] + (x != y)))
        row = new
    return row[-1]


def test_exhaustive_binary_strings():
    strings = ["".join(s) for n in range(5) for s in itertools.product("ab", repeat=n)]
    for a in strings:
        for b in strings:
            expected = oracle(a, b)
            assert edit_distance(a, b) == expected
            for limit in range(5):
                assert edit_distance_bounded(a, b, limit) == min(expected, limit + 1)


def test_random_boundaries_and_unhashable():
    rng = random.Random(18270)
    for size in (1, 30, 31, 32, 63, 64, 65, 127, 128, 129, 256):
        a = [rng.randrange(9) for _ in range(size)]
        b = [rng.randrange(9) for _ in range(size + 3)]
        expected = oracle(a, b)
        assert edit_distance(a, b) == expected
        assert edit_distance_bounded(a, b, expected) == expected
        assert edit_distance_bounded(a, b, expected - 1) == expected
    assert edit_distance([[1], [2]], [[2], [3]]) == 2
    assert edit_distance("あいうえお", "あえお") == 2
    assert edit_distance(b"kitten", b"sitting") == 3
    with pytest.raises(ValueError):
        edit_distance_bounded("a", "b", -1)


def test_edit_distance_and_reconstructed_path():
    for first, second, expected in (("kitten", "sitting", 3), ("", "abc", 3), ("same", "same", 0), ([1, 2, 3], [1, 4, 3, 5], 2)):
        assert edit_distance(first, second) == expected
        distance, steps = edit_distance_with_path(first, second)
        assert distance == expected
        assert sum(step[0] != "match" for step in steps) == expected
