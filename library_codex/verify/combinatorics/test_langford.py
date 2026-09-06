import pytest

from library_codex.combinatorics.Langford import langford
from library_codex.verify.combinatorics.pairing_checks import brute_exists, check_pairing


def test_small_against_exhaustive_search():
    for n in range(9):
        for hooked in (False, True):
            result = langford(n, hooked)
            assert (result is not None) == brute_exists(n, 1, hooked)
            if result is not None:
                check_pairing(result, n, 1, hooked)


def test_all_residues_and_construction_boundaries():
    for n in range(2001):
        for hooked in (False, True):
            result = langford(n, hooked)
            residues = (1, 2) if hooked else (0, 3)
            assert (result is not None) == (n % 4 in residues)
            if result is not None:
                check_pairing(result, n, 1, hooked)
                assert result == langford(n, hooked)


def test_large_pairings():
    for n in range(100000, 100004):
        hooked = n % 4 in (1, 2)
        check_pairing(langford(n, hooked), n, 1, hooked)


def test_invalid_arguments_and_fresh_results():
    with pytest.raises(ValueError):
        langford(-1)
    for n in (1.5, "3", None):
        with pytest.raises(TypeError):
            langford(n)
    for hooked in (None, "auto", 1):
        with pytest.raises(TypeError):
            langford(3, hooked)
    first = langford(3)
    first[0] = -1
    check_pairing(langford(3), 3, 1, False)
