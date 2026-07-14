from library_codex.math.Matrix import matrix_determinant


DEFAULT_MOD = 998244353


def determinant_arbitrary_mod(matrix, mod):
    if mod <= 0:
        raise ValueError("mod must be positive")
    size = len(matrix)
    for row in matrix:
        if len(row) != size:
            raise ValueError("matrix must be square")
    values = [[value % mod for value in row] for row in matrix]
    sign = 1
    for column in range(size):
        pivot = column
        while pivot < size and values[pivot][column] == 0:
            pivot += 1
        if pivot == size:
            return 0
        if pivot != column:
            values[column], values[pivot] = values[pivot], values[column]
            sign = -sign
        for row in range(column + 1, size):
            while values[row][column]:
                quotient = values[column][column] // values[row][column]
                source = values[row]
                target = values[column]
                for index in range(column, size):
                    target[index] = (
                        target[index] - quotient * source[index]
                    ) % mod
                values[column], values[row] = values[row], values[column]
                sign = -sign
    result = sign
    for index in range(size):
        result = result * values[index][index] % mod
    return result % mod


def _add_product_shift(target, first, second, limit, mod):
    for left in range(limit - 1):
        value = first[left]
        if value == 0:
            continue
        upper = limit - 1 - left
        for right in range(upper):
            target[left + right + 1] += value * second[right]
    for index in range(limit):
        target[index] %= mod


def hafnian(matrix, mod=DEFAULT_MOD):
    size = len(matrix)
    if size & 1:
        raise ValueError("hafnian requires even dimension")
    for row in matrix:
        if len(row) != size:
            raise ValueError("matrix must be square")
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
        current, phase, reduced, zero = frame
        if not current:
            returned = [1] + [0] * (limit - 1)
            stack.pop()
            continue
        last = len(current) - 2
        if phase == 0:
            reduced = [
                [polynomial[:] for polynomial in row]
                for row in current[:last]
            ]
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
                    _add_product_shift(
                        reduced[row][column],
                        current[last][row],
                        current[last + 1][column],
                        limit,
                        mod,
                    )
                    _add_product_shift(
                        reduced[row][column],
                        current[last + 1][row],
                        current[last][column],
                        limit,
                        mod,
                    )
            stack.append([reduced, 0, None, None])
            continue
        one = returned
        result = [(one[index] - zero[index]) % mod for index in range(limit)]
        _add_product_shift(
            result,
            one,
            current[last + 1][last],
            limit,
            mod,
        )
        returned = result
        stack.pop()
    return returned[-1]


def pfaffian(matrix, mod=DEFAULT_MOD):
    size = len(matrix)
    if size & 1:
        raise ValueError("pfaffian requires even dimension")
    for row in matrix:
        if len(row) != size:
            raise ValueError("matrix must be square")
    values = [[value % mod for value in row] for row in matrix]
    result = 1
    for left in range(0, size, 2):
        pivot = left + 1
        while pivot < size and values[left][pivot] == 0:
            pivot += 1
        if pivot == size:
            return 0
        if pivot != left + 1:
            values[left + 1], values[pivot] = values[pivot], values[left + 1]
            for row in values:
                row[left + 1], row[pivot] = row[pivot], row[left + 1]
            result = -result
        paired = left + 1
        pivot_value = values[left][paired]
        result = result * pivot_value % mod
        inverse = pow(pivot_value, -1, mod)
        for row in range(paired + 1, size):
            for column in range(row + 1, size):
                correction = (
                    values[left][row] * values[paired][column]
                    - values[left][column] * values[paired][row]
                ) % mod
                value = (values[row][column] - correction * inverse) % mod
                values[row][column] = value
                values[column][row] = -value % mod
    return result % mod


def spanning_tree_count(vertex_count, edges, mod=DEFAULT_MOD):
    if vertex_count < 0:
        raise ValueError("vertex_count must be nonnegative")
    if vertex_count <= 1:
        return 1
    size = vertex_count - 1
    laplacian = [[0] * size for _ in range(size)]
    for edge in edges:
        if len(edge) == 2:
            first, second = edge
            weight = 1
        else:
            first, second, weight = edge
        weight %= mod
        if first < size:
            laplacian[first][first] = (
                laplacian[first][first] + weight
            ) % mod
        if second < size:
            laplacian[second][second] = (
                laplacian[second][second] + weight
            ) % mod
        if first < size and second < size:
            laplacian[first][second] = (
                laplacian[first][second] - weight
            ) % mod
            laplacian[second][first] = (
                laplacian[second][first] - weight
            ) % mod
    return matrix_determinant(laplacian, mod)


def directed_spanning_tree_count(
    vertex_count, edges, root, inward=True, mod=DEFAULT_MOD
):
    if not 0 <= root < vertex_count:
        raise ValueError("invalid root")
    if vertex_count == 1:
        return 1
    laplacian = [[0] * vertex_count for _ in range(vertex_count)]
    for edge in edges:
        if len(edge) == 2:
            source, target = edge
            weight = 1
        else:
            source, target, weight = edge
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
        minor.append([
            laplacian[row][column] % mod
            for column in range(vertex_count)
            if column != root
        ])
    return matrix_determinant(minor, mod)


Hafnian = hafnian
Pfaffian = pfaffian
MatrixTree = spanning_tree_count
