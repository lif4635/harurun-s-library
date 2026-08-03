"""単峰関数の最小値または最大値を黄金分割探索する。"""

def golden_section_search(function, left, right, minimize=True):
    if left > right:
        raise ValueError("left must not exceed right")
    before = left - 1
    smaller = 1
    larger = 2
    while larger < right - left + 2:
        smaller, larger = larger, smaller + larger
    point = before + larger - smaller
    boundary = before + larger
    point_value = function(point)
    while before + boundary != point * 2:
        other = before + boundary - point
        if other > right:
            move_boundary = True
        else:
            other_value = function(other)
            move_boundary = (
                point_value < other_value
                if minimize
                else point_value > other_value
            )
        if move_boundary:
            boundary = before
            before = other
        else:
            before = point
            point = other
            point_value = other_value
    return point, point_value

