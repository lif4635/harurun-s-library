import pytest

from library_codex.combinatorics.Skolem import skolem
from library_codex.verify.combinatorics.pairing_checks import brute_exists, check_pairing


def test_small_against_exhaustive_search():
    for n in range(9):
        for hooked in (False, True):
            result = skolem(n, hooked)
            assert (result is not None) == brute_exists(n, 0, hooked)
            if result is not None:
                check_pairing(result, n, 0, hooked)


def test_all_residues_and_construction_boundaries():
    for n in range(2001):
        for hooked in (False, True):
            result = skolem(n, hooked)
            residues = (2, 3) if hooked else (0, 1)
            assert (result is not None) == (n % 4 in residues)
            if result is not None:
                check_pairing(result, n, 0, hooked)


def test_large_pairings():
    for n in range(100000, 100004):
        hooked = n % 4 in (2, 3)
        check_pairing(skolem(n, hooked), n, 0, hooked)


def test_invalid_arguments():
    with pytest.raises(ValueError):
        skolem(-1)
    for n in (1.5, "3", None):
        with pytest.raises(TypeError):
            skolem(n)
    with pytest.raises(TypeError):
        skolem(0, None)
