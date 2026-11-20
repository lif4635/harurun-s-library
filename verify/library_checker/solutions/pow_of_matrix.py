DEFAULT_MOD = 998244353

def _linear_algebra_matrix_shape(matrix):
    height = len(matrix)
    width = len(matrix[0]) if height else 0
    for row in matrix:
        if len(row) != width:
            raise ValueError('matrix rows must have equal length')
    return (height, width)

def identity_matrix(size):
    return [[int(row == column) for column in range(size)] for row in range(size)]

def transpose_matrix(matrix):
    (height, width) = _linear_algebra_matrix_shape(matrix)
    return [[matrix[row][column] for row in range(height)] for column in range(width)]

def rotate_matrix(matrix, turns=1):
    result = [list(row) for row in matrix]
    turns %= 4
    for _ in range(turns):
        (height, width) = _linear_algebra_matrix_shape(result)
        result = [[result[height - 1 - row][column] for row in range(height)] for column in range(width)]
    return result

def matrix_add(first, second, mod=DEFAULT_MOD):
    shape = _linear_algebra_matrix_shape(first)
    if _linear_algebra_matrix_shape(second) != shape:
        raise ValueError('matrix shapes must be equal')
    return [[(left + right) % mod for (left, right) in zip(row, other)] for (row, other) in zip(first, second)]

def matrix_subtract(first, second, mod=DEFAULT_MOD):
    shape = _linear_algebra_matrix_shape(first)
    if _linear_algebra_matrix_shape(second) != shape:
        raise ValueError('matrix shapes must be equal')
    return [[(left - right) % mod for (left, right) in zip(row, other)] for (row, other) in zip(first, second)]

def matrix_multiply(first, second, mod=DEFAULT_MOD):
    (height, inner) = _linear_algebra_matrix_shape(first)
    (other_height, width) = _linear_algebra_matrix_shape(second)
    if inner != other_height:
        raise ValueError('incompatible matrix shapes')
    result = [[0] * width for _ in range(height)]
    if 0 < mod <= 1 << 30:
        right = [[value % mod for value in row] for row in second]
        for row in range(height):
            output = result[row]
            remaining = 0
            for (pivot, value) in enumerate(first[row]):
                left = value % mod
                if not left:
                    continue
                source = right[pivot]
                if remaining:
                    for column in range(width):
                        output[column] += left * source[column]
                    remaining -= 1
                else:
                    for column in range(width):
                        output[column] = (output[column] + left * source[column]) % mod
                    remaining = 7
            for column in range(width):
                output[column] %= mod
        return result
    for row in range(height):
        output = result[row]
        for (pivot, left) in enumerate(first[row]):
            if left:
                source = second[pivot]
                for column in range(width):
                    output[column] += left * source[column]
        for column in range(width):
            output[column] %= mod
    return result

def matrix_vector_multiply(matrix, vector, mod=DEFAULT_MOD):
    (height, width) = _linear_algebra_matrix_shape(matrix)
    if width != len(vector):
        raise ValueError('incompatible matrix and vector sizes')
    result = [0] * height
    for row in range(height):
        total = 0
        source = matrix[row]
        for column in range(width):
            total += source[column] * vector[column]
        result[row] = total % mod
    return result

def matrix_power(matrix, exponent, mod=DEFAULT_MOD):
    (height, width) = _linear_algebra_matrix_shape(matrix)
    if height != width:
        raise ValueError('matrix must be square')
    if exponent < 0:
        raise ValueError('exponent must be nonnegative')
    result = identity_matrix(height)
    base = [[value % mod for value in row] for row in matrix]
    while exponent:
        if exponent & 1:
            result = matrix_multiply(result, base, mod)
        exponent >>= 1
        if exponent:
            base = matrix_multiply(base, base, mod)
    return result

def gauss_elimination(matrix, mod=DEFAULT_MOD, pivot_end=None, reduced=False):
    (height, width) = _linear_algebra_matrix_shape(matrix)
    if pivot_end is None:
        pivot_end = width
    if not 0 <= pivot_end <= width:
        raise ValueError('invalid pivot_end')
    values = [[value % mod for value in row] for row in matrix]
    rank = 0
    determinant = 1
    pivots = []
    for column in range(pivot_end):
        pivot = rank
        while pivot < height and values[pivot][column] == 0:
            pivot += 1
        if pivot == height:
            determinant = 0
            continue
        if pivot != rank:
            (values[rank], values[pivot]) = (values[pivot], values[rank])
            determinant = -determinant
        pivot_value = values[rank][column]
        determinant = determinant * pivot_value % mod
        inverse = pow(pivot_value, -1, mod)
        pivot_row = values[rank]
        if reduced:
            for index in range(column, width):
                pivot_row[index] = pivot_row[index] * inverse % mod
            first_row = 0
        else:
            first_row = rank + 1
        for row in range(first_row, height):
            if row == rank:
                continue
            target = values[row]
            coefficient = target[column]
            if coefficient == 0:
                continue
            if not reduced:
                coefficient = coefficient * inverse % mod
            target[column] = 0
            for index in range(column + 1, width):
                target[index] = (target[index] - coefficient * pivot_row[index]) % mod
        pivots.append(column)
        rank += 1
        if rank == height:
            break
    return (rank, determinant % mod, values, pivots)

def matrix_rank(matrix, mod=DEFAULT_MOD):
    return gauss_elimination(matrix, mod)[0]

def matrix_determinant(matrix, mod=DEFAULT_MOD):
    (height, width) = _linear_algebra_matrix_shape(matrix)
    if height != width:
        raise ValueError('matrix must be square')
    if height == 0:
        return 1
    (rank, determinant, _, _) = gauss_elimination(matrix, mod)
    return determinant if rank == height else 0

def inverse_matrix(matrix, mod=DEFAULT_MOD):
    (size, width) = _linear_algebra_matrix_shape(matrix)
    if size != width:
        raise ValueError('matrix must be square')
    if size == 0:
        return []
    augmented = [[value % mod for value in row] + [int(index == column) for column in range(size)] for (index, row) in enumerate(matrix)]
    (rank, _, reduced, _) = gauss_elimination(augmented, mod, size, True)
    if rank != size:
        return None
    return [row[size:] for row in reduced]

def linear_equation(matrix, vector, mod=DEFAULT_MOD):
    (height, width) = _linear_algebra_matrix_shape(matrix)
    if len(vector) != height:
        raise ValueError('right-hand side has invalid length')
    augmented = [[value % mod for value in row] + [vector[index] % mod] for (index, row) in enumerate(matrix)]
    (rank, _, reduced, pivots) = gauss_elimination(augmented, mod, width, True)
    for row in range(rank, height):
        if reduced[row][width]:
            return None
    particular = [0] * width
    for (row, column) in enumerate(pivots):
        particular[column] = reduced[row][width]
    pivot_set = set(pivots)
    basis = []
    for free in range(width):
        if free in pivot_set:
            continue
        direction = [0] * width
        direction[free] = 1
        for (row, column) in enumerate(pivots):
            direction[column] = -reduced[row][free] % mod
        basis.append(direction)
    return (particular, basis)

def sparse_linear_equation(matrix, vector, width=None, mod=DEFAULT_MOD, elimination_band=None):
    height = len(matrix)
    if len(vector) != height:
        raise ValueError('right-hand side has invalid length')
    if width is None:
        width = 0
        for row in matrix:
            if row:
                width = max(width, max(row) + 1)
    if width < 0:
        raise ValueError('width must be nonnegative')
    if elimination_band is not None and elimination_band < 0:
        raise ValueError('elimination_band must be nonnegative')
    values = []
    for source in matrix:
        row = {}
        for (column, value) in source.items():
            if not 0 <= column < width:
                raise ValueError('column index out of range')
            value %= mod
            if value:
                row[column] = value
        values.append(row)
    right = [value % mod for value in vector]
    pivots = [-1] * width
    rank = 0
    for column in range(width):
        pivot = rank
        while pivot < height and values[pivot].get(column, 0) == 0:
            pivot += 1
        if pivot == height:
            continue
        if pivot != rank:
            (values[rank], values[pivot]) = (values[pivot], values[rank])
            (right[rank], right[pivot]) = (right[pivot], right[rank])
        pivot_row = values[rank]
        inverse = pow(pivot_row[column], -1, mod)
        normalized = []
        for (index, value) in list(pivot_row.items()):
            value = value * inverse % mod
            if value:
                pivot_row[index] = value
                normalized.append((index, value))
            else:
                del pivot_row[index]
        right[rank] = right[rank] * inverse % mod
        end = height
        if elimination_band is not None:
            end = min(end, rank + elimination_band + 1)
        for row in range(rank + 1, end):
            target = values[row]
            coefficient = target.get(column, 0)
            if coefficient == 0:
                continue
            for (index, value) in normalized:
                updated = (target.get(index, 0) - coefficient * value) % mod
                if updated:
                    target[index] = updated
                else:
                    target.pop(index, None)
            right[row] = (right[row] - coefficient * right[rank]) % mod
        pivots[column] = rank
        rank += 1
        if rank == height:
            break
    result = [0] * width
    for column in range(width - 1, -1, -1):
        row = pivots[column]
        if row < 0:
            continue
        total = right[row]
        for (index, value) in values[row].items():
            if index != column:
                total -= value * result[index]
        result[column] = total % mod
    for row in range(height):
        total = 0
        for (column, value) in values[row].items():
            total += value * result[column]
        if total % mod != right[row]:
            return None
    return result

def characteristic_polynomial(matrix, mod=DEFAULT_MOD):
    (size, width) = _linear_algebra_matrix_shape(matrix)
    if size != width:
        raise ValueError('matrix must be square')
    if size == 0:
        return [1]
    hessenberg = [[value % mod for value in row] for row in matrix]
    for column in range(size - 2):
        pivot = column + 1
        while pivot < size and hessenberg[pivot][column] == 0:
            pivot += 1
        if pivot == size:
            continue
        if pivot != column + 1:
            (hessenberg[column + 1], hessenberg[pivot]) = (hessenberg[pivot], hessenberg[column + 1])
            for row in hessenberg:
                (row[column + 1], row[pivot]) = (row[pivot], row[column + 1])
        inverse = pow(hessenberg[column + 1][column], -1, mod)
        source = hessenberg[column + 1]
        for row in range(column + 2, size):
            target = hessenberg[row]
            if target[column] == 0:
                continue
            coefficient = target[column] * inverse % mod
            for index in range(column, size):
                target[index] = (target[index] - coefficient * source[index]) % mod
            for index in range(size):
                hessenberg[index][column + 1] = (hessenberg[index][column + 1] + coefficient * hessenberg[index][row]) % mod
    polynomials = [[1]]
    for row in range(size):
        current = [0] * (row + 2)
        previous = polynomials[row]
        diagonal = hessenberg[row][row]
        for (degree, value) in enumerate(previous):
            current[degree + 1] = (current[degree + 1] + value) % mod
            current[degree] = (current[degree] - diagonal * value) % mod
        product = 1
        for earlier in range(row - 1, -1, -1):
            product = product * hessenberg[earlier + 1][earlier] % mod
            coefficient = -hessenberg[earlier][row] * product % mod
            source = polynomials[earlier]
            for (degree, value) in enumerate(source):
                current[degree] = (current[degree] + coefficient * value) % mod
        polynomials.append(current)
    return polynomials[size]
mat_add = matrix_add
mat_sub = matrix_subtract
mat_mul = matrix_multiply
mat_pow = matrix_power
mat_inv = inverse_matrix
determinant = matrix_determinant
rank = matrix_rank
GaussElimination = gauss_elimination
LinearEquation = linear_equation
LinearEquation_hashmap = sparse_linear_equation
CharacteristicPolynomial = characteristic_polynomial
'素数modの行列の累乗・累乗和・多項式代入を、行列またはベクトルで求める。'
from random import Random

def _linear_algebra_frobenius_insert(vector, columns, rows, ways, pivots, mod):
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

def _linear_algebra_frobenius_matvec(matrix, vector, mod):
    result = []
    for row in matrix:
        total = 0
        for j in range(len(vector)):
            total += row[j] * vector[j]
            if j & 7 == 7:
                total %= mod
        result.append(total % mod)
    return result

def _linear_algebra_frobenius_divide(values, relation, mod):
    while values and (not values[-1]):
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
    while values and (not values[-1]):
        values.pop()
    return quotient

def _linear_algebra_frobenius_trial(matrix, mod, rng):
    n = len(matrix)
    (columns, pivots, blocks) = ([], [], [])
    (rows, ways) = ([None] * n, [None] * n)
    while len(columns) < n:
        start = len(columns)
        first = [rng.randrange(mod) for _ in range(n)]
        if _linear_algebra_frobenius_insert(first, columns, rows, ways, pivots, mod) is not None:
            first = [0] * n
            first[next((i for i in range(n) if rows[i] is None))] = 1
            _linear_algebra_frobenius_insert(first, columns, rows, ways, pivots, mod)
        current = first
        while True:
            current = _linear_algebra_frobenius_matvec(matrix, current, mod)
            coefficients = _linear_algebra_frobenius_insert(current, columns, rows, ways, pivots, mod)
            if coefficients is not None:
                break
        relation = coefficients[start:]
        if start:
            offset = 0
            for previous in blocks:
                degree = len(previous)
                remainder = coefficients[offset:offset + degree]
                quotient = _linear_algebra_frobenius_divide(remainder, relation, mod)
                if remainder:
                    return None
                for (i, value) in enumerate(quotient):
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
                if _linear_algebra_frobenius_insert(current, columns, rows, ways, pivots, mod) is not None:
                    return None
                if i + 1 < len(relation):
                    current = _linear_algebra_frobenius_matvec(matrix, current, mod)
        blocks.append(relation)
    basis = [list(row) for row in zip(*columns)]
    inverse = inverse_matrix(basis, mod)
    if inverse is None:
        return None
    return (basis, inverse, blocks)

def _linear_algebra_frobenius_power_x(exponent, relation, mod):
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
        if bit == '1':
            result.insert(0, 0)
        _linear_algebra_frobenius_divide(result, relation, mod)
    return result

def _linear_algebra_frobenius_multiply(first, second, relation, mod):
    if not first or not second:
        return []
    result = [0] * (len(first) + len(second) - 1)
    for (i, value) in enumerate(first):
        if value:
            for (j, other) in enumerate(second):
                result[i + j] += value * other
        if i & 3 == 3:
            result = [value % mod for value in result]
    result = [value % mod for value in result]
    _linear_algebra_frobenius_divide(result, relation, mod)
    return result

def _linear_algebra_frobenius_sum_x(count, relation, mod):
    extended = [-relation[0] % mod]
    extended.extend(((relation[i - 1] - relation[i]) % mod for i in range(1, len(relation))))
    extended.append((relation[-1] + 1) % mod)
    remainder = _linear_algebra_frobenius_power_x(count, extended, mod)
    (result, total) = ([], 0)
    for value in reversed(remainder[1:]):
        total = (total + value) % mod
        result.append(total)
    result.reverse()
    return result

class Frobenius:
    __slots__ = ('_matrix', '_mod', '_basis', '_inverse', '_blocks')

    def __init__(self, matrix, mod=998244353, seed=None, trials=32):
        n = len(matrix)
        if mod < 2 or trials < 1 or any((len(row) != n for row in matrix)):
            raise ValueError('require a square matrix, prime mod and positive trials')
        self._matrix = [[value % mod for value in row] for row in matrix]
        self._mod = mod
        rng = Random(seed)
        for _ in range(trials):
            result = _linear_algebra_frobenius_trial(self._matrix, mod, rng)
            if result is not None:
                (self._basis, self._inverse, self._blocks) = result
                return
        raise ArithmeticError('Frobenius decomposition failed; retry with another seed or more trials')

    def pow(self, exponent, vector=None):
        """Aのexponent乗、またはその行列を列ベクトルに掛けた結果を返す。"""
        if exponent < 0:
            raise ValueError('exponent must be nonnegative')
        vector = self._vector(vector)
        (n, mod) = (len(self._matrix), self._mod)
        if exponent == 0:
            return [[int(i == j) for j in range(n)] for i in range(n)] if vector is None else vector
        if exponent == 1:
            return self.tolist() if vector is None else _linear_algebra_frobenius_matvec(self._matrix, vector, mod)
        return self._evaluate([_linear_algebra_frobenius_power_x(exponent, block, mod) for block in self._blocks], vector)

    def sum(self, count, vector=None):
        """IからAのcount-1乗までの和、またはその列ベクトルへの作用を返す。"""
        if count < 0:
            raise ValueError('count must be nonnegative')
        vector = self._vector(vector)
        (n, mod) = (len(self._matrix), self._mod)
        if count == 0:
            return [[0] * n for _ in range(n)] if vector is None else [0] * n
        if count == 1:
            return [[int(i == j) for j in range(n)] for i in range(n)] if vector is None else vector
        return self._evaluate([_linear_algebra_frobenius_sum_x(count, block, mod) for block in self._blocks], vector)

    def eval(self, coefficients, vector=None):
        """定数項から並べた多項式をAに代入し、行列または列ベクトルへの作用を返す。"""
        vector = self._vector(vector)
        coefficients = [value % self._mod for value in coefficients]
        remainders = []
        for block in self._blocks:
            remainder = coefficients[:]
            _linear_algebra_frobenius_divide(remainder, block, self._mod)
            remainders.append(remainder)
        return self._evaluate(remainders, vector)

    def _vector(self, vector):
        if vector is None:
            return None
        if len(vector) != len(self._matrix):
            raise ValueError('vector length must equal matrix size')
        return [value % self._mod for value in vector]

    def _evaluate(self, remainders, vector):
        (n, mod) = (len(self._matrix), self._mod)
        if vector is not None:
            coordinates = _linear_algebra_frobenius_matvec(self._inverse, vector, mod)
            transformed = [0] * n
            offset = 0
            for (relation, coefficients) in zip(self._blocks, remainders):
                degree = len(relation)
                values = _linear_algebra_frobenius_multiply(coefficients, coordinates[offset:offset + degree], relation, mod)
                transformed[offset:offset + len(values)] = values
                offset += degree
            return _linear_algebra_frobenius_matvec(self._basis, transformed, mod)
        transformed = [[0] * n for _ in range(n)]
        offset = 0
        for (relation, coefficients) in zip(self._blocks, remainders):
            degree = len(relation)
            for column in range(degree):
                for (row, value) in enumerate(coefficients):
                    transformed[offset + row][offset + column] = value
                if column + 1 < degree:
                    coefficients.insert(0, 0)
                    _linear_algebra_frobenius_divide(coefficients, relation, mod)
            offset += degree
        return matrix_multiply(matrix_multiply(self._basis, transformed, mod), self._inverse, mod)

    def tolist(self):
        """構築時の行列をmodで正規化した二次元listのコピーを返す。"""
        return [row[:] for row in self._matrix]

    def __str__(self):
        return str(self._matrix)

    def __repr__(self):
        return f'Frobenius({self._matrix!r}, mod={self._mod})'
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, exponent) = map(int, read().split())
    matrix = [list(map(int, read().split())) for _ in range(n)]
    product = Frobenius(matrix).pow(exponent)
    sys.stdout.write('\n'.join((' '.join(map(str, row)) for row in product)))
if __name__ == '__main__':
    main()
