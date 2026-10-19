"""最小全域森のLink-Cut Tree版と一括処理版の比較用実装。"""


class IncrementalMinimumSpanningForest:
    """整数重みの辺を追加するたびに、森から外れた辺の追加順IDを返す。"""

    __slots__ = ("n", "weight", "components", "_count", "_dsu", "_left", "_right", "_parent", "_reverse", "_maximum", "_weights", "_from", "_to", "_ids")

    def __init__(self, n):
        if n < 0:
            raise ValueError("n must be nonnegative")
        self.n = n
        self.weight = 0
        self.components = n
        self._count = 0
        self._dsu = [-1] * n
        self._left = [0] * (n + 1)
        self._right = [0] * (n + 1)
        self._parent = [0] * (n + 1)
        self._reverse = bytearray(n + 1)
        self._maximum = [0] * (n + 1)
        self._weights = [0] * (n + 1)
        self._from = []
        self._to = []
        self._ids = []

    def _pull(self, node):
        maximum = self._maximum
        weights = self._weights
        best = node if node > self.n else 0
        a = maximum[self._left[node]]
        b = maximum[self._right[node]]
        if weights[a] > weights[best]:
            best = a
        if weights[b] > weights[best]:
            best = b
        maximum[node] = best

    def _splay(self, node):
        left, right, parent = self._left, self._right, self._parent
        reverse, maximum, weights = self._reverse, self._maximum, self._weights
        p = parent[node]
        if not p or left[p] != node and right[p] != node:
            if reverse[node]:
                a, b = left[node], right[node]
                if a:
                    left[a], right[a] = right[a], left[a]
                    reverse[a] ^= 1
                if b:
                    left[b], right[b] = right[b], left[b]
                    reverse[b] ^= 1
                reverse[node] = 0
            return
        stack = [node]
        current = node
        while True:
            p = parent[current]
            if not p or left[p] != current and right[p] != current:
                break
            current = p
            stack.append(current)
        root_maximum = maximum[current]
        while stack:
            current = stack.pop()
            if reverse[current]:
                a, b = left[current], right[current]
                if a:
                    left[a], right[a] = right[a], left[a]
                    reverse[a] ^= 1
                if b:
                    left[b], right[b] = right[b], left[b]
                    reverse[b] ^= 1
                reverse[current] = 0
        while True:
            p = parent[node]
            if not p or left[p] != node and right[p] != node:
                break
            g = parent[p]
            if g and (left[g] == p or right[g] == p):
                h = parent[g]
                if left[p] == node:
                    if left[g] == p:
                        a, b = right[p], right[node]
                        left[g], left[p] = a, b
                        right[p], right[node] = g, p
                        parent[g] = p
                        if a:
                            parent[a] = g
                        if b:
                            parent[b] = p
                    else:
                        a, b = left[node], right[node]
                        right[g], left[p] = a, b
                        left[node], right[node] = g, p
                        parent[g] = node
                        if a:
                            parent[a] = g
                        if b:
                            parent[b] = p
                else:
                    if right[g] == p:
                        a, b = left[p], left[node]
                        right[g], right[p] = a, b
                        left[p], left[node] = g, p
                        parent[g] = p
                        if a:
                            parent[a] = g
                        if b:
                            parent[b] = p
                    else:
                        a, b = left[node], right[node]
                        right[p], left[g] = a, b
                        left[node], right[node] = p, g
                        parent[g] = node
                        if a:
                            parent[a] = p
                        if b:
                            parent[b] = g
                parent[p] = node
                parent[node] = h
                if h:
                    if left[h] == g:
                        left[h] = node
                    elif right[h] == g:
                        right[h] = node
                self._pull(g)
                self._pull(p)
            else:
                if left[p] == node:
                    middle = right[node]
                    right[node] = p
                    left[p] = middle
                else:
                    middle = left[node]
                    left[node] = p
                    right[p] = middle
                if middle:
                    parent[middle] = p
                parent[p] = node
                parent[node] = g
                self._pull(p)
        maximum[node] = root_maximum

    def _access(self, node):
        last = 0
        current = node
        while current:
            self._splay(current)
            if self._right[current] != last:
                self._right[current] = last
                self._pull(current)
            last = current
            current = self._parent[current]
        if last != node:
            self._splay(node)

    def _make_root(self, node):
        self._access(node)
        self._left[node], self._right[node] = self._right[node], self._left[node]
        self._reverse[node] ^= 1

    def add(self, u, v, weight):
        """辺を追加し、外れた辺のIDを返す。新規接続なら-1、不採用なら今回のID。"""
        n = self.n
        if not 0 <= u < n or not 0 <= v < n:
            raise ValueError("vertex index out of range")
        edge_id = self._count
        self._count += 1
        if u == v:
            return edge_id
        if weight <= self._weights[0]:
            self._weights[0] = weight - 1
        dsu = self._dsu
        a, b = u, v
        while dsu[a] >= 0:
            if dsu[dsu[a]] >= 0:
                dsu[a] = dsu[dsu[a]]
            a = dsu[a]
        while dsu[b] >= 0:
            if dsu[dsu[b]] >= 0:
                dsu[b] = dsu[dsu[b]]
            b = dsu[b]
        if a != b:
            first, second = u + 1, v + 1
            if dsu[a] > dsu[b]:
                a, b = b, a
            else:
                first, second = second, first
            dsu[a] += dsu[b]
            dsu[b] = a
            self.components -= 1
            node = len(self._weights)
            self._weights.append(weight)
            self._left.append(0)
            self._right.append(0)
            self._parent.append(0)
            self._reverse.append(0)
            self._maximum.append(node)
            self._from.append(u)
            self._to.append(v)
            self._ids.append(edge_id)
            removed = -1
        else:
            self._make_root(u + 1)
            self._access(v + 1)
            node = self._maximum[v + 1]
            old_weight = self._weights[node]
            if weight >= old_weight:
                return edge_id
            slot = node - n - 1
            removed = self._ids[slot]
            self._splay(node)
            self._parent[self._left[node]] = node
            self._parent[self._right[node]] = 0
            self._left[node] = self._right[node] = 0
            self._parent[node] = v + 1
            self._weights[node] = weight
            self._maximum[node] = node
            self._from[slot] = u
            self._to[slot] = v
            self._ids[slot] = edge_id
            self.weight += weight - old_weight
            return removed
        self._make_root(first)
        self._parent[first] = node
        self._parent[node] = second
        self.weight += weight
        return removed

    def edges(self):
        """現在採用中の辺を、(追加順ID, u, v, 重み)のlistとしてID順に返す。"""
        return sorted((edge_id, self._from[i], self._to[i], self._weights[self.n + 1 + i])
                      for i, edge_id in enumerate(self._ids))

    def __repr__(self):
        return f"IncrementalMinimumSpanningForest(n={self.n}, edges={self.edges()!r})"

    def __str__(self):
        return str(self.edges())


def incremental_msf(n, edges):
    """追加順の辺列から、各追加時に最小全域森を外れる辺のIDをまとめて返す。"""
    if n < 0:
        raise ValueError("n must be nonnegative")
    edges = list(edges)
    m = len(edges)
    first = [0] * m
    second = [0] * m
    weights = [0] * m
    for i, (u, v, weight) in enumerate(edges):
        if not 0 <= u < n or not 0 <= v < n:
            raise ValueError("vertex index out of range")
        first[i], second[i], weights[i] = u, v, weight
    order = sorted(range(m), key=lambda i: (weights[i], i))
    parent = [-1] * n
    history = []
    last = [0] * m

    def unite(u, v):
        while parent[u] >= 0:
            u = parent[u]
        while parent[v] >= 0:
            v = parent[v]
        if u == v:
            return False
        if parent[u] > parent[v]:
            u, v = v, u
        history.append(v)
        history.append(parent[v])
        parent[u] += parent[v]
        parent[v] = u
        return True

    def rollback(size):
        while len(history) > size:
            value = history.pop()
            vertex = history.pop()
            parent[parent[vertex]] -= value
            parent[vertex] = value

    stack = [(0, m, order, -1)]
    while stack:
        left, right, candidates, restore = stack.pop()
        if restore >= 0:
            rollback(restore)
            continue
        if not candidates:
            continue
        checkpoint = len(history)
        if right - left <= 1:
            for edge_id in candidates:
                if unite(first[edge_id], second[edge_id]):
                    last[edge_id] = right
            rollback(checkpoint)
            continue
        fixed = []
        variable = []
        for edge_id in candidates:
            if edge_id < left:
                fixed.append(edge_id)
            else:
                variable.append(edge_id)
        safe = []
        if fixed:
            for edge_id in variable:
                unite(first[edge_id], second[edge_id])
            for edge_id in fixed:
                if unite(first[edge_id], second[edge_id]):
                    safe.append(edge_id)
            rollback(checkpoint)
            useful = set()
            for edge_id in fixed:
                if unite(first[edge_id], second[edge_id]):
                    useful.add(edge_id)
            rollback(checkpoint)
            for edge_id in safe:
                unite(first[edge_id], second[edge_id])
                last[edge_id] = right
                useful.remove(edge_id)
            candidates = [edge_id for edge_id in candidates if edge_id >= left or edge_id in useful]
        middle = (left + right) >> 1
        before = [edge_id for edge_id in candidates if edge_id < middle]
        stack.append((0, 0, None, checkpoint))
        stack.append((middle, right, candidates, -1))
        stack.append((left, middle, before, -1))
    answers = [i if last[i] <= i else -1 for i in range(m)]
    for edge_id, end in enumerate(last):
        if edge_id < end < m:
            answers[end] = edge_id
    return answers


if __name__ == "__main__":
    import sys

    input = sys.stdin.buffer.readline
    n, m = map(int, input().split())
    forest = IncrementalMinimumSpanningForest(n)
    answers = []
    for _ in range(m):
        u, v, weight = map(int, input().split())
        answers.append(str(forest.add(u, v, weight)))
    sys.stdout.write(" ".join(answers) + "\n")
