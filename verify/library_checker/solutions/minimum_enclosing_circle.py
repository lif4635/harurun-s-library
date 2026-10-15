"""点集合を覆う半径最小の円を求める。"""
from math import sqrt
from random import Random

def _geometry_minimum_enclosing_circle_diameter(first, second, first_id, second_id):
    x = (first[0] + second[0]) * 0.5
    y = (first[1] + second[1]) * 0.5
    dx = first[0] - second[0]
    dy = first[1] - second[1]
    return (x, y, (dx * dx + dy * dy) * 0.25, (first_id, second_id))

def _geometry_minimum_enclosing_circle_through_three(first, second, third, ids):
    (ax, ay) = first
    (bx, by) = second
    (cx, cy) = third
    denominator = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    scale = max(1.0, abs(ax), abs(ay), abs(bx), abs(by), abs(cx), abs(cy))
    if abs(denominator) <= 1e-15 * scale * scale:
        pairs = ((first, second, ids[0], ids[1]), (first, third, ids[0], ids[2]), (second, third, ids[1], ids[2]))
        return max((_geometry_minimum_enclosing_circle_diameter(*pair) for pair in pairs), key=lambda circle: circle[2])
    aa = ax * ax + ay * ay
    bb = bx * bx + by * by
    cc = cx * cx + cy * cy
    x = (aa * (by - cy) + bb * (cy - ay) + cc * (ay - by)) / denominator
    y = (aa * (cx - bx) + bb * (ax - cx) + cc * (bx - ax)) / denominator
    dx = x - ax
    dy = y - ay
    return (x, y, dx * dx + dy * dy, ids)

def _geometry_minimum_enclosing_circle_contains(circle, point):
    (x, y, radius_squared, _) = circle
    dx = point[0] - x
    dy = point[1] - y
    return dx * dx + dy * dy <= radius_squared + 1e-12 * max(1.0, radius_squared)

def minimum_enclosing_circle(points, seed=0):
    """すべての点を含む最小円を(center, radius, support)で返す。"""
    points = [tuple(point) for point in points]
    if not points:
        raise ValueError('at least one point is required')
    order = list(range(len(points)))
    Random(seed).shuffle(order)
    circle = None
    for (position, first_id) in enumerate(order):
        first = points[first_id]
        if circle is not None and _geometry_minimum_enclosing_circle_contains(circle, first):
            continue
        circle = (float(first[0]), float(first[1]), 0.0, (first_id,))
        for second_position in range(position):
            second_id = order[second_position]
            second = points[second_id]
            if _geometry_minimum_enclosing_circle_contains(circle, second):
                continue
            circle = _geometry_minimum_enclosing_circle_diameter(first, second, first_id, second_id)
            for third_position in range(second_position):
                third_id = order[third_position]
                third = points[third_id]
                if not _geometry_minimum_enclosing_circle_contains(circle, third):
                    circle = _geometry_minimum_enclosing_circle_through_three(first, second, third, (first_id, second_id, third_id))
    (x, y, radius_squared, support) = circle
    return ((x, y), sqrt(max(0.0, radius_squared)), tuple(sorted(support)))

def _geometry_minimum_enclosing_circle_integer_diameter(first, second):
    x = first[0] + second[0]
    y = first[1] + second[1]
    dx = first[0] - second[0]
    dy = first[1] - second[1]
    return (x, y, 2, dx * dx + dy * dy)

def _geometry_minimum_enclosing_circle_integer_three(first, second, third):
    (bx, by) = (second[0] - first[0], second[1] - first[1])
    (cx, cy) = (third[0] - first[0], third[1] - first[1])
    denominator = 2 * (bx * cy - by * cx)
    if denominator == 0:
        return max((_geometry_minimum_enclosing_circle_integer_diameter(first, second), _geometry_minimum_enclosing_circle_integer_diameter(first, third), _geometry_minimum_enclosing_circle_integer_diameter(second, third)), key=lambda circle: circle[3])
    bb = bx * bx + by * by
    cc = cx * cx + cy * cy
    x = bb * cy - cc * by
    y = bx * cc - cx * bb
    return (x + first[0] * denominator, y + first[1] * denominator, denominator, x * x + y * y)

def _geometry_minimum_enclosing_circle_integer_contains(circle, point):
    (x, y, denominator, squared) = circle
    dx = point[0] * denominator - x
    dy = point[1] * denominator - y
    return dx * dx + dy * dy <= squared

def minimum_enclosing_circle_boundary(points, seed=0):
    """整数座標の最小包含円について、各点が円周上なら1、内部なら0を返す。"""
    points = [tuple(point) for point in points]
    if not points:
        raise ValueError('at least one point is required')
    if any((not isinstance(value, int) for point in points for value in point)):
        raise TypeError('integer coordinates required')
    order = list(range(len(points)))
    Random(seed).shuffle(order)
    circle = None
    for (position, first_id) in enumerate(order):
        first = points[first_id]
        if circle is not None and _geometry_minimum_enclosing_circle_integer_contains(circle, first):
            continue
        circle = (first[0], first[1], 1, 0)
        for second_position in range(position):
            second = points[order[second_position]]
            if _geometry_minimum_enclosing_circle_integer_contains(circle, second):
                continue
            circle = _geometry_minimum_enclosing_circle_integer_diameter(first, second)
            for third_position in range(second_position):
                third = points[order[third_position]]
                if not _geometry_minimum_enclosing_circle_integer_contains(circle, third):
                    circle = _geometry_minimum_enclosing_circle_integer_three(first, second, third)
    (x, y, denominator, squared) = circle
    return [int((point[0] * denominator - x) ** 2 + (point[1] * denominator - y) ** 2 == squared) for point in points]
import sys
read = sys.stdin.buffer.readline
n = int(read())
points = [tuple(map(int, read().split())) for _ in range(n)]
print(''.join(map(str, minimum_enclosing_circle_boundary(points))))
