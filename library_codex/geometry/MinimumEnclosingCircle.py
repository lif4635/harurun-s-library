"""点集合を覆う半径最小の円を求める。"""

from math import sqrt
from random import Random


def _diameter(first, second, first_id, second_id):
    x = (first[0] + second[0]) * 0.5
    y = (first[1] + second[1]) * 0.5
    dx = first[0] - second[0]
    dy = first[1] - second[1]
    return x, y, (dx * dx + dy * dy) * 0.25, (first_id, second_id)


def _through_three(first, second, third, ids):
    ax, ay = first
    bx, by = second
    cx, cy = third
    denominator = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    scale = max(1.0, abs(ax), abs(ay), abs(bx), abs(by), abs(cx), abs(cy))
    if abs(denominator) <= 1e-15 * scale * scale:
        pairs = ((first, second, ids[0], ids[1]),
                 (first, third, ids[0], ids[2]),
                 (second, third, ids[1], ids[2]))
        return max(((_diameter(*pair)) for pair in pairs), key=lambda circle: circle[2])
    aa = ax * ax + ay * ay
    bb = bx * bx + by * by
    cc = cx * cx + cy * cy
    x = (aa * (by - cy) + bb * (cy - ay) + cc * (ay - by)) / denominator
    y = (aa * (cx - bx) + bb * (ax - cx) + cc * (bx - ax)) / denominator
    dx = x - ax
    dy = y - ay
    return x, y, dx * dx + dy * dy, ids


def _contains(circle, point):
    x, y, radius_squared, _ = circle
    dx = point[0] - x
    dy = point[1] - y
    return dx * dx + dy * dy <= radius_squared + 1e-12 * max(1.0, radius_squared)


def minimum_enclosing_circle(points, seed=0):
    """すべての点を含む最小円を(center, radius, support)で返す。"""
    points = [tuple(point) for point in points]
    if not points:
        raise ValueError("at least one point is required")
    order = list(range(len(points)))
    Random(seed).shuffle(order)
    circle = None
    for position, first_id in enumerate(order):
        first = points[first_id]
        if circle is not None and _contains(circle, first):
            continue
        circle = (float(first[0]), float(first[1]), 0.0, (first_id,))
        for second_position in range(position):
            second_id = order[second_position]
            second = points[second_id]
            if _contains(circle, second):
                continue
            circle = _diameter(first, second, first_id, second_id)
            for third_position in range(second_position):
                third_id = order[third_position]
                third = points[third_id]
                if not _contains(circle, third):
                    circle = _through_three(
                        first, second, third, (first_id, second_id, third_id)
                    )
    x, y, radius_squared, support = circle
    return (x, y), sqrt(max(0.0, radius_squared)), tuple(sorted(support))
