"""2次元点集合でEuclidean距離が最小の2点を求める。"""

def closest_pair(points):
    """最短距離の点対を反復型divide-and-conquerで求める。"""
    ordered = sorted(((point[0], point[1], index) for (index, point) in enumerate(points)))
    n = len(ordered)
    if n < 2:
        raise ValueError('at least two points are required')
    xs = [point[0] for point in ordered]
    ys = [point[1] for point in ordered]
    ids = [point[2] for point in ordered]
    dx = xs[1] - xs[0]
    dy = ys[1] - ys[0]
    distance = dx * dx + dy * dy
    (first, second) = sorted((ids[0], ids[1]))
    for i in range(1, n):
        dx = xs[i] - xs[i - 1]
        dy = ys[i] - ys[i - 1]
        value = dx * dx + dy * dy
        if value <= distance:
            (a, b) = (ids[i - 1], ids[i])
            if a > b:
                (a, b) = (b, a)
            if value < distance or a < first or (a == first and b < second):
                (distance, first, second) = (value, a, b)
    if distance == 0:
        return (first, second, distance)
    del ordered
    by_y = list(range(n))
    buffer = [0] * n
    width = 1
    while width < n:
        for left in range(0, n, width << 1):
            middle = min(left + width, n)
            right = min(middle + width, n)
            if middle == right:
                buffer[left:right] = by_y[left:right]
                continue
            (i, j, write) = (left, middle, left)
            while i < middle and j < right:
                if ys[by_y[i]] <= ys[by_y[j]]:
                    buffer[write] = by_y[i]
                    i += 1
                else:
                    buffer[write] = by_y[j]
                    j += 1
                write += 1
            while i < middle:
                buffer[write] = by_y[i]
                i += 1
                write += 1
            while j < right:
                buffer[write] = by_y[j]
                j += 1
                write += 1
            boundary = xs[middle]
            strip = []
            for pos in range(left, right):
                point = buffer[pos]
                (x, y) = (xs[point], ys[point])
                dx = x - boundary
                if dx * dx > distance:
                    continue
                for other in reversed(strip):
                    dy = y - ys[other]
                    if dy * dy > distance:
                        break
                    dx = x - xs[other]
                    value = dx * dx + dy * dy
                    if value <= distance:
                        (a, b) = (ids[point], ids[other])
                        if a > b:
                            (a, b) = (b, a)
                        if value < distance or a < first or (a == first and b < second):
                            (distance, first, second) = (value, a, b)
                strip.append(point)
        (by_y, buffer) = (buffer, by_y)
        width <<= 1
    return (first, second, distance)
import sys

def main():
    read = sys.stdin.buffer.readline
    answer = []
    for _ in range(int(read())):
        points = [tuple(map(int, read().split())) for _ in range(int(read()))]
        (first, second, distance) = closest_pair(points)
        answer.append(f'{first} {second}')
    sys.stdout.write('\n'.join(answer))
if __name__ == '__main__':
    main()
