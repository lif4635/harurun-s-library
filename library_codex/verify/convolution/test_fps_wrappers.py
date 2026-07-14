from library_codex.convolution.FPSWrappers import DualFPS, FPSFraction


def test_fps_fraction_and_dual_fps_arithmetic():
    first = FPSFraction([1], [1, -1])
    second = FPSFraction([1], [1, 1])
    total = (first + second).shrink()
    assert total.numerator == [2]
    assert total.denominator == [1, 0, -1 % first.mod]
    recovered = ((first * second) / second).shrink()
    from library_codex.convolution.FormalPowerSeries import fps_multiply
    assert fps_multiply(recovered.numerator, first.denominator) == fps_multiply(
        first.numerator, recovered.denominator
    )

    left = DualFPS([1, 2, 3])
    right = DualFPS([4, 5])
    assert (left + right).get() == [5, 7, 3]
    assert (left * right).get() == [4, 13, 22, 15]
    assert (left << 3).get() == [0, 0, 0, 1, 2, 3]
