"""多角形の符号付き面積・重心・格子点数を求める。"""

from math import gcd


def signed_doubled_area(polygon):
    """頂点順の向きを保った面積の2倍を返す。"""
    polygon = list(polygon)
    total = 0
    for index, point in enumerate(polygon):
        other = polygon[(index + 1) % len(polygon)]
        total += point[0] * other[1] - point[1] * other[0]
    return total


def polygon_centroid(polygon):
    """一様な多角形板の重心を返す。"""
    polygon = list(polygon)
    area2 = signed_doubled_area(polygon)
    if area2 == 0:
        raise ValueError("polygon must have nonzero area")
    x_sum = y_sum = 0
    for index, point in enumerate(polygon):
        other = polygon[(index + 1) % len(polygon)]
        cross = point[0] * other[1] - point[1] * other[0]
        x_sum += (point[0] + other[0]) * cross
        y_sum += (point[1] + other[1]) * cross
    scale = 3 * area2
    return x_sum / scale, y_sum / scale


def pick_lattice_points(polygon):
    """格子多角形の境界上と内部の格子点数を返す。"""
    polygon = list(polygon)
    if len(polygon) < 3:
        raise ValueError("at least three vertices are required")
    boundary = 0
    for index, point in enumerate(polygon):
        other = polygon[(index + 1) % len(polygon)]
        boundary += gcd(abs(other[0] - point[0]), abs(other[1] - point[1]))
    area2 = abs(signed_doubled_area(polygon))
    interior2 = area2 - boundary + 2
    if interior2 < 0 or interior2 & 1:
        raise ValueError("polygon must be a simple lattice polygon")
    return boundary, interior2 // 2
