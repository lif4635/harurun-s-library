"""軸平行矩形の和集合面積をsweep lineで求める。"""

def union_rectangle_area(rectangles):
    """Area of the union of axis-aligned half-open rectangles."""
    rectangles = [(left, right, bottom, top)
                  for left, right, bottom, top in rectangles
                  if left < right and bottom < top]
    if not rectangles:
        return 0
    xs = sorted({value for rectangle in rectangles for value in rectangle[:2]})
    ys = sorted({value for rectangle in rectangles for value in rectangle[2:]})
    sweep_axis = 0
    interval_axis = 2
    if len(xs) < len(ys):
        xs, ys = ys, xs
        sweep_axis, interval_axis = 2, 0
    x_index = {value: i for i, value in enumerate(xs)}
    y_index = {value: i for i, value in enumerate(ys)}
    heads = [-1] * len(xs)
    links = [0] * (2 * len(rectangles))
    lowers = [0] * len(rectangles)
    uppers = [0] * len(rectangles)
    for i, rectangle in enumerate(rectangles):
        lowers[i] = y_index[rectangle[interval_axis]]
        uppers[i] = y_index[rectangle[interval_axis + 1]]
        left = x_index[rectangle[sweep_axis]]
        right = x_index[rectangle[sweep_axis + 1]]
        event = i << 1
        links[event] = heads[left]
        heads[left] = event
        links[event | 1] = heads[right]
        heads[right] = event | 1
    del x_index, y_index
    size = len(ys) - 1
    cover = [0] * (size << 1)
    uncovered = [0] * size + [ys[i + 1] - ys[i] for i in range(size)]
    for node in range(size - 1, 0, -1):
        uncovered[node] = uncovered[node << 1] + uncovered[node << 1 | 1]
    total = ys[-1] - ys[0]
    area = 0
    for position in range(len(xs) - 1):
        event = heads[position]
        while event != -1:
            index = event >> 1
            delta = 1 - ((event & 1) << 1)
            left = lowers[index] + size
            right = uppers[index] + size
            left_path = (left // (left & -left)) >> 1
            right_path = ((right // (right & -right)) - 1) >> 1
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
                uncovered[left_path] = ((0 if cover[child] else uncovered[child])
                                        + (0 if cover[child | 1] else uncovered[child | 1]))
                left_path >>= 1
            while right_path:
                child = right_path << 1
                uncovered[right_path] = ((0 if cover[child] else uncovered[child])
                                         + (0 if cover[child | 1] else uncovered[child | 1]))
                right_path >>= 1
            event = links[event]
        area += (total - (0 if cover[1] else uncovered[1])) * (xs[position + 1] - xs[position])
    return area

class UnionRectangle:
    __slots__ = ("rectangles",)

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
        return "UnionRectangle(" + str(self.rectangles) + ")"
