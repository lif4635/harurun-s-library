import itertools
import math
import random

from library_codex.algorithm.BasicAlgorithms import (
    bucket_sort,
    bucket_sort_permutation,
    ensure_permutation,
    least_significant_bit_index,
    most_significant_bit_index,
    permute,
    permute_in_place,
    popcount,
)
from library_codex.algorithm.MiscAlgorithms import (
    integer_partitions,
    nearest_congruent_at_least,
    split_modular_arithmetic_progression,
)


def test_bits_sorting_and_permutations():
    rng = random.Random(51)
    for _ in range(1000):
        value = rng.randrange(1, 1 << 200)
        assert popcount(value) == bin(value).count("1")
        assert most_significant_bit_index(value) == value.bit_length() - 1
        assert least_significant_bit_index(value) == (value & -value).bit_length() - 1
    for size in range(30):
        permutation = list(range(size))
        rng.shuffle(permutation)
        values = list(range(100, 100 + size))
        expected = [values[index] for index in permutation]
        assert ensure_permutation(permutation)
        assert permute(values, permutation) == expected
        assert permute_in_place(values[:], permutation) == expected
        keys = [rng.randrange(8) for _ in range(size)]
        indices = bucket_sort_permutation(keys, 7)
        assert indices == sorted(range(size), key=keys.__getitem__)
        pairs = list(zip(keys, range(size)))
        assert bucket_sort(pairs, key=lambda pair: pair[0], maximum=7) == sorted(pairs)


def test_integer_partitions_and_nearest_congruent():
    known = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56]
    for number, count in enumerate(known):
        partitions = integer_partitions(number)
        assert len(partitions) == count
        assert len(partitions) == len(set(partitions))
        assert all(sum(partition) == number and all(
            partition[i] >= partition[i + 1] for i in range(len(partition) - 1)
        ) for partition in partitions)
    for value in range(-20, 21):
        for lower in range(-20, 21):
            for modulus in range(1, 11):
                result = nearest_congruent_at_least(value, lower, modulus)
                assert result >= lower and (result - value) % modulus == 0
                assert result - modulus < lower


def test_modular_progression_split():
    for count in range(1, 80):
        for modulus in range(1, 30):
            for multiplier in range(-3, modulus + 3):
                addend = count * 7 - modulus * 3
                runs = split_modular_arithmetic_progression(
                    multiplier, addend, count, modulus
                )
                restored = [None] * count
                for x, y, dx, dy, length in runs:
                    for offset in range(length):
                        restored[x + dx * offset] = (y + dy * offset) % modulus
                expected = [(multiplier * index + addend) % modulus
                            for index in range(count)]
                assert restored == expected
