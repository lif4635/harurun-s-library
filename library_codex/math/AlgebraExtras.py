import math
from fractions import Fraction

from library_codex.prime.Factorization import divisors, factor_count


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


class FloatBinomial:
    __slots__ = ("log_factorial",)
    LOG_ZERO = -1e100

    def __init__(self, maximum):
        self.log_factorial = [0.0] * (maximum + 1)
        for index in range(1, maximum + 1):
            self.log_factorial[index] = self.log_factorial[index - 1] + math.log(index)

    def logfac(self, number):
        return self.log_factorial[number]

    def logfinv(self, number):
        return -self.log_factorial[number]

    def logC(self, number, chosen):
        if chosen < 0 or number < chosen:
            return self.LOG_ZERO
        return (self.log_factorial[number] - self.log_factorial[chosen]
                - self.log_factorial[number - chosen])

    def logP(self, number, chosen):
        if chosen < 0 or number < chosen:
            return self.LOG_ZERO
        return self.log_factorial[number] - self.log_factorial[number - chosen]


class RationalBinomial:
    def fac(self, number):
        return Fraction(math.factorial(number)) if number >= 0 else Fraction(0)

    def finv(self, number):
        return 1 / self.fac(number) if number >= 0 else Fraction(0)

    def inv(self, number):
        return Fraction(1, number) if number else Fraction(1)

    def C(self, number, chosen):
        return Fraction(math.comb(number, chosen)) if 0 <= chosen <= number else Fraction(0)

    def P(self, number, chosen):
        return Fraction(math.perm(number, chosen)) if 0 <= chosen <= number else Fraction(0)

    def H(self, number, chosen):
        if number < 0 or chosen < 0:
            return Fraction(0)
        return Fraction(1) if chosen == 0 else self.C(number + chosen - 1, chosen)

    def multinomial(self, groups):
        if any(group < 0 for group in groups):
            return Fraction(0)
        total = sum(groups)
        result = math.factorial(total)
        for group in groups:
            result //= math.factorial(group)
        return Fraction(result)

    __call__ = C


def _fib_pair(index, modulus):
    first, second = 0, 1
    for bit in bin(index)[2:]:
        doubled = first * ((second << 1) - first) % modulus
        next_value = (first * first + second * second) % modulus
        if bit == "0":
            first, second = doubled, next_value
        else:
            first, second = next_value, (doubled + next_value) % modulus
    return first, second


def pisano_prime(prime):
    if prime == 2:
        return 3
    if prime == 5:
        return 20
    candidate = prime - 1 if prime % 5 in (1, 4) else 2 * (prime + 1)
    for period in divisors(candidate):
        if _fib_pair(period, prime) == (0, 1):
            return period
    raise ArithmeticError("Pisano period was not found")


def pisano_period(modulus):
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    if modulus == 1:
        return 1
    result = 1
    for prime, exponent in factor_count(modulus).items():
        period = pisano_prime(prime) * prime ** (exponent - 1)
        result = math.lcm(result, period)
    return result


def power_table(limit, exponent, mod=None):
    if limit < 0 or exponent < 0:
        raise ValueError("limit and exponent must be nonnegative")
    if mod is None:
        return [value ** exponent for value in range(limit + 1)]
    return [pow(value, exponent, mod) for value in range(limit + 1)]


def digamma(value):
    result = 0.0
    while value < 50.0:
        result -= 1.0 / value
        value += 1.0
    inverse = 1.0 / value
    square = inverse * inverse
    fourth = square * square
    return (result + math.log(value) - 0.5 * inverse - square / 12.0
            + fourth / 120.0 - fourth * square / 252.0)


def inverse_sum(left, right):
    return digamma(right) - digamma(left)


class QBinomial:
    __slots__ = ("q", "mod", "order", "factorial", "inverse_factorial")

    def __init__(self, q, maximum, mod=998244353):
        self.q = q % mod
        self.mod = mod
        quantum = 1
        factorial = [1]
        order = None
        for index in range(1, maximum + 2):
            factorial.append(factorial[-1] * quantum % mod)
            quantum = (quantum * self.q + 1) % mod
            if quantum == 0:
                order = index + 1
                break
        if order is None:
            order = maximum + 2
        self.order = order
        factorial = factorial[:order]
        inverse_factorial = [1] * len(factorial)
        inverse_factorial[-1] = pow(factorial[-1], -1, mod)
        for index in range(len(factorial) - 1, 0, -1):
            quantum_index = sum(pow(self.q, power, mod) for power in range(index)) % mod
            inverse_factorial[index - 1] = inverse_factorial[index] * quantum_index % mod
        self.factorial = factorial
        self.inverse_factorial = inverse_factorial

    def binomial(self, number, chosen):
        if chosen < 0 or chosen > number:
            return 0
        order = self.order
        high_n, low_n = divmod(number, order)
        high_k, low_k = divmod(chosen, order)
        if low_k > low_n:
            return 0
        low = (self.factorial[low_n] * self.inverse_factorial[low_k]
               % self.mod * self.inverse_factorial[low_n - low_k] % self.mod)
        return math.comb(high_n, high_k) % self.mod * low % self.mod


Binomial_rational = RationalBinomial
Pisano = pisano_prime
PisanoComposite = pisano_period
powertable = power_table
inv_sum = inverse_sum
QBinom = QBinomial
