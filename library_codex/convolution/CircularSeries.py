"""循環構造の母関数係数を計算する。"""

from library_codex.convolution.FormalPowerSeries import (
    DEFAULT_MOD,
    fps_exponential,
    fps_inverse,
    fps_logarithm,
    fps_multiply,
    fps_power,
    fps_shrink,
    fps_taylor_shift,
)

from library_codex.math.ModularArithmetic import modular_square_root

def circular_series(real_angle, imaginary_angle=None, degree=None, mod=DEFAULT_MOD):
    """Return real/imaginary parts of exp(-imaginary_angle + i*real_angle)."""
    if imaginary_angle is None:
        imaginary_angle = []
    if degree is None:
        degree = max(len(real_angle), len(imaginary_angle))
    if degree == 0:
        return [], []
    if (real_angle and real_angle[0] % mod) or (
        imaginary_angle and imaginary_angle[0] % mod
    ):
        raise ValueError("both constant coefficients must be zero")
    imaginary_unit = modular_square_root(-1, mod)
    if imaginary_unit is not None:
        first = [0] * degree
        second = [0] * degree
        for index in range(degree):
            real = real_angle[index] if index < len(real_angle) else 0
            imaginary = imaginary_angle[index] if index < len(imaginary_angle) else 0
            first[index] = (-imaginary + imaginary_unit * real) % mod
            second[index] = (-imaginary - imaginary_unit * real) % mod
        first = fps_exponential(first, degree, mod)
        second = fps_exponential(second, degree, mod)
        inverse_two = pow(2, -1, mod)
        inverse_two_i = pow(2 * imaginary_unit % mod, -1, mod)
        real = [(left + right) * inverse_two % mod
                for left, right in zip(first, second)]
        imaginary = [(left - right) * inverse_two_i % mod
                     for left, right in zip(first, second)]
        return real, imaginary
    real = [0] * degree
    imaginary = [0] * degree
    real[0] = 1
    for index in range(1, degree):
        real_value = 0
        imaginary_value = 0
        for offset in range(1, index + 1):
            angle_real = real_angle[offset] if offset < len(real_angle) else 0
            angle_imag = imaginary_angle[offset] if offset < len(imaginary_angle) else 0
            scale = offset
            real_value += scale * (
                -angle_imag * real[index - offset]
                - angle_real * imaginary[index - offset]
            )
            imaginary_value += scale * (
                angle_real * real[index - offset]
                - angle_imag * imaginary[index - offset]
            )
        inverse = pow(index, -1, mod)
        real[index] = real_value % mod * inverse % mod
        imaginary[index] = imaginary_value % mod * inverse % mod
    return real, imaginary

