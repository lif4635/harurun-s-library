"""2次元点集合で距離が最大の2点を求める。"""

from library_codex.geometry.ConvexHull import convex_hull


def _cross(first, second):
    return first[0] * second[1] - first[1] * second[0]


def furthest_pair(points):
    """距離最大の入力添字pairと距離の二乗を返す。"""
    points = [tuple(point) for point in points]
    if not points:
        raise ValueError("at least one point is required")
    first_index = {}
    for index, point in enumerate(points):
        first_index.setdefault(point, index)
    hull = convex_hull(points)
    if len(hull) == 1:
        index = first_index[hull[0]]
        return index, index, 0

    best_pair = None
    best_distance = -1

    def update(first, second):
        nonlocal best_pair, best_distance
        i = first_index[hull[first]]
        j = first_index[hull[second]]
        if i > j:
            i, j = j, i
        dx = hull[first][0] - hull[second][0]
        dy = hull[first][1] - hull[second][1]
        distance = dx * dx + dy * dy
        if distance > best_distance or distance == best_distance and (i, j) < best_pair:
            best_distance = distance
            best_pair = (i, j)

    if len(hull) == 2:
        update(0, 1)
        return best_pair[0], best_pair[1], best_distance

    j = 1
    size = len(hull)
    for i in range(size):
        nxt = (i + 1) % size
        edge = (hull[nxt][0] - hull[i][0], hull[nxt][1] - hull[i][1])
        while True:
            next_j = (j + 1) % size
            current = abs(_cross(edge, (hull[j][0] - hull[i][0], hull[j][1] - hull[i][1])))
            candidate = abs(_cross(edge, (hull[next_j][0] - hull[i][0], hull[next_j][1] - hull[i][1])))
            if candidate <= current:
                break
            j = next_j
        update(i, j)
        update(nxt, j)
    return best_pair[0], best_pair[1], best_distance
