"""2つの凸多角形のMinkowski和を構築する。"""

from library_codex.geometry.ConvexHull import convex_hull


def _cross(first, second):
    return first[0] * second[1] - first[1] * second[0]


def _prepare(points):
    points = list(points)
    if len(points) > 1 and points[0] == points[-1]:
        points.pop()
    clean = []
    for point in points:
        point = tuple(point)
        if not clean or clean[-1] != point:
            clean.append(point)
    if len(clean) > 1 and clean[0] == clean[-1]:
        clean.pop()
    if len(clean) <= 2:
        return sorted(set(clean))

    sign = 0
    strict = True
    for index in range(len(clean)):
        first = clean[index - 1]
        second = clean[index]
        third = clean[(index + 1) % len(clean)]
        value = _cross(
            (second[0] - first[0], second[1] - first[1]),
            (third[0] - second[0], third[1] - second[1]),
        )
        if value == 0:
            strict = False
            break
        current = 1 if value > 0 else -1
        if sign and sign != current:
            strict = False
            break
        sign = current
    if not strict:
        clean = convex_hull(clean)
    elif sign < 0:
        clean.reverse()
    start = min(range(len(clean)), key=clean.__getitem__)
    return clean[start:] + clean[:start]


def minkowski_sum(first, second):
    """凸多角形firstとsecondの点和全体の凸包を返す。"""
    first = _prepare(first)
    second = _prepare(second)
    if not first or not second:
        return []
    if len(first) < 3 or len(second) < 3:
        return convex_hull([
            (a[0] + b[0], a[1] + b[1]) for a in first for b in second
        ])

    first_edges = [
        (first[(i + 1) % len(first)][0] - first[i][0],
         first[(i + 1) % len(first)][1] - first[i][1])
        for i in range(len(first))
    ]
    second_edges = [
        (second[(i + 1) % len(second)][0] - second[i][0],
         second[(i + 1) % len(second)][1] - second[i][1])
        for i in range(len(second))
    ]
    point = (first[0][0] + second[0][0], first[0][1] + second[0][1])
    result = [point]
    i = j = 0
    while i < len(first_edges) or j < len(second_edges):
        if i == len(first_edges):
            edge = second_edges[j]
            j += 1
        elif j == len(second_edges):
            edge = first_edges[i]
            i += 1
        else:
            turn = _cross(first_edges[i], second_edges[j])
            if turn > 0:
                edge = first_edges[i]
                i += 1
            elif turn < 0:
                edge = second_edges[j]
                j += 1
            else:
                edge = (first_edges[i][0] + second_edges[j][0],
                        first_edges[i][1] + second_edges[j][1])
                i += 1
                j += 1
        point = (point[0] + edge[0], point[1] + edge[1])
        result.append(point)
    result.pop()
    return result
