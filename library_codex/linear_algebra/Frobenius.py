"""素数modの行列の累乗・累乗和・多項式代入を、行列またはベクトルで求める。"""

from random import Random

from library_codex.linear_algebra.Matrix import inverse_matrix, matrix_multiply


def _insert(vector, columns, rows, ways, pivots, mod):
    n = len(vector)
    rank = len(columns)
    reduced = vector[:]
    weights = [0] * rank
    for pivot in range(n):
        row = rows[pivot]
        factor = reduced[pivot]
        if row is None or not factor:
            continue
        for j in range(pivot, n):
            reduced[j] = (reduced[j] - factor * row[j]) % mod
        way = ways[pivot]
        for j in range(len(way)):
            weights[j] = (weights[j] + factor * way[j]) % mod
    pivot = next((i for i in range(n) if reduced[i]), -1)
    if pivot < 0:
        return weights
    scale = pow(reduced[pivot], -1, mod)
    rows[pivot] = [value * scale % mod for value in reduced]
    ways[pivot] = [-value * scale % mod for value in weights] + [scale]
    columns.append(vector[:])
    pivots.append(pivot)
    return None


def _matvec(matrix, vector, mod):
    result = []
    for row in matrix:
        total = 0
        for j in range(len(vector)):
            total += row[j] * vector[j]
            if j & 7 == 7:
                total %= mod
        result.append(total % mod)
    return result


def _divide(values, relation, mod):
    while values and not values[-1]:
        values.pop()
    degree = len(relation)
    quotient = [0] * max(0, len(values) - degree)
    for i in range(len(values) - 1, degree - 1, -1):
        value = values[i]
        quotient[i - degree] = value
        if value:
            for j in range(degree):
                values[i - degree + j] = (values[i - degree + j] + value * relation[j]) % mod
    del values[degree:]
    while values and not values[-1]:
        values.pop()
    return quotient


def _trial(matrix, mod, rng):
    n = len(matrix)
    columns, pivots, blocks = [], [], []
    rows, ways = [None] * n, [None] * n
    while len(columns) < n:
        start = len(columns)
        first = [rng.randrange(mod) for _ in range(n)]
        if _insert(first, columns, rows, ways, pivots, mod) is not None:
            first = [0] * n
            first[next(i for i in range(n) if rows[i] is None)] = 1
            _insert(first, columns, rows, ways, pivots, mod)
        current = first
        while True:
            current = _matvec(matrix, current, mod)
            coefficients = _insert(current, columns, rows, ways, pivots, mod)
            if coefficients is not None:
                break
        relation = coefficients[start:]
        if start:
            offset = 0
            for previous in blocks:
                degree = len(previous)
                remainder = coefficients[offset:offset + degree]
                quotient = _divide(remainder, relation, mod)
                if remainder:
                    return None
                for i, value in enumerate(quotient):
                    if value:
                        column = columns[offset + i]
                        for j in range(n):
                            first[j] = (first[j] - value * column[j]) % mod
                offset += degree
            for pivot in pivots[start:]:
                rows[pivot] = ways[pivot] = None
            del pivots[start:]
            del columns[start:]
            current = first
            for i in range(len(relation)):
                if _insert(current, columns, rows, ways, pivots, mod) is not None:
                    return None
                if i + 1 < len(relation):
                    current = _matvec(matrix, current, mod)
        blocks.append(relation)
    basis = [list(row) for row in zip(*columns)]
    inverse = inverse_matrix(basis, mod)
    if inverse is None:
        return None
    return basis, inverse, blocks


def _power_x(exponent, relation, mod):
    degree = len(relation)
    if exponent < degree:
        return [0] * exponent + [1]
    result = [1]
    for bit in bin(exponent)[2:]:
        size = len(result)
        if not size:
            break
        squared = [0] * (2 * size - 1)
        for i in range(size):
            value = result[i]
            squared[2 * i] += value * value
            doubled = 2 * value
            if value:
                for j in range(i + 1, size):
                    squared[i + j] += doubled * result[j]
            if i & 3 == 3:
                squared = [value % mod for value in squared]
        result = [value % mod for value in squared]
        if bit == "1":
            result.insert(0, 0)
        _divide(result, relation, mod)
    return result


def _multiply(first, second, relation, mod):
    if not first or not second:
        return []
    result = [0] * (len(first) + len(second) - 1)
    for i, value in enumerate(first):
        if value:
            for j, other in enumerate(second):
                result[i + j] += value * other
        if i & 3 == 3:
            result = [value % mod for value in result]
    result = [value % mod for value in result]
    _divide(result, relation, mod)
    return result


def _sum_x(count, relation, mod):
    extended = [-relation[0] % mod]
    extended.extend((relation[i - 1] - relation[i]) % mod for i in range(1, len(relation)))
    extended.append((relation[-1] + 1) % mod)
    remainder = _power_x(count, extended, mod)
    result, total = [], 0
    for value in reversed(remainder[1:]):
        total = (total + value) % mod
        result.append(total)
    result.reverse()
    return result


class Frobenius:
    __slots__ = ("_matrix", "_mod", "_basis", "_inverse", "_blocks")

    def __init__(self, matrix, mod=998244353, seed=None, trials=32):
        n = len(matrix)
        if mod < 2 or trials < 1 or any(len(row) != n for row in matrix):
            raise ValueError("require a square matrix, prime mod and positive trials")
        self._matrix = [[value % mod for value in row] for row in matrix]
        self._mod = mod
        rng = Random(seed)
        for _ in range(trials):
            result = _trial(self._matrix, mod, rng)
            if result is not None:
                self._basis, self._inverse, self._blocks = result
                return
        raise ArithmeticError("Frobenius decomposition failed; retry with another seed or more trials")

    def pow(self, exponent, vector=None):
        """Aのexponent乗、またはその行列を列ベクトルに掛けた結果を返す。"""
        if exponent < 0:
            raise ValueError("exponent must be nonnegative")
        vector = self._vector(vector)
        n, mod = len(self._matrix), self._mod
        if exponent == 0:
            return [[int(i == j) for j in range(n)] for i in range(n)] if vector is None else vector
        if exponent == 1:
            return self.tolist() if vector is None else _matvec(self._matrix, vector, mod)
        return self._evaluate([_power_x(exponent, block, mod) for block in self._blocks], vector)

    def sum(self, count, vector=None):
        """IからAのcount-1乗までの和、またはその列ベクトルへの作用を返す。"""
        if count < 0:
            raise ValueError("count must be nonnegative")
        vector = self._vector(vector)
        n, mod = len(self._matrix), self._mod
        if count == 0:
            return [[0] * n for _ in range(n)] if vector is None else [0] * n
        if count == 1:
            return [[int(i == j) for j in range(n)] for i in range(n)] if vector is None else vector
        return self._evaluate([_sum_x(count, block, mod) for block in self._blocks], vector)

    def eval(self, coefficients, vector=None):
        """定数項から並べた多項式をAに代入し、行列または列ベクトルへの作用を返す。"""
        vector = self._vector(vector)
        coefficients = [value % self._mod for value in coefficients]
        remainders = []
        for block in self._blocks:
            remainder = coefficients[:]
            _divide(remainder, block, self._mod)
            remainders.append(remainder)
        return self._evaluate(remainders, vector)

    def _vector(self, vector):
        if vector is None:
            return None
        if len(vector) != len(self._matrix):
            raise ValueError("vector length must equal matrix size")
        return [value % self._mod for value in vector]

    def _evaluate(self, remainders, vector):
        n, mod = len(self._matrix), self._mod
        if vector is not None:
            coordinates = _matvec(self._inverse, vector, mod)
            transformed = [0] * n
            offset = 0
            for relation, coefficients in zip(self._blocks, remainders):
                degree = len(relation)
                values = _multiply(coefficients, coordinates[offset:offset + degree], relation, mod)
                transformed[offset:offset + len(values)] = values
                offset += degree
            return _matvec(self._basis, transformed, mod)
        transformed = [[0] * n for _ in range(n)]
        offset = 0
        for relation, coefficients in zip(self._blocks, remainders):
            degree = len(relation)
            for column in range(degree):
                for row, value in enumerate(coefficients):
                    transformed[offset + row][offset + column] = value
                if column + 1 < degree:
                    coefficients.insert(0, 0)
                    _divide(coefficients, relation, mod)
            offset += degree
        return matrix_multiply(matrix_multiply(self._basis, transformed, mod), self._inverse, mod)

    def tolist(self):
        """構築時の行列をmodで正規化した二次元listのコピーを返す。"""
        return [row[:] for row in self._matrix]

    def __str__(self):
        return str(self._matrix)

    def __repr__(self):
        return f"Frobenius({self._matrix!r}, mod={self._mod})"
