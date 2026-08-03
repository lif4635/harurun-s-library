"""2次元点集合の凸包をAndrewの単調鎖法で構築する。"""

from library_codex.geometry.Orientation import cross


def convex_hull(points, keep_collinear=False):
    """凸包の頂点を反時計回りに、始点を重ねず返す。O(N log N)。"""
    points = sorted(set(points))
    if len(points) <= 1:
        return points
    if keep_collinear and all(
        cross(points[0], points[-1], point) == 0 for point in points[1:-1]
    ):
        return points

    lower = []
    upper = []
    for point in points:
        while len(lower) >= 2:
            turn = cross(lower[-2], lower[-1], point)
            if turn > 0 or keep_collinear and turn == 0:
                break
            lower.pop()
        lower.append(point)
    for point in reversed(points):
        while len(upper) >= 2:
            turn = cross(upper[-2], upper[-1], point)
            if turn > 0 or keep_collinear and turn == 0:
                break
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]
