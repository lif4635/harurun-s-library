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
import sys

def main():
    read = sys.stdin.buffer.readline
    answer = []
    for _ in range(int(read())):
        points = [tuple(map(int, read().split())) for _ in range(int(read()))]
        hull = convex_hull(points)
        answer.append(str(len(hull)))
        answer.extend((f'{x} {y}' for (x, y) in hull))
    sys.stdout.write('\n'.join(answer))
if __name__ == '__main__':
    main()
