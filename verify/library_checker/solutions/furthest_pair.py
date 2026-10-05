"""2次元点の外積と向きを整数演算で判定する。"""

def cross(origin, first, second):
    """ベクトル origin→first と origin→second の外積を返す。O(1)。"""
    return (first[0] - origin[0]) * (second[1] - origin[1]) - (first[1] - origin[1]) * (second[0] - origin[0])

def orientation(first, second, third):
    """3点の向きを反時計回りなら1、時計回りなら-1、一直線なら0で返す。O(1)。"""
    value = cross(first, second, third)
    return (value > 0) - (value < 0)
'2次元点集合の凸包をAndrewの単調鎖法で構築する。'

def convex_hull(points, keep_collinear=False):
    """凸包の頂点を反時計回りに、始点を重ねず返す。O(N log N)。"""
    points = sorted(set(points))
    if len(points) <= 1:
        return points
    if keep_collinear and all((cross(points[0], points[-1], point) == 0 for point in points[1:-1])):
        return points
    lower = []
    upper = []
    for point in points:
        while len(lower) >= 2:
            turn = cross(lower[-2], lower[-1], point)
            if turn > 0 or (keep_collinear and turn == 0):
                break
            lower.pop()
        lower.append(point)
    for point in reversed(points):
        while len(upper) >= 2:
            turn = cross(upper[-2], upper[-1], point)
            if turn > 0 or (keep_collinear and turn == 0):
                break
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]
'2次元点集合で距離が最大の2点を求める。'

def _geometry_furthest_pair_cross(first, second):
    return first[0] * second[1] - first[1] * second[0]

def furthest_pair(points):
    """距離最大の入力添字pairと距離の二乗を返す。"""
    points = [tuple(point) for point in points]
    if not points:
        raise ValueError('at least one point is required')
    first_index = {}
    for (index, point) in enumerate(points):
        first_index.setdefault(point, index)
    hull = convex_hull(points)
    if len(hull) == 1:
        index = first_index[hull[0]]
        return (index, index, 0)
    best_pair = None
    best_distance = -1

    def update(first, second):
        nonlocal best_pair, best_distance
        i = first_index[hull[first]]
        j = first_index[hull[second]]
        if i > j:
            (i, j) = (j, i)
        dx = hull[first][0] - hull[second][0]
        dy = hull[first][1] - hull[second][1]
        distance = dx * dx + dy * dy
        if distance > best_distance or (distance == best_distance and (i, j) < best_pair):
            best_distance = distance
            best_pair = (i, j)
    if len(hull) == 2:
        update(0, 1)
        return (best_pair[0], best_pair[1], best_distance)
    j = 1
    size = len(hull)
    for i in range(size):
        nxt = (i + 1) % size
        edge = (hull[nxt][0] - hull[i][0], hull[nxt][1] - hull[i][1])
        while True:
            next_j = (j + 1) % size
            current = abs(_geometry_furthest_pair_cross(edge, (hull[j][0] - hull[i][0], hull[j][1] - hull[i][1])))
            candidate = abs(_geometry_furthest_pair_cross(edge, (hull[next_j][0] - hull[i][0], hull[next_j][1] - hull[i][1])))
            if candidate <= current:
                break
            j = next_j
        update(i, j)
        update(nxt, j)
    return (best_pair[0], best_pair[1], best_distance)
import sys

def main():
    read = sys.stdin.buffer.readline
    answer = []
    for _ in range(int(read())):
        points = [tuple(map(int, read().split())) for _ in range(int(read()))]
        (first, second, distance) = furthest_pair(points)
        if first == second:
            (first, second) = (0, 1)
        answer.append(f'{first} {second}')
    sys.stdout.write('\n'.join(answer))
if __name__ == '__main__':
    main()
