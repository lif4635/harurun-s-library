from heapq import _heappop_max, _siftdown_max, _heapify_max

class frac:
    __slots__ = ["p", "q", "idx"]
    def __init__(self, p, q, idx = -1):
        self.p = p
        self.q = q
        self.idx = idx
    def __eq__(self, other):
        return self.p * other.q == other.p * self.q
    def __ne__(self, other):
        return self.p * other.q != other.p * self.q
    def __lt__(self, other):
        return self.p * other.q < other.p * self.q
    def __le__(self, other):
        return self.p * other.q <= other.p * self.q
    def __gt__(self, other):
        return self.p * other.q > other.p * self.q
    def __gt__(self, other):
        return self.p * other.q >= other.p * self.q

def o1_on_tree(par, c0, c1):
    """
    各頂点に 0 * c0 + 1 * c1 があり
    トポロジカルソート順に並べた時の転倒数の最小値
    """
    ans = 0
    heap = []
    for i in range(1, n):
        heap.append(frac(c0[i], c1[i], i))
    _heapify_max(heap)
    uf = [i for i in range(n)]
    while heap:
        f = _heappop_max(heap)
        v = f.idx
        if f.p != c0[v] or f.q != c1[v]:
            continue
        
        p = par[v]
        while uf[p] != p:
            uf[p] = p = uf[uf[p]]
        uf[v] = p
        
        ans += c1[p] * c0[v]
        c0[p] += c0[v]
        c1[p] += c1[v]
        if p != 0:
            heap.append(frac(c0[p], c1[p], p))
            _siftdown_max(heap, 0, len(heap) - 1)
    return ans