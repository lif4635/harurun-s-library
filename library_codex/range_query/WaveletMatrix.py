_MASK = [(1 << i) - 1 for i in range(64)]


class WaveletMatrix:
    __slots__ = ("n", "log", "mid", "blocks", "prefix")

    def __init__(self, a):
        n = len(a)
        if n:
            assert min(a) >= 0
            log = max(1, max(a).bit_length())
        else:
            log = 1

        mid = [0] * log
        blocks = [None] * log
        prefix = [None] * log
        cur = list(a)
        block_count = (n >> 6) + 1

        for h in range(log - 1, -1, -1):
            block = [0] * block_count
            zero = []
            one = []
            bit = 1 << h
            for i, x in enumerate(cur):
                if x & bit:
                    block[i >> 6] |= 1 << (i & 63)
                    one.append(x)
                else:
                    zero.append(x)

            pref = [0] * (block_count + 1)
            for i, x in enumerate(block):
                pref[i + 1] = pref[i] + x.bit_count()

            mid[h] = len(zero)
            blocks[h] = block
            prefix[h] = pref
            cur = zero + one

        self.n = n
        self.log = log
        self.mid = mid
        self.blocks = blocks
        self.prefix = prefix

    def access(self, k):
        assert 0 <= k < self.n
        res = 0
        mask = _MASK
        blocks = self.blocks
        prefix = self.prefix
        mid = self.mid
        for h in range(self.log - 1, -1, -1):
            block = blocks[h]
            b = k >> 6
            o = k & 63
            ones = prefix[h][b] + (block[b] & mask[o]).bit_count()
            if block[b] >> o & 1:
                res |= 1 << h
                k = mid[h] + ones
            else:
                k -= ones
        return res

    __getitem__ = access

    def rank(self, l, r, x):
        assert 0 <= l <= r <= self.n
        if x < 0 or x >= 1 << self.log:
            return 0
        mask = _MASK
        blocks = self.blocks
        prefix = self.prefix
        mid = self.mid
        for h in range(self.log - 1, -1, -1):
            block = blocks[h]
            pref = prefix[h]
            lb = l >> 6
            rb = r >> 6
            lo = l & 63
            ro = r & 63
            l1 = pref[lb] + (block[lb] & mask[lo]).bit_count()
            r1 = pref[rb] + (block[rb] & mask[ro]).bit_count()
            if x >> h & 1:
                l = mid[h] + l1
                r = mid[h] + r1
            else:
                l -= l1
                r -= r1
        return r - l

    count = rank

    def kth_smallest(self, l, r, k):
        assert 0 <= l <= r <= self.n and 0 <= k < r - l
        res = 0
        mask = _MASK
        blocks = self.blocks
        prefix = self.prefix
        mid = self.mid
        for h in range(self.log - 1, -1, -1):
            block = blocks[h]
            pref = prefix[h]
            lb = l >> 6
            rb = r >> 6
            lo = l & 63
            ro = r & 63
            l1 = pref[lb] + (block[lb] & mask[lo]).bit_count()
            r1 = pref[rb] + (block[rb] & mask[ro]).bit_count()
            zeros = r - l - r1 + l1
            if k < zeros:
                l -= l1
                r -= r1
            else:
                k -= zeros
                res |= 1 << h
                l = mid[h] + l1
                r = mid[h] + r1
        return res

    quantile = kth_smallest

    def kth_largest(self, l, r, k):
        assert 0 <= k < r - l
        return self.kth_smallest(l, r, r - l - k - 1)

    def count_lt(self, l, r, upper):
        assert 0 <= l <= r <= self.n
        if upper <= 0:
            return 0
        if upper >= 1 << self.log:
            return r - l
        res = 0
        mask = _MASK
        blocks = self.blocks
        prefix = self.prefix
        mid = self.mid
        for h in range(self.log - 1, -1, -1):
            block = blocks[h]
            pref = prefix[h]
            lb = l >> 6
            rb = r >> 6
            lo = l & 63
            ro = r & 63
            l1 = pref[lb] + (block[lb] & mask[lo]).bit_count()
            r1 = pref[rb] + (block[rb] & mask[ro]).bit_count()
            if upper >> h & 1:
                res += r - l - r1 + l1
                l = mid[h] + l1
                r = mid[h] + r1
            else:
                l -= l1
                r -= r1
        return res

    range_lowerbound = count_lt

    def count_le(self, l, r, upper):
        return self.count_lt(l, r, upper + 1)

    range_upperbound = count_le

    def range_freq(self, l, r, lower, upper=None):
        if upper is None:
            return self.count_lt(l, r, lower)
        return self.count_lt(l, r, upper) - self.count_lt(l, r, lower)

    def prev_value(self, l, r, upper, default=-1):
        k = self.count_lt(l, r, upper)
        return default if k == 0 else self.kth_smallest(l, r, k - 1)

    def next_value(self, l, r, lower, default=-1):
        k = self.count_lt(l, r, lower)
        return default if k == r - l else self.kth_smallest(l, r, k)

    def max_le(self, l, r, x, default=-1):
        k = self.count_le(l, r, x)
        return default if k == 0 else self.kth_smallest(l, r, k - 1)

    def min_ge(self, l, r, x, default=-1):
        return self.next_value(l, r, x, default)
