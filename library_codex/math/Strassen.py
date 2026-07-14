from library_codex.convolution.FormalPowerSeries import DEFAULT_MOD


def _naive(first, second, mod):
    size = len(first)
    result = [[0] * size for _ in range(size)]
    for row in range(size):
        output = result[row]
        for pivot, value in enumerate(first[row]):
            if value:
                source = second[pivot]
                for column in range(size):
                    output[column] += value * source[column]
        if mod is not None:
            for column in range(size):
                output[column] %= mod
    return result


def _combine(first, second, sign=1, mod=None):
    size = len(first)
    result = [[0] * size for _ in range(size)]
    if mod is None:
        for row in range(size):
            result[row] = [left + sign * right
                           for left, right in zip(first[row], second[row])]
    else:
        for row in range(size):
            result[row] = [(left + sign * right) % mod
                           for left, right in zip(first[row], second[row])]
    return result


def _quadrants(matrix):
    half = len(matrix) >> 1
    return (
        [row[:half] for row in matrix[:half]],
        [row[half:] for row in matrix[:half]],
        [row[:half] for row in matrix[half:]],
        [row[half:] for row in matrix[half:]],
    )


def strassen_matrix_multiply(first, second, mod=DEFAULT_MOD, threshold=32):
    """Rectangular matrix product using an explicit-stack Strassen engine."""
    rows = len(first)
    inner = len(first[0]) if rows else 0
    if any(len(row) != inner for row in first):
        raise ValueError("first matrix is ragged")
    if len(second) != inner:
        raise ValueError("incompatible matrix shapes")
    columns = len(second[0]) if second else 0
    if any(len(row) != columns for row in second):
        raise ValueError("second matrix is ragged")
    if rows == 0 or columns == 0:
        return [[] for _ in range(rows)]
    size = 1
    while size < max(rows, inner, columns):
        size <<= 1
    left = [[0] * size for _ in range(size)]
    right = [[0] * size for _ in range(size)]
    for row in range(rows):
        for column in range(inner):
            left[row][column] = (first[row][column] if mod is None
                                 else first[row][column] % mod)
    for row in range(inner):
        for column in range(columns):
            right[row][column] = (second[row][column] if mod is None
                                  else second[row][column] % mod)

    tasks = [(0, left, right)]
    results = []
    while tasks:
        kind, *payload = tasks.pop()
        if kind == 1:
            products = results[-7:]
            del results[-7:]
            p1, p2, p3, p4, p5, p6, p7 = products
            c11 = _combine(_combine(_combine(p1, p4, 1, mod), p5, -1, mod),
                           p7, 1, mod)
            c12 = _combine(p3, p5, 1, mod)
            c21 = _combine(p2, p4, 1, mod)
            c22 = _combine(_combine(_combine(p1, p2, -1, mod), p3, 1, mod),
                           p6, 1, mod)
            half = len(c11)
            combined = [c11[row] + c12[row] for row in range(half)]
            combined += [c21[row] + c22[row] for row in range(half)]
            results.append(combined)
            continue
        left_matrix, right_matrix = payload
        n = len(left_matrix)
        if n <= threshold:
            results.append(_naive(left_matrix, right_matrix, mod))
            continue
        a, b, c, d = _quadrants(left_matrix)
        e, f, g, h = _quadrants(right_matrix)
        calls = [
            (_combine(a, d, 1, mod), _combine(e, h, 1, mod)),
            (_combine(c, d, 1, mod), e),
            (a, _combine(f, h, -1, mod)),
            (d, _combine(g, e, -1, mod)),
            (_combine(a, b, 1, mod), h),
            (_combine(c, a, -1, mod), _combine(e, f, 1, mod)),
            (_combine(b, d, -1, mod), _combine(g, h, 1, mod)),
        ]
        tasks.append((1,))
        for left_call, right_call in reversed(calls):
            tasks.append((0, left_call, right_call))
    product = results[0]
    return [row[:columns] for row in product[:rows]]


strassen = strassen_matrix_multiply
fast_mat_prod = strassen_matrix_multiply
