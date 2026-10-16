"""過去の版を保持し、区間のアフィン変換・別の版からの区間コピー・区間和を扱う。"""

class PersistentRangeAffineRangeSum:
    """配列を版番号で管理する。初期状態は版0、更新は新しい版番号を返す。"""
    __slots__ = ('n', 'size', 'mod', 'roots', '_left', '_right', '_lb', '_lc', '_rb', '_rc', '_sum')

    def __init__(self, values, mod=998244353):
        if mod <= 0:
            raise ValueError('modulus must be positive')
        values = [value % mod for value in values]
        self.n = len(values)
        self.size = size = 1 << max(0, (len(values) - 1).bit_length()) if values else 1
        self.mod = mod
        count = size * 2
        self._left = [0] * count
        self._right = [0] * count
        self._lb = [1] * count
        self._lc = [0] * count
        self._rb = [1] * count
        self._rc = [0] * count
        self._sum = total = [0] * count
        total[size:size + len(values)] = values
        for node in range(size - 1, 0, -1):
            self._left[node] = node * 2
            self._right[node] = node * 2 + 1
            total[node] = (total[node * 2] + total[node * 2 + 1]) % mod
        self.roots = [(1, 1, 0)]

    def _splice(self, base, source, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError('invalid half-open range')
        stack = [(base, source, 0, self.size)]
        results = []
        (lc, rc) = (self._left, self._right)
        (lb, la, rb, ra) = (self._lb, self._lc, self._rb, self._rc)
        (total, mod) = (self._sum, self.mod)
        while stack:
            (old, new, start, end) = stack.pop()
            if old is None:
                (v, vb, vc) = results.pop()
                (u, ub, uc) = results.pop()
                node = len(total)
                lc.append(u)
                rc.append(v)
                lb.append(ub)
                la.append(uc)
                rb.append(vb)
                ra.append(vc)
                total.append((ub * total[u] + vb * total[v] + (uc + vc) * end) % mod)
                results.append((node, 1, 0))
            elif right <= start or end <= left or old == new:
                results.append(old)
            elif left <= start and end <= right:
                results.append(new)
            else:
                (u, ub, uc) = old
                (v, vb, vc) = new
                middle = start + end >> 1
                stack.append((None, None, 0, middle - start))
                stack.append(((rc[u], ub * rb[u] % mod, (ub * ra[u] + uc) % mod), (rc[v], vb * rb[v] % mod, (vb * ra[v] + vc) % mod), middle, end))
                stack.append(((lc[u], ub * lb[u] % mod, (ub * la[u] + uc) % mod), (lc[v], vb * lb[v] % mod, (vb * la[v] + vc) % mod), start, middle))
        self.roots.append(results[0])
        return len(self.roots) - 1

    def apply(self, left, right, multiplier, addend, version=-1):
        """指定版の区間[left, right)を変換した新しい版番号を返す。元の版は変更しない。"""
        base = self.roots[version]
        (node, b, c) = base
        mod = self.mod
        multiplier %= mod
        addend %= mod
        source = (node, multiplier * b % mod, (multiplier * c + addend) % mod)
        return self._splice(base, source, left, right)

    def copy(self, left, right, source, version=-1):
        """指定版の区間[left, right)をsource版の同じ区間で置換した新しい版番号を返す。"""
        return self._splice(self.roots[version], self.roots[source], left, right)

    def prod(self, left, right, version=-1):
        """指定版の区間[left, right)の和をmodで割った余りを返す。"""
        if not 0 <= left <= right <= self.n:
            raise IndexError('invalid half-open range')
        (root, b, c) = self.roots[version]
        stack = [(root, b, c, 0, self.size)]
        (total, mod) = (self._sum, self.mod)
        (lc, rc) = (self._left, self._right)
        (lb, la, rb, ra) = (self._lb, self._lc, self._rb, self._rc)
        answer = 0
        while stack:
            (node, b, c, start, end) = stack.pop()
            if right <= start or end <= left:
                continue
            if left <= start and end <= right:
                answer += b * total[node] + c * (end - start)
                continue
            middle = start + end >> 1
            if middle < right:
                stack.append((rc[node], b * rb[node] % mod, (b * ra[node] + c) % mod, middle, end))
            if left < middle:
                stack.append((lc[node], b * lb[node] % mod, (b * la[node] + c) % mod, start, middle))
        return answer % mod

    def get(self, index, version=-1):
        """指定版のindex番目の値を返す。"""
        return self.prod(index, index + 1, version)

    def tolist(self, version=-1):
        """指定版の全要素を添字順の新しいlistとして返す。"""
        (root, b, c) = self.roots[version]
        stack = [(root, b, c, 0, self.size)]
        result = [0] * self.n
        mod = self.mod
        while stack:
            (node, b, c, start, end) = stack.pop()
            if start >= self.n:
                continue
            if end - start == 1:
                result[start] = (b * self._sum[node] + c) % mod
                continue
            middle = start + end >> 1
            stack.append((self._right[node], b * self._rb[node] % mod, (b * self._rc[node] + c) % mod, middle, end))
            stack.append((self._left[node], b * self._lb[node] % mod, (b * self._lc[node] + c) % mod, start, middle))
        return result

    def __len__(self):
        return self.n

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return f'PersistentRangeAffineRangeSum({self.tolist()}, mod={self.mod})'
import sys
input = sys.stdin.buffer.readline
(n, q) = map(int, input().split())
tree = PersistentRangeAffineRangeSum(map(int, input().split()))
versions = [0] * (q + 1)
answer = []
for i in range(q):
    query = list(map(int, input().split()))
    (kind, k) = query[:2]
    if kind == 0:
        (_, _, left, right, b, c) = query
        versions[i + 1] = tree.apply(left, right, b, c, versions[k + 1])
    elif kind == 1:
        (_, _, source, left, right) = query
        versions[i + 1] = tree.copy(left, right, versions[source + 1], versions[k + 1])
    else:
        (_, _, left, right) = query
        answer.append(str(tree.prod(left, right, versions[k + 1])))
sys.stdout.write('\n'.join(answer))
