import random

import pytest

from library_codex.linear_algebra.Frobenius import Frobenius
from library_codex.linear_algebra.Matrix import inverse_matrix, matrix_multiply, matrix_power


def _check(matrix, mod, seed):
    saved = [row[:] for row in matrix]
    form = Frobenius(matrix, mod, seed=seed, trials=128)
    n = len(matrix)
    normal = [[x % mod for x in row] for row in matrix]
    assert form.tolist() == normal
    companion = [[0] * n for _ in range(n)]
    offset = 0
    for relation in form._blocks:
        degree = len(relation)
        assert degree
        for i in range(degree - 1):
            companion[offset + i + 1][offset + i] = 1
        for i, value in enumerate(relation):
            companion[offset + i][offset + degree - 1] = value
        offset += degree
    assert offset == n
    assert matrix_multiply(normal, form._basis, mod) == matrix_multiply(form._basis, companion, mod)
    for exponent in (0, 1, 2, 3, 7, 32, 10**18 + 37):
        assert form.pow(exponent) == matrix_power(matrix, exponent, mod)
    assert matrix == saved
    copied = form.tolist()
    if n:
        copied[0][0] += 1
    assert form.tolist() == normal
    assert str(form) == str(normal)
    assert repr(form) == f"Frobenius({normal!r}, mod={mod})"
    return form


def test_random_matrices():
    rng = random.Random(20261120)
    for mod in (2, 3, 5, 101, 998244353, 1000000007, (1 << 61) - 1):
        for n in range(9):
            for seed in range(5):
                matrix = [[rng.randrange(-mod, mod) for _ in range(n)] for _ in range(n)]
                _check(matrix, mod, seed)


def test_repeated_and_noncyclic_blocks():
    rng = random.Random(71)
    for mod in (2, 101, 998244353):
        for lengths in ((8,), (4, 4), (3, 2, 2, 1), (1,) * 8):
            for eigenvalue in (0, 1, mod - 1):
                n = sum(lengths)
                matrix = [[0] * n for _ in range(n)]
                offset = 0
                for length in lengths:
                    for i in range(length):
                        matrix[offset + i][offset + i] = eigenvalue
                        if i:
                            matrix[offset + i][offset + i - 1] = 1
                    offset += length
                while True:
                    basis = [[rng.randrange(mod) for _ in range(n)] for _ in range(n)]
                    inverse = inverse_matrix(basis, mod)
                    if inverse is not None:
                        break
                matrix = matrix_multiply(matrix_multiply(basis, matrix, mod), inverse, mod)
                _check(matrix, mod, 96)


def test_permutation_and_boundaries():
    permutation = [1, 2, 0, 4, 3, 5]
    matrix = [[int(permutation[i] == j) for j in range(6)] for i in range(6)]
    _check(matrix, 998244353, 7)
    assert Frobenius([], seed=1).pow(10**100) == []
    assert Frobenius([[3]], seed=1).pow(10**100) == [[pow(3, 10**100, 998244353)]]
    with pytest.raises(ValueError):
        Frobenius([[1, 2]])
    with pytest.raises(ValueError):
        Frobenius([[1]], mod=1)
    with pytest.raises(ValueError):
        Frobenius([[1]], trials=0)
    with pytest.raises(ValueError):
        Frobenius([[1]]).pow(-1)


def test_failed_trial_never_returns_a_matrix(monkeypatch):
    import importlib

    module = importlib.import_module("library_codex.linear_algebra.Frobenius")
    monkeypatch.setattr(module, "_trial", lambda *args: None)
    with pytest.raises(ArithmeticError):
        module.Frobenius([[1]], seed=1, trials=2)
