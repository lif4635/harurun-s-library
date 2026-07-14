"""Meldable heap and rectangle-union sweep structures."""


class SkewHeap:
    """Array-backed meldable heap with whole-heap additive lazy action."""

    __slots__ = ("min_heap", "key", "value", "left", "right", "lazy")

    def __init__(self, min_heap=True):
        self.min_heap = min_heap
        self.key = []
        self.value = []
        self.left = []
        self.right = []
        self.lazy = []

    def new_node(self, key, value=None):
        node = len(self.key)
        self.key.append(key)
        self.value.append(value)
        self.left.append(-1)
        self.right.append(-1)
        self.lazy.append(0)
        return node

    def _better(self, first, second):
        a = self.key[first] + self.lazy[first]
        b = self.key[second] + self.lazy[second]
        return a < b if self.min_heap else a > b

    def _push(self, node):
        action = self.lazy[node]
        if action:
            self.key[node] += action
            left = self.left[node]
            right = self.right[node]
            if left >= 0:
                self.lazy[left] += action
            if right >= 0:
                self.lazy[right] += action
            self.lazy[node] = 0

    def meld(self, first, second):
        if first < 0:
            return second
        if second < 0:
            return first
        path = []
        while first >= 0 and second >= 0:
            if not self._better(first, second):
                first, second = second, first
            self._push(first)
            path.append(first)
            first = self.right[first]
        root = first if first >= 0 else second
        for node in reversed(path):
            self.right[node] = root
            self.left[node], self.right[node] = self.right[node], self.left[node]
            root = node
        return root

    def push(self, root, key, value=None):
        return self.meld(root, self.new_node(key, value))

    def add_all(self, root, delta):
        if root >= 0:
            self.lazy[root] += delta
        return root

    apply = add_all

    def top(self, root):
        if root < 0:
            raise IndexError("empty skew heap")
        self._push(root)
        return self.key[root], self.value[root]

    def pop(self, root):
        if root < 0:
            raise IndexError("empty skew heap")
        self._push(root)
        return self.meld(self.left[root], self.right[root])


def union_rectangle_area(rectangles):
    """Area of the union of axis-aligned half-open rectangles."""
    rectangles = [(left, right, bottom, top)
                  for left, right, bottom, top in rectangles
                  if left < right and bottom < top]
    if not rectangles:
        return 0
    ys = sorted({coordinate for rectangle in rectangles
                 for coordinate in rectangle[2:]})
    index = {value: i for i, value in enumerate(ys)}
    events = []
    for left, right, bottom, top in rectangles:
        lower = index[bottom]
        upper = index[top]
        events.append((left, 1, lower, upper))
        events.append((right, -1, lower, upper))
    events.sort()
    segments = len(ys) - 1
    size = 1
    while size < segments:
        size <<= 1
    cover = [0] * (size << 1)
    covered = [0] * (size << 1)

    def pull(node, left, right):
        if cover[node]:
            covered[node] = ys[min(right, segments)] - ys[left]
        elif right - left == 1:
            covered[node] = 0
        else:
            covered[node] = covered[node << 1] + covered[node << 1 | 1]

    def update(query_left, query_right, delta):
        stack = [(1, 0, size, 0)]
        while stack:
            node, left, right, state = stack.pop()
            if query_right <= left or right <= query_left:
                continue
            if state:
                pull(node, left, right)
            elif query_left <= left and right <= query_right:
                cover[node] += delta
                pull(node, left, right)
            else:
                middle = (left + right) >> 1
                stack.append((node, left, right, 1))
                stack.append((node << 1 | 1, middle, right, 0))
                stack.append((node << 1, left, middle, 0))

    area = 0
    previous_x = events[0][0]
    position = 0
    while position < len(events):
        x = events[position][0]
        area += covered[1] * (x - previous_x)
        while position < len(events) and events[position][0] == x:
            _, delta, lower, upper = events[position]
            update(lower, upper, delta)
            position += 1
        previous_x = x
    return area


class UnionRectangle:
    __slots__ = ("rectangles",)

    def __init__(self):
        self.rectangles = []

    def add(self, left, right, bottom, top):
        self.rectangles.append((left, right, bottom, top))

    def run(self):
        return union_rectangle_area(self.rectangles)
