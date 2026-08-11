import itertools

from library_codex.combinatorics.SetPartitions import set_partitions
from library_codex.number_theory.DiscreteLog import discrete_log


def test_discrete_log_all_small_moduli():
    for modulus in range(1, 90):
        for base in range(modulus):
            seen = {}
            value = 1 % modulus
            exponent = 0
            while value not in seen:
                seen[value] = exponent
                value = value * base % modulus
                exponent += 1
            for target in range(modulus):
                assert discrete_log(base, target, modulus) == seen.get(target, -1)


def test_set_partitions_bell_counts_and_exact_blocks():
    bell = [1, 1, 2, 5, 15, 52, 203]
    stirling = {
        4: [0, 1, 7, 6, 1],
        5: [0, 1, 15, 25, 10, 1],
    }
    for n, expected in enumerate(bell):
        partitions = list(set_partitions(range(n)))
        assert len(partitions) == expected
        canonical = {
            tuple(tuple(block) for block in partition)
            for partition in partitions
        }
        assert len(canonical) == expected
    for n, counts in stirling.items():
        for blocks, expected in enumerate(counts):
            assert len(list(set_partitions(range(n), blocks))) == expected
