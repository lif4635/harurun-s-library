import random

import pytest

from library_codex.number_theory.FixedDiscreteLog import FixedDiscreteLog


def test_all_small_primes_and_roots():
    for prime in range(2, 120):
        if any(prime % d == 0 for d in range(2, prime)):
            continue
        for root in range(1, prime):
            powers = [pow(root, i, prime) for i in range(prime - 1)]
            if len(set(powers)) != prime - 1:
                with pytest.raises(ValueError):
                    FixedDiscreteLog(prime, root)
                continue
            log = FixedDiscreteLog(prime, root)
            assert [log(value) for value in powers] == list(range(prime - 1))
            assert log(0) == log(prime) == -1
            assert log(-1) == (prime - 1) // 2


def test_farey_lookup_against_all_powers():
    for prime, root in ((4099, 2), (10007, 5), (65537, 3)):
        log = FixedDiscreteLog(prime, root)
        value = 1
        for exponent in range(prime - 1):
            assert log(value) == exponent
            assert log(value - prime) == exponent
            value = value * root % prime
        before = repr(log)
        assert before == f"FixedDiscreteLog(prime={prime}, root={root})"
        assert log(root) == 1


def test_large_prime_and_input_validation():
    rng = random.Random(48621)
    prime, root = 998244353, 3
    log = FixedDiscreteLog(prime, root)
    for _ in range(2000):
        exponent = rng.randrange(prime - 1)
        assert log(pow(root, exponent, prime)) == exponent
    for prime, root in ((1, 1), (4, 3), (25, 2), (341, 2), (999999999, 2), (1000000007, 5), (7, 0), (7, 7), (7, 2)):
        with pytest.raises(ValueError):
            FixedDiscreteLog(prime, root)
