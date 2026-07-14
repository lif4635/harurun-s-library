import random

from library_codex.convolution.FormalPowerSeries import (
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
)
from library_codex.convolution.OnlineFormalPowerSeries import (
    OnlineFormalPowerSeries,
    RelaxedConvolution,
    RelaxedExponential,
    RelaxedInverse,
    RelaxedLogarithm,
    differential_equation,
    newton_method,
)


MOD = 998244353


def test_relaxed_convolution_and_elementary_series():
    rng = random.Random(101)
    for size in (1, 2, 3, 20, 200, 1000):
        first = [rng.randrange(MOD) for _ in range(size)]
        second = [rng.randrange(MOD) for _ in range(size)]
        relaxed = RelaxedConvolution(size)
        actual = [relaxed.next(first[i], second[i]) for i in range(size)]
        assert actual == fps_multiply(first, second)[:size]
    size = 500
    source = [1] + [rng.randrange(MOD) for _ in range(size - 1)]
    inverse = RelaxedInverse(size)
    assert [inverse.next(value) for value in source] == fps_inverse(source, size)
    logarithm = RelaxedLogarithm(size)
    assert [logarithm.next(value) for value in source] == fps_logarithm(source, size)
    source[0] = 0
    exponential = RelaxedExponential(size)
    assert [exponential.next(value) for value in source] == fps_exponential(source, size)


def test_online_fps_dense_and_self_referential_catalan():
    rng = random.Random(102)
    first_values = [rng.randrange(MOD) for _ in range(300)]
    second_values = [rng.randrange(MOD) for _ in range(300)]
    first = OnlineFormalPowerSeries(first_values)
    second = OnlineFormalPowerSeries(second_values)
    assert (first * second).prefix(300) == fps_multiply(first_values, second_values)[:300]
    invertible = OnlineFormalPowerSeries([1] + first_values[1:])
    assert invertible.inverse().prefix(300) == fps_inverse([1] + first_values[1:], 300)

    catalan = OnlineFormalPowerSeries([1])
    equation = OnlineFormalPowerSeries([1]) + (catalan * catalan).shift_left(1)
    catalan.set(equation)
    expected = [1]
    for n in range(1, 200):
        expected.append(sum(expected[i] * expected[n - 1 - i]
                            for i in range(n)) % MOD)
    assert catalan.prefix(200) == expected


def test_differential_equation_and_newton_method():
    # f'=f, f(0)=1.
    result = differential_equation(
        lambda f, degree: f[:degree],
        lambda _f, degree: [1] + [0] * (degree - 1),
        1,
        300,
    )
    assert result == fps_exponential([0, 1], 300)

    # Solve f^2 = 1+x, starting from f(0)=1.
    target = [1, 1]

    def calculate(f, degree):
        square = fps_multiply(f, f)[:degree]
        value = [0] * max(len(square), len(target))
        for i in range(len(value)):
            value[i] = ((square[i] if i < len(square) else 0)
                        - (target[i] if i < len(target) else 0)) % MOD
        derivative = [2 * coefficient % MOD for coefficient in f]
        return value, derivative

    root = newton_method(calculate, 1, 256)
    square = fps_multiply(root, root)[:256]
    assert square == target + [0] * 254
