"""一次式の行列と分母による漸化式を平方分割でまとめて進める。"""

from math import isqrt
from library_codex.fps.FormalPowerSeries import fps_multiply
from library_codex.polynomial.MultipointEvaluation import ProductTree


def _matrix_product(a, b, dimension, mod):
    result = [[] for _ in range(dimension * dimension)]
    for i in range(dimension):
        for k in range(dimension):
            first = a[i * dimension + k]
            if not first:
                continue
            for j in range(dimension):
                second = b[k * dimension + j]
                if not second:
                    continue
                product = fps_multiply(first, second, mod)
                target = result[i * dimension + j]
                if len(target) < len(product):
                    target.extend([0] * (len(product) - len(target)))
                for p, value in enumerate(product):
                    target[p] = (target[p] + value) % mod
    return result


def linear_matrix_recurrence(initial, constant, linear, denominator, steps, mod=998244353):
    """v(t+1)=(constant+t*linear)v(t)/(denominator[0]+t*denominator[1])をsteps回進める。"""
    if mod < 2 or steps < 0:
        raise ValueError("require mod >= 2 and steps >= 0")
    state = [value % mod for value in initial]
    dimension = len(state)
    if mod < 2 or steps < 0 or dimension == 0:
        raise ValueError("require mod >= 2, steps >= 0 and a nonempty state")
    if len(constant) != dimension or len(linear) != dimension or any(len(row) != dimension for row in constant) or any(len(row) != dimension for row in linear):
        raise ValueError("matrices must be square and match the state")
    a = [value % mod for row in constant for value in row]
    b = [value % mod for row in linear for value in row]
    c, d = denominator
    c, d = c % mod, d % mod
    block = isqrt(steps)
    blocks = 0
    if steps > 64:
        matrices, divisors = [], []
        for t in range(block):
            matrices.append([[((x + t * y) % mod), y] if y else ([x] if x else []) for x, y in zip(a, b)])
            divisors.append([(c + t * d) % mod, d] if d else [c])
        while len(matrices) > 1:
            next_matrices, next_divisors = [], []
            for i in range(0, len(matrices) - 1, 2):
                next_matrices.append(_matrix_product(matrices[i + 1], matrices[i], dimension, mod))
                next_divisors.append(fps_multiply(divisors[i], divisors[i + 1], mod))
            if len(matrices) & 1:
                next_matrices.append(matrices[-1])
                next_divisors.append(divisors[-1])
            matrices, divisors = next_matrices, next_divisors
        blocks = steps // block
        tree = ProductTree(range(0, blocks * block, block), mod)
        entries = [tree.evaluate(poly) for poly in matrices[0]]
        den = tree.evaluate(divisors[0])
        prefix = [1]
        for value in den:
            prefix.append(prefix[-1] * value % mod)
        inverse = pow(prefix[-1], -1, mod)
        for i in range(blocks - 1, -1, -1):
            den[i], inverse = inverse * prefix[i] % mod, inverse * den[i] % mod
        for t in range(blocks):
            state = [sum(entries[i * dimension + j][t] * state[j] for j in range(dimension)) % mod * den[t] % mod for i in range(dimension)]
    for t in range(blocks * block, steps):
        inverse = pow((c + t * d) % mod, -1, mod)
        state = [sum((a[i * dimension + j] + t * b[i * dimension + j]) * state[j] for j in range(dimension)) % mod * inverse % mod for i in range(dimension)]
    return state
