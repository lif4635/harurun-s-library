"""軸平行矩形の和集合面積をsweep lineで求める。"""

def union_rectangle_area(rectangles):
    """Area of the union of axis-aligned half-open rectangles."""
    rectangles = [(left, right, bottom, top) for (left, right, bottom, top) in rectangles if left < right and bottom < top]
    if not rectangles:
        return 0
    ys = sorted({coordinate for rectangle in rectangles for coordinate in rectangle[2:]})
    index = {value: i for (i, value) in enumerate(ys)}
    events = []
    for (left, right, bottom, top) in rectangles:
        lower = index[bottom]
        upper = index[top]
        events.append((left, 1, lower, upper))
        events.append((right, -1, lower, upper))
    events.sort()
    size = len(ys) - 1
    cover = [0] * (size << 1)
    uncovered = [0] * size + [ys[i + 1] - ys[i] for i in range(size)]
    for node in range(size - 1, 0, -1):
        uncovered[node] = uncovered[node << 1] + uncovered[node << 1 | 1]
    total = ys[-1] - ys[0]
    area = 0
    previous_x = events[0][0]
    for (x, delta, lower, upper) in events:
        area += (total - (0 if cover[1] else uncovered[1])) * (x - previous_x)
        previous_x = x
        left = lower + size
        right = upper + size
        left_path = left // (left & -left) >> 1
        right_path = right // (right & -right) - 1 >> 1
        while left < right:
            if left & 1:
                cover[left] += delta
                left += 1
            if right & 1:
                right -= 1
                cover[right] += delta
            left >>= 1
            right >>= 1
        while left_path:
            child = left_path << 1
            uncovered[left_path] = (0 if cover[child] else uncovered[child]) + (0 if cover[child | 1] else uncovered[child | 1])
            left_path >>= 1
        while right_path:
            child = right_path << 1
            uncovered[right_path] = (0 if cover[child] else uncovered[child]) + (0 if cover[child | 1] else uncovered[child | 1])
            right_path >>= 1
    return area

class UnionRectangle:
    __slots__ = ('rectangles',)

    def __init__(self):
        self.rectangles = []

    def add(self, left, right, bottom, top):
        self.rectangles.append((left, right, bottom, top))

    def run(self):
        return union_rectangle_area(self.rectangles)

    def tolist(self):
        return self.rectangles[:]

    def __str__(self):
        return str(self.rectangles)

    def __repr__(self):
        return 'UnionRectangle(' + str(self.rectangles) + ')'
import sys
read = sys.stdin.buffer.readline
rectangles = []
for _ in range(int(read())):
    (left, bottom, right, top) = map(int, read().split())
    rectangles.append((left, right, bottom, top))
print(union_rectangle_area(rectangles))
