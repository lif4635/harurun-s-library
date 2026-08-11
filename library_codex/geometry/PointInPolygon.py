"""多角形に対する点の内外と境界を判定する。"""


def point_location(polygon, point):
    """点が内部なら1、境界上なら0、外部なら-1を返す。"""
    n = len(polygon)
    if n == 0:
        return -1
    x, y = point
    inside = False
    for index, first in enumerate(polygon):
        second = polygon[(index + 1) % n]
        ax, ay = first
        bx, by = second
        cross = (bx - ax) * (y - ay) - (by - ay) * (x - ax)
        if cross == 0 and min(ax, bx) <= x <= max(ax, bx) and min(ay, by) <= y <= max(ay, by):
            return 0
        if (ay > y) != (by > y):
            if (by > ay and cross > 0) or (by < ay and cross < 0):
                inside = not inside
    return 1 if inside else -1
