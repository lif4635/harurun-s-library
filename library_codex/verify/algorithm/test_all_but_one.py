from operator import add, mul

from library_codex.algorithm.AllButOne import all_but_one


def test_all_but_one_products_and_boundaries():
    assert all_but_one([], mul, 1) == []
    assert all_but_one([7], mul, 1) == [1]
    assert all_but_one([2, 3, 5, 7], mul, 1) == [105, 70, 42, 30]


def test_all_but_one_preserves_order_for_noncommutative_operation():
    values = ["a", "b", "c", "d"]
    assert all_but_one(values, add, "") == ["bcd", "acd", "abd", "abc"]
