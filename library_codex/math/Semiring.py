"""任意の加法・乗法を指定した半環上で行列演算と線形漸化式を計算する。"""

class Semiring:
    __slots__ = ("value", "add_function", "multiply_function", "zero", "one")

    def __init__(self, value, add, multiply, zero, one):
        self.value = value
        self.add_function = add
        self.multiply_function = multiply
        self.zero = zero
        self.one = one

    def __add__(self, other):
        return Semiring(self.add_function(self.value, other.value),
                        self.add_function, self.multiply_function,
                        self.zero, self.one)

    def __mul__(self, other):
        return Semiring(self.multiply_function(self.value, other.value),
                        self.add_function, self.multiply_function,
                        self.zero, self.one)

    def __eq__(self, other):
        return isinstance(other, Semiring) and self.value == other.value

def semiring_matrix_multiply(first, second, add, multiply, zero):
    height = len(first)
    common = len(second)
    width = len(second[0]) if second else 0
    result = [[zero for _ in range(width)] for _ in range(height)]
    for row in range(height):
        for middle in range(common):
            left = first[row][middle]
            for column in range(width):
                result[row][column] = add(
                    result[row][column], multiply(left, second[middle][column])
                )
    return result

def semiring_matrix_power(matrix, exponent, add, multiply, zero, one):
    if exponent < 0 or any(len(row) != len(matrix) for row in matrix):
        raise ValueError("a square matrix and nonnegative exponent are required")
    size = len(matrix)
    result = [[one if row == column else zero for column in range(size)]
              for row in range(size)]
    base = [row[:] for row in matrix]
    while exponent:
        if exponent & 1:
            result = semiring_matrix_multiply(result, base, add, multiply, zero)
        exponent >>= 1
        if exponent:
            base = semiring_matrix_multiply(base, base, add, multiply, zero)
    return result

def semiring_linear_recurrence(initial, coefficients, index,
                               add, multiply, zero, one):
    """Kitamasa over an arbitrary semiring; a[n]=sum(c[i]*a[n-k+i])."""
    size = len(coefficients)
    if len(initial) != size or index < 0:
        raise ValueError("invalid recurrence")
    if index < size:
        return initial[index]

    def combine(first, second):
        product = [zero] * (size * 2 - 1)
        for i, left in enumerate(first):
            for j, right in enumerate(second):
                product[i + j] = add(product[i + j], multiply(left, right))
        for degree in range(len(product) - 1, size - 1, -1):
            value = product[degree]
            for offset, coefficient in enumerate(coefficients):
                target = degree - size + offset
                product[target] = add(product[target], multiply(value, coefficient))
        return product[:size]

    result = [zero] * size
    result[0] = one
    base = [zero] * size
    if size == 1:
        base[0] = coefficients[0]
    else:
        base[1] = one
    while index:
        if index & 1:
            result = combine(result, base)
        index >>= 1
        if index:
            base = combine(base, base)
    answer = zero
    for value, coefficient in zip(initial, result):
        answer = add(answer, multiply(value, coefficient))
    return answer

