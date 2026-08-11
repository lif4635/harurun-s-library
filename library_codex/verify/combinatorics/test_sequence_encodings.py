import itertools
import math

import pytest

from library_codex.combinatorics.DeBruijnSequence import de_bruijn
from library_codex.combinatorics.FactorialNumberSystem import (
    lehmer_to_permutation,
    permutation_rank,
    permutation_to_lehmer,
    unrank_permutation,
)


def test_de_bruijn_contains_every_word_once():
    for size in range(1, 5):
        alphabet = tuple(range(size))
        for order in range(1, 6):
            sequence = de_bruijn(order, alphabet)
            assert len(sequence) == size ** order
            words = {
                tuple(sequence[(index + offset) % len(sequence)] for offset in range(order))
                for index in range(len(sequence))
            }
            assert words == set(itertools.product(alphabet, repeat=order))
    assert set(de_bruijn(3, "ab")) == {"a", "b"}
    with pytest.raises(ValueError):
        de_bruijn(0)
    with pytest.raises(ValueError):
        de_bruijn(2, "aa")


def test_factorial_number_system_all_small_permutations():
    for size in range(9):
        permutations = itertools.permutations(range(size))
        for rank, permutation in enumerate(permutations):
            code = permutation_to_lehmer(permutation)
            assert lehmer_to_permutation(code) == list(permutation)
            assert permutation_rank(permutation) == rank
            assert unrank_permutation(size, rank) == list(permutation)
        with pytest.raises(IndexError):
            unrank_permutation(size, math.factorial(size))
    with pytest.raises(ValueError):
        permutation_to_lehmer([0, 0])
    with pytest.raises(ValueError):
        lehmer_to_permutation([2, 0])
