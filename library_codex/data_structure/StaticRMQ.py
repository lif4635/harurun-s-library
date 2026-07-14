class StaticRMQ:
    __slots__ = (
        "n", "block_size", "block_shift", "block_mask", "values", "masks",
        "prefix_min", "suffix_min", "table"
    )

    def __init__(self, values):
        values = list(values)
        n = len(values)
        logn = max(1, n.bit_length())
        block_size = 1 << (logn - 1).bit_length()
        block_shift = block_size.bit_length() - 1
        masks = [0] * n
        prefix_min = [0] * n
        suffix_min = [0] * n
        block_min = []

        for left in range(0, n, block_size):
            right = min(left + block_size, n)
            mask = 0
            best = left
            for i in range(left, right):
                x = values[i]
                while mask:
                    top = mask.bit_length() - 1
                    if values[left + top] <= x:
                        break
                    mask ^= 1 << top
                mask |= 1 << (i - left)
                masks[i] = mask
                if values[i] < values[best]:
                    best = i
                prefix_min[i] = best
            block_min.append(best)
            best = right - 1
            for i in range(right - 1, left - 1, -1):
                if values[i] <= values[best]:
                    best = i
                suffix_min[i] = best

        table = []
        if block_min:
            table.append(block_min)
            width = 2
            while width <= len(block_min):
                half = width >> 1
                prev = table[-1]
                cur = [0] * (len(block_min) - width + 1)
                for i in range(len(cur)):
                    x = prev[i]
                    y = prev[i + half]
                    cur[i] = x if values[x] <= values[y] else y
                table.append(cur)
                width <<= 1

        self.n = n
        self.block_size = block_size
        self.block_shift = block_shift
        self.block_mask = block_size - 1
        self.values = values
        self.masks = masks
        self.prefix_min = prefix_min
        self.suffix_min = suffix_min
        self.table = table

    def _small_argmin(self, l, r):
        base = l >> self.block_shift << self.block_shift
        mask = self.masks[r - 1] & ~((1 << (l & self.block_mask)) - 1)
        return base + ((mask & -mask).bit_length() - 1)

    def argmin(self, l, r):
        assert 0 <= l < r <= self.n
        shift = self.block_shift
        left_block = l >> shift
        right_block = (r - 1) >> shift
        if left_block == right_block:
            return self._small_argmin(l, r)

        best = self.suffix_min[l]

        first = left_block + 1
        last = right_block
        if first < last:
            level = (last - first).bit_length() - 1
            width = 1 << level
            table = self.table[level]
            x = table[first]
            y = table[last - width]
            middle = x if self.values[x] <= self.values[y] else y
            if self.values[middle] < self.values[best]:
                best = middle

        right = self.prefix_min[r - 1]
        if self.values[right] < self.values[best]:
            best = right
        return best

    def query(self, l, r):
        return self.values[self.argmin(l, r)]

    prod = query

    def __len__(self):
        return self.n
