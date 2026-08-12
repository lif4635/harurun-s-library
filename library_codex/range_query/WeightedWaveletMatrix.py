"""静的な列で値域を絞った重み和とk個の最小・最大要素の重み和を求める。"""

from bisect import bisect_left


_MASK = [(1 << index) - 1 for index in range(64)]


class WeightedWaveletMatrix:
    """Wavelet Matrixの各levelに重みprefix sumを持たせた構造。"""

    __slots__ = (
        "n", "values", "log", "mid", "blocks", "bit_prefix",
        "weight_prefix", "leaf_prefix", "original_prefix",
    )

    def __init__(self, values, weights=None):
        values = list(values)
        n = len(values)
        if weights is None:
            weights = values
        else:
            weights = list(weights)
            if len(weights) != n:
                raise ValueError("values and weights must have the same length")

        ordered = sorted(set(values))
        rank = {value: index for index, value in enumerate(ordered)}
        current_values = [rank[value] for value in values]
        current_weights = list(weights)
        sigma = len(ordered)
        log = max(1, (sigma - 1).bit_length())
        mid = [0] * log
        blocks = [None] * log
        bit_prefix = [None] * log
        weight_prefix = [None] * log
        block_count = (n >> 6) + 1

        original_prefix = [0] * (n + 1)
        for index, weight in enumerate(weights):
            original_prefix[index + 1] = original_prefix[index] + weight

        for height in range(log - 1, -1, -1):
            bit = 1 << height
            block = [0] * block_count
            zero_values = []
            one_values = []
            zero_weights = []
            one_weights = []
            for index, (value, weight) in enumerate(
                zip(current_values, current_weights)
            ):
                if value & bit:
                    block[index >> 6] |= 1 << (index & 63)
                    one_values.append(value)
                    one_weights.append(weight)
                else:
                    zero_values.append(value)
                    zero_weights.append(weight)

            prefix = [0] * (block_count + 1)
            for index, bits in enumerate(block):
                prefix[index + 1] = prefix[index] + bits.bit_count()
            current_values = zero_values + one_values
            current_weights = zero_weights + one_weights
            sums = [0] * (n + 1)
            for index, weight in enumerate(current_weights):
                sums[index + 1] = sums[index] + weight
            mid[height] = len(zero_values)
            blocks[height] = block
            bit_prefix[height] = prefix
            weight_prefix[height] = sums

        leaf_prefix = [0] * (n + 1)
        for index, weight in enumerate(current_weights):
            leaf_prefix[index + 1] = leaf_prefix[index] + weight

        self.n = n
        self.values = ordered
        self.log = log
        self.mid = mid
        self.blocks = blocks
        self.bit_prefix = bit_prefix
        self.weight_prefix = weight_prefix
        self.leaf_prefix = leaf_prefix
        self.original_prefix = original_prefix

    def _ones_before(self, height, index):
        block_index = index >> 6
        offset = index & 63
        return (
            self.bit_prefix[height][block_index]
            + (self.blocks[height][block_index] & _MASK[offset]).bit_count()
        )

    def total(self, left, right):
        """半開区間の全要素の重み和を返す。"""
        if not 0 <= left <= right <= self.n:
            raise IndexError("range is outside the sequence")
        return self.original_prefix[right] - self.original_prefix[left]

    def sum_lt(self, left, right, upper):
        """値が ``upper`` 未満の要素だけの重み和を返す。"""
        if not 0 <= left <= right <= self.n:
            raise IndexError("range is outside the sequence")
        limit = bisect_left(self.values, upper)
        if limit == 0:
            return 0
        if limit == len(self.values):
            return self.total(left, right)
        result = 0
        for height in range(self.log - 1, -1, -1):
            left_one = self._ones_before(height, left)
            right_one = self._ones_before(height, right)
            left_zero = left - left_one
            right_zero = right - right_one
            if limit >> height & 1:
                prefix = self.weight_prefix[height]
                result += prefix[right_zero] - prefix[left_zero]
                left = self.mid[height] + left_one
                right = self.mid[height] + right_one
            else:
                left = left_zero
                right = right_zero
        return result

    def range_sum(self, left, right, lower, upper):
        """位置と値の両方が指定した半開区間に入る要素の重み和を返す。"""
        return self.sum_lt(left, right, upper) - self.sum_lt(
            left, right, lower
        )

    def sum_k_smallest(self, left, right, k):
        """位置区間にある値の小さい方からk個を選んだ重み和を返す。"""
        if not 0 <= left <= right <= self.n:
            raise IndexError("range is outside the sequence")
        if not 0 <= k <= right - left:
            raise IndexError("k is outside the range length")
        result = 0
        for height in range(self.log - 1, -1, -1):
            left_one = self._ones_before(height, left)
            right_one = self._ones_before(height, right)
            left_zero = left - left_one
            right_zero = right - right_one
            zeros = right_zero - left_zero
            if k < zeros:
                left = left_zero
                right = right_zero
            else:
                prefix = self.weight_prefix[height]
                result += prefix[right_zero] - prefix[left_zero]
                k -= zeros
                left = self.mid[height] + left_one
                right = self.mid[height] + right_one
        if k:
            result += self.leaf_prefix[left + k] - self.leaf_prefix[left]
        return result

    def sum_k_largest(self, left, right, k):
        """位置区間にある値の大きい方からk個を選んだ重み和を返す。"""
        if not 0 <= left <= right <= self.n:
            raise IndexError("range is outside the sequence")
        if not 0 <= k <= right - left:
            raise IndexError("k is outside the range length")
        return self.total(left, right) - self.sum_k_smallest(
            left, right, right - left - k
        )

