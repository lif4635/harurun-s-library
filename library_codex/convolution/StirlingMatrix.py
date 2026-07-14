from library_codex.convolution.AdvancedSeries import (
    composite_exponential_scaled,
    inverse_composite_exponential,
)
from library_codex.convolution.MultipointEvaluation import ProductTree
from library_codex.convolution.SeriesSequences import pascal_transform
from library_codex.convolution.FormalPowerSeries import DEFAULT_MOD


def _factorials(size, mod):
    factorial = [1] * size
    for index in range(1, size):
        factorial[index] = factorial[index - 1] * index % mod
    inverse = [1] * size
    if size:
        inverse[-1] = pow(factorial[-1], -1, mod)
        for index in range(size - 1, 0, -1):
            inverse[index - 1] = inverse[index] * index % mod
    return factorial, inverse


def stirling_matrix(values, inverse=False, mod=DEFAULT_MOD):
    size = len(values)
    if size == 0:
        return []
    factorial, inverse_factorial = _factorials(size, mod)
    scaled = [values[index] * inverse_factorial[index] % mod
              for index in range(size)]
    if not inverse:
        transformed = pascal_transform(
            scaled, inverse=True, transpose=True, mod=mod
        )
        result = composite_exponential_scaled(transformed, 1, size, mod)
    else:
        transformed = inverse_composite_exponential(scaled, 1, mod)
        result = pascal_transform(
            transformed, inverse=False, transpose=True, mod=mod
        )
    return [result[index] * factorial[index] % mod for index in range(size)]


def stirling_matrix_transpose(values, inverse=False, mod=DEFAULT_MOD):
    size = len(values)
    if size == 0:
        return []
    factorial, inverse_factorial = _factorials(size, mod)
    tree = ProductTree(range(size), mod)
    if not inverse:
        evaluated = tree.evaluate(values)
        transformed = pascal_transform(evaluated, inverse=True, mod=mod)
        return [transformed[index] * inverse_factorial[index] % mod
                for index in range(size)]
    scaled = [values[index] * factorial[index] % mod
              for index in range(size)]
    transformed = pascal_transform(scaled, inverse=False, mod=mod)
    return tree.interpolate(transformed)


stirling_matrix_trans = stirling_matrix_transpose
