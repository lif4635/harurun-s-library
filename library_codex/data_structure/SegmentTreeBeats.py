INF = float("inf")


class SegmentTreeBeats:
    __slots__ = (
        "n", "size", "log", "sum", "max1", "max2", "maxc",
        "min1", "min2", "minc", "add", "lazy_set"
    )

    def __init__(self, a):
        n = len(a)
        size = 1 << (n - 1).bit_length() if n else 1
        m = size << 1
        total = [0] * m
        max1 = [0] * m
        max2 = [-INF] * m
        maxc = [1] * m
        min1 = [0] * m
        min2 = [INF] * m
        minc = [1] * m
        total[size:size + n] = a
        max1[size:size + n] = a
        min1[size:size + n] = a

        self.n = n
        self.size = size
        self.log = size.bit_length() - 1
        self.sum = total
        self.max1 = max1
        self.max2 = max2
        self.maxc = maxc
        self.min1 = min1
        self.min2 = min2
        self.minc = minc
        self.add = [0] * size
        self.lazy_set = [None] * size

        for k in range(size - 1, 0, -1):
            self._pull(k)

    def _pull(self, k):
        lc = k << 1
        rc = lc | 1
        total = self.sum
        max1 = self.max1
        max2 = self.max2
        maxc = self.maxc
        min1 = self.min1
        min2 = self.min2
        minc = self.minc
        total[k] = total[lc] + total[rc]

        if max1[lc] == max1[rc]:
            max1[k] = max1[lc]
            max2[k] = max(max2[lc], max2[rc])
            maxc[k] = maxc[lc] + maxc[rc]
        elif max1[lc] > max1[rc]:
            max1[k] = max1[lc]
            max2[k] = max(max2[lc], max1[rc])
            maxc[k] = maxc[lc]
        else:
            max1[k] = max1[rc]
            max2[k] = max(max1[lc], max2[rc])
            maxc[k] = maxc[rc]

        if min1[lc] == min1[rc]:
            min1[k] = min1[lc]
            min2[k] = min(min2[lc], min2[rc])
            minc[k] = minc[lc] + minc[rc]
        elif min1[lc] < min1[rc]:
            min1[k] = min1[lc]
            min2[k] = min(min2[lc], min1[rc])
            minc[k] = minc[lc]
        else:
            min1[k] = min1[rc]
            min2[k] = min(min1[lc], min2[rc])
            minc[k] = minc[rc]

    def _apply_add(self, k, x):
        length = 1 << (self.log - (k.bit_length() - 1))
        self.sum[k] += x * length
        self.max1[k] += x
        self.min1[k] += x
        if self.max2[k] != -INF:
            self.max2[k] += x
        if self.min2[k] != INF:
            self.min2[k] += x
        if k < self.size:
            if self.lazy_set[k] is None:
                self.add[k] += x
            else:
                self.lazy_set[k] += x

    def _apply_set(self, k, x):
        length = 1 << (self.log - (k.bit_length() - 1))
        self.sum[k] = x * length
        self.max1[k] = x
        self.max2[k] = -INF
        self.maxc[k] = length
        self.min1[k] = x
        self.min2[k] = INF
        self.minc[k] = length
        if k < self.size:
            self.add[k] = 0
            self.lazy_set[k] = x

    def _apply_chmin(self, k, x):
        old = self.max1[k]
        self.sum[k] += (x - old) * self.maxc[k]
        if self.min1[k] == old:
            self.min1[k] = x
        elif self.min2[k] == old:
            self.min2[k] = x
        self.max1[k] = x

    def _apply_chmax(self, k, x):
        old = self.min1[k]
        self.sum[k] += (x - old) * self.minc[k]
        if self.max1[k] == old:
            self.max1[k] = x
        elif self.max2[k] == old:
            self.max2[k] = x
        self.min1[k] = x

    def _push(self, k):
        if k >= self.size:
            return
        lc = k << 1
        rc = lc | 1
        lazy_set = self.lazy_set[k]
        if lazy_set is not None:
            self._apply_set(lc, lazy_set)
            self._apply_set(rc, lazy_set)
            self.lazy_set[k] = None
        add = self.add[k]
        if add:
            self._apply_add(lc, add)
            self._apply_add(rc, add)
            self.add[k] = 0
        upper = self.max1[k]
        if self.max1[lc] > upper:
            self._apply_chmin(lc, upper)
        if self.max1[rc] > upper:
            self._apply_chmin(rc, upper)
        lower = self.min1[k]
        if self.min1[lc] < lower:
            self._apply_chmax(lc, lower)
        if self.min1[rc] < lower:
            self._apply_chmax(rc, lower)

    def _subtree_chmin(self, root, x):
        stack = [root]
        max1 = self.max1
        max2 = self.max2
        while stack:
            k = stack.pop()
            if k < 0:
                self._pull(~k)
            elif max1[k] <= x:
                continue
            elif max2[k] < x:
                self._apply_chmin(k, x)
            else:
                self._push(k)
                stack.append(~k)
                stack.append(k << 1 | 1)
                stack.append(k << 1)

    def _subtree_chmax(self, root, x):
        stack = [root]
        min1 = self.min1
        min2 = self.min2
        while stack:
            k = stack.pop()
            if k < 0:
                self._pull(~k)
            elif x <= min1[k]:
                continue
            elif x < min2[k]:
                self._apply_chmax(k, x)
            else:
                self._push(k)
                stack.append(~k)
                stack.append(k << 1 | 1)
                stack.append(k << 1)

    def _range_apply(self, l, r, x, cmd):
        assert 0 <= l <= r <= self.n
        if l == r:
            return
        size = self.size
        left = l + size
        right = r + size
        for h in range(self.log, 0, -1):
            if left >> h << h != left:
                self._push(left >> h)
            if right >> h << h != right:
                self._push((right - 1) >> h)

        l0 = left
        r0 = right
        while left < right:
            if left & 1:
                if cmd == 0:
                    self._subtree_chmin(left, x)
                elif cmd == 1:
                    self._subtree_chmax(left, x)
                elif cmd == 2:
                    self._apply_add(left, x)
                else:
                    self._apply_set(left, x)
                left += 1
            if right & 1:
                right -= 1
                if cmd == 0:
                    self._subtree_chmin(right, x)
                elif cmd == 1:
                    self._subtree_chmax(right, x)
                elif cmd == 2:
                    self._apply_add(right, x)
                else:
                    self._apply_set(right, x)
            left >>= 1
            right >>= 1

        for h in range(1, self.log + 1):
            if l0 >> h << h != l0:
                self._pull(l0 >> h)
            if r0 >> h << h != r0:
                self._pull((r0 - 1) >> h)

    def range_chmin(self, l, r, x):
        self._range_apply(l, r, x, 0)

    def range_chmax(self, l, r, x):
        self._range_apply(l, r, x, 1)

    def range_add(self, l, r, x):
        self._range_apply(l, r, x, 2)

    def range_update(self, l, r, x):
        self._range_apply(l, r, x, 3)

    range_assign = range_update

    def _range_query(self, l, r, cmd):
        assert 0 <= l <= r <= self.n
        if l == r:
            return 0 if cmd == 0 else (INF if cmd == 1 else -INF)
        left = l + self.size
        right = r + self.size
        for h in range(self.log, 0, -1):
            if left >> h << h != left:
                self._push(left >> h)
            if right >> h << h != right:
                self._push((right - 1) >> h)

        if cmd == 0:
            res = 0
            data = self.sum
            while left < right:
                if left & 1:
                    res += data[left]
                    left += 1
                if right & 1:
                    right -= 1
                    res += data[right]
                left >>= 1
                right >>= 1
            return res
        if cmd == 1:
            res = INF
            data = self.min1
            while left < right:
                if left & 1:
                    res = min(res, data[left])
                    left += 1
                if right & 1:
                    right -= 1
                    res = min(res, data[right])
                left >>= 1
                right >>= 1
            return res
        res = -INF
        data = self.max1
        while left < right:
            if left & 1:
                res = max(res, data[left])
                left += 1
            if right & 1:
                right -= 1
                res = max(res, data[right])
            left >>= 1
            right >>= 1
        return res

    def range_sum(self, l, r):
        return self._range_query(l, r, 0)

    def range_min(self, l, r):
        return self._range_query(l, r, 1)

    def range_max(self, l, r):
        return self._range_query(l, r, 2)

    query_sum = range_sum
    query_min = range_min
    query_max = range_max

    def get(self, p):
        assert 0 <= p < self.n
        k = p + self.size
        for h in range(self.log, 0, -1):
            self._push(k >> h)
        return self.sum[k]

    def set(self, p, x):
        assert 0 <= p < self.n
        self.range_update(p, p + 1, x)

    def all_sum(self):
        return self.sum[1]

    def all_min(self):
        return self.range_min(0, self.n)

    def all_max(self):
        return self.range_max(0, self.n)
