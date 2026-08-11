"""2次元点集合でEuclidean距離が最小の2点を求める。"""


def closest_pair(points):
    """最短距離の点対を反復型divide-and-conquerで求める。"""
    points = list(points)
    if len(points) < 2:
        raise ValueError("at least two points are required")
    ordered = sorted((point[0], point[1], index)
                     for index, point in enumerate(points))
    duplicate = None
    for index in range(1, len(ordered)):
        if ordered[index][:2] == ordered[index - 1][:2]:
            pair = tuple(sorted((ordered[index - 1][2], ordered[index][2])))
            if duplicate is None or pair < duplicate:
                duplicate = pair
    if duplicate is not None:
        return duplicate[0], duplicate[1], 0

    n = len(ordered)
    by_y = ordered[:]
    best = {index: (float("inf"), -1, -1) for index in range(n)}
    width = 1
    while width < n:
        merged_y = by_y[:]
        next_best = {}
        for left in range(0, n, width << 1):
            middle = min(left + width, n)
            right = min(middle + width, n)
            if middle == right:
                next_best[left] = best[left]
                continue
            candidate = min(best[left], best[middle])
            i, j, write = left, middle, left
            while i < middle and j < right:
                if (by_y[i][1], by_y[i][0], by_y[i][2]) <= (
                        by_y[j][1], by_y[j][0], by_y[j][2]):
                    merged_y[write] = by_y[i]
                    i += 1
                else:
                    merged_y[write] = by_y[j]
                    j += 1
                write += 1
            while i < middle:
                merged_y[write] = by_y[i]
                i += 1
                write += 1
            while j < right:
                merged_y[write] = by_y[j]
                j += 1
                write += 1

            boundary2 = ordered[middle - 1][0] + ordered[middle][0]
            strip = []
            distance = candidate[0]
            for point in merged_y[left:right]:
                if (2 * point[0] - boundary2) ** 2 <= 4 * distance:
                    for other in reversed(strip):
                        dy = point[1] - other[1]
                        if dy * dy > distance:
                            break
                        dx = point[0] - other[0]
                        value = dx * dx + dy * dy
                        first, second = sorted((point[2], other[2]))
                        current = (value, first, second)
                        if current < candidate:
                            candidate = current
                            distance = value
                    strip.append(point)
            next_best[left] = candidate
        by_y = merged_y
        best = next_best
        width <<= 1
    distance, first, second = best[0]
    return first, second, distance
