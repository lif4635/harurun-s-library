"""2つの同じ長さの区間をまとめて対応位置ごとに併合するUnion-Find。"""
from array import array

class RangeParallelUnionFind:
    __slots__ = ('n', 'parent')

    def __init__(self, size):
        self.n = size
        count = size * max(1, size.bit_length())
        kind = 'i' if count < 1 << 31 and array('i').itemsize == 4 else 'q'
        self.parent = array(kind, [-1]) * count

    def merge(self, first, second, length=1, callback=None):
        if length <= 0:
            return
        if first < 0 or second < 0 or first + length > self.n or (second + length > self.n):
            raise IndexError('range is out of bounds')
        n = self.n
        parent = self.parent
        level = length.bit_length() - 1
        width = 1 << level
        stack = [(first, second, level)]
        if length != width:
            stack.append((first + length - width, second + length - width, level))
        while stack:
            (left, right, level) = stack.pop()
            left_root = level * n + left
            right_root = level * n + right
            while parent[left_root] >= 0:
                above = parent[left_root]
                if parent[above] < 0:
                    left_root = above
                    break
                parent[left_root] = parent[above]
                left_root = parent[above]
            while parent[right_root] >= 0:
                above = parent[right_root]
                if parent[above] < 0:
                    right_root = above
                    break
                parent[right_root] = parent[above]
                right_root = parent[above]
            if left_root == right_root:
                continue
            if parent[left_root] > parent[right_root]:
                (left_root, right_root) = (right_root, left_root)
            parent[left_root] += parent[right_root]
            parent[right_root] = left_root
            if level == 0:
                if callback is not None:
                    callback(left_root, right_root)
                continue
            half = 1 << level - 1
            stack.append((left + half, right + half, level - 1))
            stack.append((left, right, level - 1))
    unite = merge

    def find(self, node):
        parent = self.parent
        while parent[node] >= 0:
            above = parent[node]
            if parent[above] < 0:
                return above
            parent[node] = parent[above]
            node = parent[above]
        return node

    def same(self, first, second):
        return self.find(first) == self.find(second)

    def size(self, node):
        return -self.parent[self.find(node)]
import sys

def solve():
    read = sys.stdin.buffer.readline
    (n, q) = map(int, read().split())
    values = list(map(int, read().split()))
    union = RangeParallelUnionFind(n)
    total = 0

    def merged(root, old):
        nonlocal total
        total = (total + values[root] * values[old]) % 998244353
        values[root] = (values[root] + values[old]) % 998244353
    answer = []
    for _ in range(q):
        (k, a, b) = map(int, read().split())
        union.merge(a, b, k, merged)
        answer.append(str(total))
    print('\n'.join(answer))
if __name__ == '__main__':
    solve()
