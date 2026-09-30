from library_codex.convolution.NTT998 import MOD, intt, ntt
from library_codex.fps998.FPS import fps_inv
from library_codex.fps.MultivariateFPS import _inverses


def colored_inverse(series, base, mod, size):
    if mod != MOD or len(base) != 2:
        raise ValueError("two variables modulo 998244353 required")
    width = base[0]
    result = [pow(series[0], -1, mod)]
    while len(result) < size:
        degree = len(result)
        length = 2 * degree
        left = [[0] * length for _ in range(2)]
        right = [[0] * length for _ in range(2)]
        for i, value in enumerate(series[:length]):
            left[i // width & 1][i] = value
        for i, value in enumerate(result):
            right[i // width & 1][i] = value
        for row in left + right:
            ntt(row)
        a, b = left
        c, d = right
        high = [[(a[i] * c[i] + b[i] * d[i]) % mod for i in range(length)],
                [(a[i] * d[i] + b[i] * c[i]) % mod for i in range(length)]]
        for row in high:
            intt(row)
        left = [[0] * length for _ in range(2)]
        for i in range(degree, min(length, size)):
            color = i // width & 1
            left[color][i] = high[color][i]
        for row in left:
            ntt(row)
        a, b = left
        high = [[(a[i] * c[i] + b[i] * d[i]) % mod for i in range(length)],
                [(a[i] * d[i] + b[i] * c[i]) % mod for i in range(length)]]
        for row in high:
            intt(row)
        result.extend(-high[i // width & 1][i] % mod for i in range(degree, min(length, size)))
    return result


def _columns(matrix, inverse=False):
    transform = intt if inverse else ntt
    for column in range(len(matrix[0])):
        values = [row[column] for row in matrix]
        transform(values)
        for row, value in zip(matrix, values):
            row[column] = value


def row_inverse(series, base, mod, size):
    if mod != MOD or len(base) != 2:
        raise ValueError("two variables modulo 998244353 required")
    width = min(base[0], size)
    height = (size + width - 1) // width
    length = 1 << (2 * width - 1).bit_length()
    source = [series[i * width:(i + 1) * width] for i in range(height)]
    for row in source:
        row.extend([0] * (length - len(row)))
    result = [[0] * length for _ in range(height)]
    result[0][:width] = fps_inv(source[0][:width], width)
    for row in source:
        ntt(row)
    ntt(result[0])
    degree = 1
    while degree < height:
        count = 2 * degree
        left = [source[i][:] if i < height else [0] * length for i in range(count)]
        right = [result[i][:] if i < degree else [0] * length for i in range(count)]
        _columns(left)
        _columns(right)
        for a, b in zip(left, right):
            for j in range(length):
                a[j] = a[j] * b[j] % mod
        _columns(left, True)
        for i in range(count):
            if i < degree:
                left[i] = [0] * length
            else:
                intt(left[i])
                left[i][width:] = [0] * (length - width)
                ntt(left[i])
        _columns(left)
        for a, b in zip(left, right):
            for j in range(length):
                a[j] = a[j] * b[j] % mod
        _columns(left, True)
        for i in range(degree, min(count, height)):
            intt(left[i])
            left[i][width:] = [0] * (length - width)
            ntt(left[i])
            result[i] = [-value % mod for value in left[i]]
        degree *= 2
    for row in result:
        intt(row)
    return [value for row in result for value in row[:width]][:size]


def sparse_unlimited(series, base, mod, exponent=None, logarithm=False):
    width = base[0]
    scale = pow(series[0], -1, mod) if exponent is not None else 1
    terms = [(i, i % width, value * scale % mod) for i, value in enumerate(series) if i and value]
    inverses = _inverses(len(series), mod)
    result = [0] * len(series)
    result[0] = 0 if logarithm else 1 if exponent is None else pow(series[0], exponent, mod)
    if logarithm:
        for i in range(1, len(series)):
            x = i % width
            total = i * series[i] % mod
            for offset, column, coefficient in terms:
                if offset >= i:
                    break
                if column <= x:
                    total -= coefficient * result[i - offset]
            result[i] = total % mod
        for i in range(1, len(series)):
            result[i] = result[i] * inverses[i] % mod
    elif exponent is None:
        terms = [(offset, x, offset * coefficient % mod) for offset, x, coefficient in terms]
        for i in range(1, len(series)):
            x = i % width
            total = 0
            for offset, column, coefficient in terms:
                if offset > i:
                    break
                if column <= x:
                    total += coefficient * result[i - offset]
            result[i] = total % mod * inverses[i] % mod
    else:
        factor = (exponent + 1) % mod
        terms = [(offset, x, coefficient, factor * offset * coefficient % mod) for offset, x, coefficient in terms]
        for i in range(1, len(series)):
            x = i % width
            total = 0
            for offset, column, coefficient, weighted in terms:
                if offset > i:
                    break
                if column <= x:
                    total += (weighted - i * coefficient) % mod * result[i - offset]
            result[i] = total % mod * inverses[i] % mod
    return result
