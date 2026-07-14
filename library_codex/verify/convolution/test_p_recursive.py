from library_codex.convolution.PRecursive import (
    enumerate_p_recursive,
    find_p_recursive,
    kth_term_p_recursive,
)
from library_codex.convolution.FormalPowerSeries import DEFAULT_MOD


def test_find_and_enumerate_p_recursive_factorials():
    values = [1]
    for index in range(1, 80):
        values.append(values[-1] * index % DEFAULT_MOD)
    recurrence = find_p_recursive(values[:30], 1)
    assert enumerate_p_recursive(values[:2], recurrence, 80) == values
    index = 10 ** 6
    expected = 1
    for value in range(2, index + 1):
        expected = expected * value % DEFAULT_MOD
    assert kth_term_p_recursive(values[:2], recurrence, index) == expected


def test_constant_coefficient_recurrence():
    values = [0, 1]
    for _ in range(2, 100):
        values.append((values[-1] + values[-2]) % DEFAULT_MOD)
    recurrence = find_p_recursive(values[:30], 0)
    assert enumerate_p_recursive(values[:2], recurrence, 100) == values
    assert kth_term_p_recursive(values[:2], recurrence, 99) == values[99]
