"""更新のない配列の半開区間ごとに、順序が逆になった要素の組数を求める。

Adapted from yosupo06/library-checker-problems, revision
1814c4e5205517e368bb57a8d1127eb961cfeaae,
data_structure/static_range_inversions_query/sol/correct.cpp.
Changes: Python implementation, packed counts, configurable block width,
range validation, empty input support and logical debug output.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy at https://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from array import array
from math import isqrt


class StaticRangeInversions:
    """前計算した配列に対して、区間内の転倒数をO(sqrt(N))で答える。"""

    __slots__ = ("n", "block_size", "_values", "_ranks", "_order", "_prefix", "_blocks", "_freq")

    def __init__(self, values, block_size=None):
        values = list(values)
        n = len(values)
        if block_size is None:
            block_size = isqrt(n) + 1
        if block_size <= 0:
            raise ValueError("block_size must be positive")
        width = min(block_size, max(1, n))
        rank = [0] * n
        for value, index in enumerate(sorted(range(n), key=values.__getitem__)):
            rank[index] = value
        count = n // width + 1
        ranks = [rank[i * width:(i + 1) * width] for i in range(count)]
        order = [sorted(range(len(row)), key=row.__getitem__) for row in ranks]
        sorted_rows = [[row[i] for i in indices] for row, indices in zip(ranks, order)]
        prefix = []
        blocks = [[] for _ in range(count)]
        frequencies = []
        seen = [0] * n
        typecode = "I" if n <= 0xffffffff else "Q"
        for r in range(count):
            row = ranks[r]
            freq = array(typecode, [0]) * (n + 1)
            total = 0
            for i in range(n):
                total += seen[i]
                freq[i + 1] = total
            frequencies.append(freq)
            for value in row:
                seen[value] = 1
            inv = 0
            local = [0]
            for i in range(len(row)):
                value = row[i]
                for j in range(i):
                    inv += row[j] > value
                local.append(inv)
            prefix.append(local)
            if r + 1 == count:
                continue
            whole = [0] * (r + 1)
            whole[r] = inv
            current = sorted_rows[r]
            size = len(current)
            previous = blocks[r]
            for l in range(r - 1, -1, -1):
                j = 0
                for value in sorted_rows[l]:
                    while j < size and current[j] < value:
                        j += 1
                    inv += j
                whole[l] = previous[l] + inv
            blocks[r + 1] = whole
        self.n = n
        self.block_size = width
        self._values = values
        self._ranks = ranks
        self._order = order
        self._prefix = prefix
        self._blocks = blocks
        self._freq = frequencies

    def query(self, left, right):
        """半開区間[left, right)のi<jかつa[i]>a[j]となる組数を返す。"""
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        if right - left < 2:
            return 0
        width = self.block_size
        fq, fr = divmod(left, width)
        lq, lr = divmod(right, width)
        fp = self._prefix[fq]
        fo = self._order[fq]
        if fq == lq:
            result = fp[lr] - fp[fr]
            total = 0
            for index in fo:
                if index < fr:
                    result -= total
                elif index < lr:
                    total += 1
            return result
        fa = self._ranks[fq]
        la = self._ranks[lq]
        ff = self._freq[fq]
        lf = self._freq[lq]
        result = self._blocks[lq][fq] + fr * (fr - 1) // 2 - fp[fr]
        for i in range(fr):
            value = fa[i]
            result -= lf[value] - ff[value]
        result += self._prefix[lq][lr] + (lq - fq) * width * lr
        for i in range(lr):
            value = la[i]
            result -= lf[value] - ff[value]
        lo = self._order[lq]
        j = 0
        total = 0
        size = len(lo)
        for i in fo:
            value = fa[i]
            while j < size and la[lo[j]] < value:
                total += lo[j] < lr
                j += 1
            if i < fr:
                result -= total
        return result

    def tolist(self):
        """前計算した元の配列を添字順の新しいlistで返す。"""
        return self._values[:]

    def __len__(self):
        return self.n

    def __str__(self):
        return str(self._values)

    def __repr__(self):
        return "StaticRangeInversions(%r)" % self._values
