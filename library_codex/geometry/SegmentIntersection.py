"""2次元の線分が交差するかを整数演算で判定する。"""

from library_codex.geometry.Orientation import orientation


def _on_segment(first, second, point):
    return (
        min(first[0], second[0]) <= point[0] <= max(first[0], second[0])
        and min(first[1], second[1]) <= point[1] <= max(first[1], second[1])
    )


def segments_intersect(first, second, third, fourth, touch=True):
    """線分[first, second]と[third, fourth]が交差するかを返す。O(1)。"""
    first_side = orientation(first, second, third)
    second_side = orientation(first, second, fourth)
    third_side = orientation(third, fourth, first)
    fourth_side = orientation(third, fourth, second)

    if not touch:
        return first_side * second_side < 0 and third_side * fourth_side < 0
    if first_side == 0 and _on_segment(first, second, third):
        return True
    if second_side == 0 and _on_segment(first, second, fourth):
        return True
    if third_side == 0 and _on_segment(third, fourth, first):
        return True
    if fourth_side == 0 and _on_segment(third, fourth, second):
        return True
    return first_side * second_side < 0 and third_side * fourth_side < 0
