"""親を子より先に並べる制約下で0/1列の転倒数を最小化する。"""

from heapq import heappop, heappush


class _Block:
    __slots__ = ("zero", "one", "vertex")

    def __init__(self, zero, one, vertex):
        self.zero = zero
        self.one = one
        self.vertex = vertex

    def __lt__(self, other):
        first = self.zero * other.one
        second = other.zero * self.one
        if first != second:
            return first > second
        return self.vertex < other.vertex


def _validate_parent(parent, root):
    size = len(parent)
    if not 0 <= root < size:
        raise IndexError("root is outside the tree")
    state = [0] * size
    state[root] = 2
    for start in range(size):
        if state[start]:
            continue
        path = []
        vertex = start
        while state[vertex] == 0:
            state[vertex] = 1
            path.append(vertex)
            next_vertex = parent[vertex]
            if not 0 <= next_vertex < size:
                raise IndexError("parent is outside the tree")
            vertex = next_vertex
        if state[vertex] == 1:
            raise ValueError("parent contains a cycle")
        for vertex in path:
            state[vertex] = 2


def min_block_inversions(parent, zero_count, one_count, root=0):
    """各頂点の0列・1列を親優先で並べたときの最小転倒数を返す。O(N log N)。"""
    parent = list(parent)
    zero_count = list(zero_count)
    one_count = list(one_count)
    size = len(parent)
    if len(zero_count) != size or len(one_count) != size:
        raise ValueError("parent and count arrays must have the same length")
    if any(value < 0 for value in zero_count + one_count):
        raise ValueError("counts must be nonnegative")
    _validate_parent(parent, root)

    representative = list(range(size))
    heap = []
    for vertex in range(size):
        if vertex != root:
            heappush(heap, _Block(zero_count[vertex], one_count[vertex], vertex))

    answer = 0
    while heap:
        block = heappop(heap)
        vertex = block.vertex
        if block.zero != zero_count[vertex] or block.one != one_count[vertex]:
            continue
        ancestor = parent[vertex]
        while representative[ancestor] != ancestor:
            representative[ancestor] = representative[representative[ancestor]]
            ancestor = representative[ancestor]
        representative[vertex] = ancestor
        answer += one_count[ancestor] * zero_count[vertex]
        zero_count[ancestor] += zero_count[vertex]
        one_count[ancestor] += one_count[vertex]
        if ancestor != root:
            heappush(heap, _Block(
                zero_count[ancestor], one_count[ancestor], ancestor
            ))
    return answer


def min_inversions(parent, labels, root=0):
    """0/1ラベル付き木を親優先で並べたときの最小転倒数を返す。O(N log N)。"""
    labels = list(labels)
    if any(label not in (0, 1) for label in labels):
        raise ValueError("labels must contain only 0 and 1")
    return min_block_inversions(
        parent,
        [label == 0 for label in labels],
        [label == 1 for label in labels],
        root,
    )
