"""変更されない列の半開区間に含まれる異なる値の個数を求める。"""


class StaticRangeDistinct:
    """Persistent Segment Treeで静的なrange distinct queryを処理する。"""

    __slots__ = ("size", "roots", "left", "right", "total")

    def __init__(self, values):
        values = list(values)
        size = len(values)
        left = [0]
        right = [0]
        total = [0]
        roots = [0] * (size + 1)
        last = {}

        def update(root, index, delta):
            new_root = len(total)
            left.append(left[root])
            right.append(right[root])
            total.append(total[root] + delta)
            node = new_root
            lower = 0
            upper = size
            while upper - lower > 1:
                middle = (lower + upper) >> 1
                if index < middle:
                    child = left[node]
                    new_child = len(total)
                    left.append(left[child])
                    right.append(right[child])
                    total.append(total[child] + delta)
                    left[node] = new_child
                    node = new_child
                    upper = middle
                else:
                    child = right[node]
                    new_child = len(total)
                    left.append(left[child])
                    right.append(right[child])
                    total.append(total[child] + delta)
                    right[node] = new_child
                    node = new_child
                    lower = middle
            return new_root

        root = 0
        if size:
            for index, value in enumerate(values):
                previous = last.get(value)
                if previous is not None:
                    root = update(root, previous, -1)
                root = update(root, index, 1)
                roots[index + 1] = root
                last[value] = index

        self.size = size
        self.roots = roots
        self.left = left
        self.right = right
        self.total = total

    def count(self, left, right):
        """半開区間 ``[left, right)`` に現れる異なる値の個数を返す。"""
        if not 0 <= left <= right <= self.size:
            raise IndexError("range is outside the sequence")
        if left == right:
            return 0
        node = self.roots[right]
        lower = 0
        upper = self.size
        result = 0
        tree_left = self.left
        tree_right = self.right
        total = self.total
        query_left = left
        while node and lower < upper:
            if query_left <= lower:
                result += total[node]
                break
            middle = (lower + upper) >> 1
            if query_left < middle:
                result += total[tree_right[node]]
                node = tree_left[node]
                upper = middle
            else:
                node = tree_right[node]
                lower = middle
        return result

