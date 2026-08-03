"""2次元ベクトルを偏角順に浮動小数点数を使わず並べる。"""

from functools import cmp_to_key


def _half(point):
    x, y = point
    return 0 if y > 0 or y == 0 and x >= 0 else 1


def _compare(first, second):
    first_zero = first[0] == 0 and first[1] == 0
    second_zero = second[0] == 0 and second[1] == 0
    if first_zero or second_zero:
        return second_zero - first_zero
    first_half = _half(first)
    second_half = _half(second)
    if first_half != second_half:
        return first_half - second_half
    product = first[0] * second[1] - first[1] * second[0]
    if product:
        return -1 if product > 0 else 1
    first_norm = first[0] * first[0] + first[1] * first[1]
    second_norm = second[0] * second[0] + second[1] * second[1]
    return (first_norm > second_norm) - (first_norm < second_norm)


def argument_sort(points):
    """ベクトルを正のx軸から反時計回りの偏角順に返す。O(N log N)。"""
    return sorted(points, key=cmp_to_key(_compare))
