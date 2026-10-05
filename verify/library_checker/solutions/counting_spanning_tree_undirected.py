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
_linear_algebra_advanced_matrix_DEFAULT_MOD = 998244353

def determinant_arbitrary_mod(matrix, mod):
    if mod <= 0:
        raise ValueError('mod must be positive')
    size = len(matrix)
    for row in matrix:
        if len(row) != size:
            raise ValueError('matrix must be square')
    values = [[value % mod for value in row] for row in matrix]
    sign = 1
    for column in range(size):
        pivot = column
        while pivot < size and values[pivot][column] == 0:
            pivot += 1
        if pivot == size:
            return 0
        if pivot != column:
            (values[column], values[pivot]) = (values[pivot], values[column])
            sign = -sign
        for row in range(column + 1, size):
            while values[row][column]:
                quotient = values[column][column] // values[row][column]
                source = values[row]
                target = values[column]
                for index in range(column, size):
                    target[index] = (target[index] - quotient * source[index]) % mod
                (values[column], values[row]) = (values[row], values[column])
                sign = -sign
    result = sign
    for index in range(size):
        result = result * values[index][index] % mod
    return result % mod

def _linear_algebra_advanced_matrix_add_product_shift(target, first, second, limit, mod):
    for left in range(limit - 1):
        value = first[left]
        if value == 0:
            continue
        upper = limit - 1 - left
        for right in range(upper):
            target[left + right + 1] += value * second[right]
    for index in range(limit):
        target[index] %= mod

def hafnian(matrix, mod=_linear_algebra_advanced_matrix_DEFAULT_MOD):
    size = len(matrix)
    if size & 1:
        raise ValueError('hafnian requires even dimension')
    for row in matrix:
        if len(row) != size:
            raise ValueError('matrix must be square')
    limit = size // 2 + 1
    values = []
    for row in range(size):
        current = []
        for column in range(row):
            polynomial = [0] * limit
            polynomial[0] = matrix[row][column] % mod
            current.append(polynomial)
        values.append(current)
    stack = [[values, 0, None, None]]
    returned = None
    while stack:
        frame = stack[-1]
        (current, phase, reduced, zero) = frame
        if not current:
            returned = [1] + [0] * (limit - 1)
            stack.pop()
            continue
        last = len(current) - 2
        if phase == 0:
            reduced = [[polynomial[:] for polynomial in row] for row in current[:last]]
            frame[1] = 1
            frame[2] = reduced
            stack.append([reduced, 0, None, None])
            continue
        if phase == 1:
            zero = returned
            frame[1] = 2
            frame[3] = zero
            for row in range(last):
                for column in range(row):
                    _linear_algebra_advanced_matrix_add_product_shift(reduced[row][column], current[last][row], current[last + 1][column], limit, mod)
                    _linear_algebra_advanced_matrix_add_product_shift(reduced[row][column], current[last + 1][row], current[last][column], limit, mod)
            stack.append([reduced, 0, None, None])
            continue
        one = returned
        result = [(one[index] - zero[index]) % mod for index in range(limit)]
        _linear_algebra_advanced_matrix_add_product_shift(result, one, current[last + 1][last], limit, mod)
        returned = result
        stack.pop()
    return returned[-1]

def pfaffian(matrix, mod=_linear_algebra_advanced_matrix_DEFAULT_MOD):
    size = len(matrix)
    if size & 1:
        raise ValueError('pfaffian requires even dimension')
    for row in matrix:
        if len(row) != size:
            raise ValueError('matrix must be square')
    values = [[value % mod for value in row] for row in matrix]
    result = 1
    for left in range(0, size, 2):
        pivot = left + 1
        while pivot < size and values[left][pivot] == 0:
            pivot += 1
        if pivot == size:
            return 0
        if pivot != left + 1:
            (values[left + 1], values[pivot]) = (values[pivot], values[left + 1])
            for row in values:
                (row[left + 1], row[pivot]) = (row[pivot], row[left + 1])
            result = -result
        paired = left + 1
        pivot_value = values[left][paired]
        result = result * pivot_value % mod
        inverse = pow(pivot_value, -1, mod)
        for row in range(paired + 1, size):
            for column in range(row + 1, size):
                correction = (values[left][row] * values[paired][column] - values[left][column] * values[paired][row]) % mod
                value = (values[row][column] - correction * inverse) % mod
                values[row][column] = value
                values[column][row] = -value % mod
    return result % mod

def spanning_tree_count(vertex_count, edges, mod=_linear_algebra_advanced_matrix_DEFAULT_MOD):
    if vertex_count < 0:
        raise ValueError('vertex_count must be nonnegative')
    if vertex_count <= 1:
        return 1
    size = vertex_count - 1
    laplacian = [[0] * size for _ in range(size)]
    for edge in edges:
        if len(edge) == 2:
            (first, second) = edge
            weight = 1
        else:
            (first, second, weight) = edge
        weight %= mod
        if first < size:
            laplacian[first][first] = (laplacian[first][first] + weight) % mod
        if second < size:
            laplacian[second][second] = (laplacian[second][second] + weight) % mod
        if first < size and second < size:
            laplacian[first][second] = (laplacian[first][second] - weight) % mod
            laplacian[second][first] = (laplacian[second][first] - weight) % mod
    return matrix_determinant(laplacian, mod)

def directed_spanning_tree_count(vertex_count, edges, root, inward=True, mod=_linear_algebra_advanced_matrix_DEFAULT_MOD):
    if not 0 <= root < vertex_count:
        raise ValueError('invalid root')
    if vertex_count == 1:
        return 1
    laplacian = [[0] * vertex_count for _ in range(vertex_count)]
    for edge in edges:
        if len(edge) == 2:
            (source, target) = edge
            weight = 1
        else:
            (source, target, weight) = edge
        weight %= mod
        if inward:
            laplacian[source][source] += weight
            laplacian[source][target] -= weight
        else:
            laplacian[target][target] += weight
            laplacian[target][source] -= weight
    minor = []
    for row in range(vertex_count):
        if row == root:
            continue
        minor.append([laplacian[row][column] % mod for column in range(vertex_count) if column != root])
    return matrix_determinant(minor, mod)
Hafnian = hafnian
Pfaffian = pfaffian
MatrixTree = spanning_tree_count
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, m) = map(int, read().split())
    edges = [tuple(map(int, read().split())) for _ in range(m)]
    print(spanning_tree_count(n, edges))
if __name__ == '__main__':
    main()
