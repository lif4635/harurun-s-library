import random

import pytest

from library_codex.linear_algebra.Frobenius import Frobenius
from library_codex.linear_algebra.Matrix import inverse_matrix, matrix_multiply, matrix_power, matrix_vector_multiply


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
        expected = matrix_power(matrix, exponent, mod)
        vector = [i - 3 for i in range(n)]
        assert form.pow(exponent) == expected
        assert form.pow(exponent, vector) == matrix_vector_multiply(expected, vector, mod)
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


def _naive_eval(matrix, coefficients, mod):
    n = len(matrix)
    result = [[0] * n for _ in range(n)]
    for coefficient in reversed(coefficients):
        result = matrix_multiply(result, matrix, mod)
        for i in range(n):
            result[i][i] = (result[i][i] + coefficient) % mod
    return result


def _binary_sum(matrix, count, mod):
    n = len(matrix)
    identity = [[int(i == j) for j in range(n)] for i in range(n)]
    block = [matrix[i][:] + identity[i] for i in range(n)]
    block += [[0] * n + identity[i] for i in range(n)]
    powered = matrix_power(block, count, mod)
    return [row[n:] for row in powered[:n]]


def test_sum_and_polynomial_random():
    rng = random.Random(286)
    for mod in (2, 3, 101, 998244353, (1 << 61) - 1):
        for n in range(8):
            matrix = [[rng.randrange(-mod, mod) for _ in range(n)] for _ in range(n)]
            form = Frobenius(matrix, mod, seed=48, trials=256)
            vector = [rng.randrange(-mod, mod) for _ in range(n)]
            for size in (0, 1, 2, n, n + 1, 3 * n + 4):
                coefficients = [rng.randrange(-mod, mod) for _ in range(size)]
                saved = coefficients[:]
                expected = _naive_eval(matrix, coefficients, mod)
                assert form.eval(coefficients) == expected
                assert form.eval(iter(coefficients), vector) == matrix_vector_multiply(expected, vector, mod)
                assert coefficients == saved
                expected = _naive_eval(matrix, [1] * size, mod)
                assert form.sum(size) == expected
                assert form.sum(size, vector) == matrix_vector_multiply(expected, vector, mod)
            for count in (10**18 + 7, 10**100):
                expected = _binary_sum(matrix, count, mod)
                assert form.sum(count) == expected
                assert form.sum(count, vector) == matrix_vector_multiply(expected, vector, mod)


def test_extensions_noncyclic_and_eigenvalue_one():
    for mod in (2, 101, 998244353):
        for diagonal in (0, 1, 3):
            matrix = [[diagonal * int(i == j) + int(i == j + 1 and i % 3) for j in range(6)] for i in range(6)]
            form = Frobenius(matrix, mod, seed=15, trials=256)
            vector = [2, -4, 7, 0, 1, 9]
            for count in (0, 1, 2, 3, 8, 10**18):
                expected = _binary_sum(matrix, count, mod)
                assert form.sum(count) == expected
                assert form.sum(count, vector) == matrix_vector_multiply(expected, vector, mod)
            for coefficients in ([], [0] * 20, [1], [1, -3, 0, 7, 0, 0], list(range(20))):
                expected = _naive_eval(matrix, coefficients, mod)
                assert form.eval(coefficients) == expected
                assert form.eval(coefficients, vector) == matrix_vector_multiply(expected, vector, mod)


def test_extensions_inputs_and_copies():
    form = Frobenius([[1, 1], [0, 1]], mod=101, seed=8)
    vector = [-1, 3]
    for call in (lambda v: form.pow(0, v), lambda v: form.pow(1, v), lambda v: form.sum(0, v),
                 lambda v: form.sum(1, v), lambda v: form.sum(9, v), lambda v: form.eval([1, 2], v)):
        result = call(vector)
        result[0] = 70
        assert vector == [-1, 3]
        assert form.tolist() == [[1, 1], [0, 1]]
        with pytest.raises(ValueError):
            call([1])
    with pytest.raises(ValueError):
        form.sum(-1)
    for call in (lambda: Frobenius([]).sum(10**50, []), lambda: Frobenius([]).eval([1, 2], [])):
        assert call() == []


def test_vector_queries_do_not_build_full_matrix(monkeypatch):
    import importlib

    form = Frobenius([[1, 1], [1, 0]], seed=19)
    module = importlib.import_module("library_codex.linear_algebra.Frobenius")
    def fail(*args):
        raise AssertionError("dense matrix product in vector query")
    monkeypatch.setattr(module, "matrix_multiply", fail)
    assert form.pow(5, [1, 0]) == [8, 5]
    assert form.sum(5, [1, 0]) == [12, 7]
    assert form.eval([2, 3, 1], [1, 0]) == [7, 4]
