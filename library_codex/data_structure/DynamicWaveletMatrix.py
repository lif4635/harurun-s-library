"""Dynamic range order statistics for positive integer sequences.

The module offers three deliberately different execution models:

``DynamicWaveletMatrix``
    Fully online.  Update values do not need to be known in advance.

``CompressedDynamicWaveletMatrix``
    Fully online after construction, but every possible ``(index, value)``
    update must be declared up front.  This is normally the fastest immediate
    backend and is a genuine static wavelet matrix over candidate positions.

``OfflineDynamicWaveletMatrix``
    Records operations and answers them together in ``solve()``.  Use it when
    only batch answers are needed and the tightest limits matter.

Indices are zero based and ranges are half open.  Sequence values must satisfy
``1 <= value < 2**64``.  Query bounds and targets may be any integer.
"""

from __future__ import annotations

from array import array
from bisect import bisect_left
from operator import index as operator_index
from typing import Any, Iterable, Iterator, Sequence


__all__ = (
    "DynamicWaveletMatrix",
    "CompressedDynamicWaveletMatrix",
    "OfflineDynamicWaveletMatrix",
    "dynamic_range_min_count_sum_at_least",
    "solve_dynamic_wavelet_matrix_queries",
)


_I32_LIMIT = 1 << 31
_I64_LIMIT = 1 << 63
_U64_LIMIT = 1 << 64


def _integer(value: Any, name: str) -> int:
    """Return an integer-like value as ``int``, rejecting booleans."""
    if type(value) is int:
        return value
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    try:
        return operator_index(value)
    except TypeError:
        raise TypeError(f"{name} must be an integer") from None


def _positive_integer(value: Any, name: str = "value") -> int:
    value = _integer(value, name)
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    if value >= _U64_LIMIT:
        raise OverflowError(f"{name} must fit in 64 bits")
    return value


def _sequence(values: Iterable[int]) -> list[int]:
    result = [_positive_integer(value) for value in values]
    if len(result) >= _I32_LIMIT:
        raise OverflowError("the sequence is too large for this implementation")
    return result


def _normalize_index(index: Any, size: int) -> int:
    index = _integer(index, "index")
    if not 0 <= index < size:
        raise IndexError("index out of range")
    return index


def _normalize_range(left: Any, right: Any, size: int) -> tuple[int, int]:
    left = _integer(left, "left")
    right = _integer(right, "right")
    if not 0 <= left <= right <= size:
        raise IndexError("range must satisfy 0 <= left <= right <= n")
    return left, right


def _normalize_k(k: Any, length: int, *, inclusive: bool) -> int:
    k = _integer(k, "k")
    valid = 0 <= k <= length if inclusive else 0 <= k < length
    if not valid:
        relation = "<=" if inclusive else "<"
        raise IndexError(f"k must satisfy 0 <= k {relation} right-left")
    return k


class _ImmediateQueries:
    """Backend-independent immediate range-query implementation.

    A backend supplies a root state, a binary partition operation, and a way
    to encode/decode values.  Keeping the traversal here makes the two online
    implementations agree on validation and edge cases.
    """

    n: int
    _levels: int
    _domain_size: int

    def _make_state(self, left: int, right: int) -> Any:
        raise NotImplementedError

    def _split_state(self, state: Any, level: int) -> tuple[Any, Any]:
        raise NotImplementedError

    def _state_pair(self, state: Any, level: int) -> tuple[int, int]:
        """Return ``(active count, active sum)`` for a traversal state."""
        raise NotImplementedError

    def _range_total(self, left: int, right: int) -> int:
        raise NotImplementedError

    def _encode_bound(self, upper: int) -> int:
        raise NotImplementedError

    def _decode_value(self, code: int) -> int:
        raise NotImplementedError

    def __len__(self) -> int:
        return self.n

    def __iter__(self) -> Iterator[int]:
        return iter(self._values)

    def tolist(self) -> list[int]:
        """Return a copy of the current sequence."""
        return self._values[:]

    def __str__(self) -> str:
        return str(self.tolist())

    def __repr__(self) -> str:
        return "%s(%r)" % (type(self).__name__, self.tolist())

    def _count_lt_checked(self, left: int, right: int, upper: int) -> int:
        if left == right:
            return 0
        code = self._encode_bound(upper)
        if code <= 0:
            return 0
        if code >= self._domain_size:
            return right - left

        state = self._make_state(left, right)
        result = 0
        for level in range(self._levels):
            zero, one = self._split_state(state, level)
            bit = 1 << (self._levels - level - 1)
            if code & bit:
                zero_count, _ = self._state_pair(zero, level + 1)
                result += zero_count
                state = one
            else:
                state = zero
        return result

    def _sum_lt_checked(self, left: int, right: int, upper: int) -> int:
        if left == right:
            return 0
        code = self._encode_bound(upper)
        if code <= 0:
            return 0
        if code >= self._domain_size:
            return self._range_total(left, right)

        state = self._make_state(left, right)
        result = 0
        for level in range(self._levels):
            zero, one = self._split_state(state, level)
            bit = 1 << (self._levels - level - 1)
            if code & bit:
                _, zero_sum = self._state_pair(zero, level + 1)
                result += zero_sum
                state = one
            else:
                state = zero
        return result

    def _kth_checked(self, left: int, right: int, k: int) -> int:
        state = self._make_state(left, right)
        code = 0
        for level in range(self._levels):
            zero, one = self._split_state(state, level)
            zero_count, _ = self._state_pair(zero, level + 1)
            if k < zero_count:
                state = zero
            else:
                k -= zero_count
                code |= 1 << (self._levels - level - 1)
                state = one
        return self._decode_value(code)

    def range_sum(self, left: Any, right: Any) -> int:
        """Return ``sum(A[left:right])``."""
        left, right = _normalize_range(left, right, self.n)
        return self._range_total(left, right)

    sum = range_sum

    def count_lt(self, left: Any, right: Any, upper: Any) -> int:
        """Count values smaller than ``upper`` in ``A[left:right]``."""
        left, right = _normalize_range(left, right, self.n)
        upper = _integer(upper, "upper")
        return self._count_lt_checked(left, right, upper)

    range_lowerbound = count_lt

    def count_le(self, left: Any, right: Any, upper: Any) -> int:
        """Count values at most ``upper`` in ``A[left:right]``."""
        left, right = _normalize_range(left, right, self.n)
        upper = _integer(upper, "upper")
        return self._count_lt_checked(left, right, upper + 1)

    range_upperbound = count_le

    def rank(self, left: Any, right: Any, value: Any) -> int:
        """Count occurrences of ``value`` in ``A[left:right]``."""
        left, right = _normalize_range(left, right, self.n)
        value = _integer(value, "value")
        return self._count_lt_checked(
            left, right, value + 1
        ) - self._count_lt_checked(left, right, value)

    count = rank

    def range_freq(
        self, left: Any, right: Any, lower: Any, upper: Any | None = None
    ) -> int:
        """Count values below ``lower``, or values in ``[lower, upper)``."""
        left, right = _normalize_range(left, right, self.n)
        lower = _integer(lower, "lower")
        if upper is None:
            return self._count_lt_checked(left, right, lower)
        upper = _integer(upper, "upper")
        if lower >= upper:
            return 0
        return self._count_lt_checked(
            left, right, upper
        ) - self._count_lt_checked(left, right, lower)

    def sum_lt(self, left: Any, right: Any, upper: Any) -> int:
        """Sum values smaller than ``upper`` in ``A[left:right]``."""
        left, right = _normalize_range(left, right, self.n)
        upper = _integer(upper, "upper")
        return self._sum_lt_checked(left, right, upper)

    def sum_le(self, left: Any, right: Any, upper: Any) -> int:
        """Sum values at most ``upper`` in ``A[left:right]``."""
        left, right = _normalize_range(left, right, self.n)
        upper = _integer(upper, "upper")
        return self._sum_lt_checked(left, right, upper + 1)

    def sum_range(
        self, left: Any, right: Any, lower: Any, upper: Any | None = None
    ) -> int:
        """Sum values below ``lower``, or values in ``[lower, upper)``."""
        left, right = _normalize_range(left, right, self.n)
        lower = _integer(lower, "lower")
        if upper is None:
            return self._sum_lt_checked(left, right, lower)
        upper = _integer(upper, "upper")
        if lower >= upper:
            return 0
        return self._sum_lt_checked(
            left, right, upper
        ) - self._sum_lt_checked(left, right, lower)

    def kth_smallest(self, left: Any, right: Any, k: Any) -> int:
        """Return the zero-indexed k-th smallest value in the range."""
        left, right = _normalize_range(left, right, self.n)
        k = _normalize_k(k, right - left, inclusive=False)
        return self._kth_checked(left, right, k)

    quantile = kth_smallest

    def kth_largest(self, left: Any, right: Any, k: Any) -> int:
        """Return the zero-indexed k-th largest value in the range."""
        left, right = _normalize_range(left, right, self.n)
        k = _normalize_k(k, right - left, inclusive=False)
        return self._kth_checked(left, right, right - left - k - 1)

    def sum_k_smallest(self, left: Any, right: Any, k: Any) -> int:
        """Return the sum of the ``k`` smallest values in the range."""
        left, right = _normalize_range(left, right, self.n)
        k = _normalize_k(k, right - left, inclusive=True)
        if k == 0:
            return 0

        state = self._make_state(left, right)
        result = code = 0
        for level in range(self._levels):
            zero, one = self._split_state(state, level)
            zero_count, zero_sum = self._state_pair(zero, level + 1)
            if k <= zero_count:
                state = zero
            else:
                result += zero_sum
                k -= zero_count
                code |= 1 << (self._levels - level - 1)
                state = one
        return result + k * self._decode_value(code)

    def sum_k_largest(self, left: Any, right: Any, k: Any) -> int:
        """Return the sum of the ``k`` largest values in the range."""
        left, right = _normalize_range(left, right, self.n)
        k = _normalize_k(k, right - left, inclusive=True)
        if k == 0:
            return 0

        state = self._make_state(left, right)
        result = code = 0
        for level in range(self._levels):
            zero, one = self._split_state(state, level)
            one_count, one_sum = self._state_pair(one, level + 1)
            if k <= one_count:
                code |= 1 << (self._levels - level - 1)
                state = one
            else:
                result += one_sum
                k -= one_count
                state = zero
        return result + k * self._decode_value(code)

    def min_count_sum_at_least(
        self, left: Any, right: Any, target: Any
    ) -> int:
        """Minimum count whose largest-value sum reaches ``target``.

        Return zero for a non-positive target and ``-1`` if the entire range
        sum is too small.
        """
        left, right = _normalize_range(left, right, self.n)
        target = _integer(target, "target")
        if target <= 0:
            return 0
        if self._range_total(left, right) < target:
            return -1

        state = self._make_state(left, right)
        answer = code = 0
        for level in range(self._levels):
            zero, one = self._split_state(state, level)
            one_count, one_sum = self._state_pair(one, level + 1)
            if one_sum >= target:
                code |= 1 << (self._levels - level - 1)
                state = one
            else:
                answer += one_count
                target -= one_sum
                state = zero
        value = self._decode_value(code)
        return answer + (target + value - 1) // value

    def prev_value(
        self, left: Any, right: Any, upper: Any, default: Any = -1
    ) -> Any:
        """Return the largest value below ``upper``, or ``default``."""
        left, right = _normalize_range(left, right, self.n)
        upper = _integer(upper, "upper")
        count = self._count_lt_checked(left, right, upper)
        return default if count == 0 else self._kth_checked(left, right, count - 1)

    def next_value(
        self, left: Any, right: Any, lower: Any, default: Any = -1
    ) -> Any:
        """Return the smallest value at least ``lower``, or ``default``."""
        left, right = _normalize_range(left, right, self.n)
        lower = _integer(lower, "lower")
        count = self._count_lt_checked(left, right, lower)
        return (
            default
            if count == right - left
            else self._kth_checked(left, right, count)
        )

    def max_le(
        self, left: Any, right: Any, value: Any, default: Any = -1
    ) -> Any:
        """Return the largest value at most ``value``, or ``default``."""
        value = _integer(value, "value")
        return self.prev_value(left, right, value + 1, default)

    def min_ge(
        self, left: Any, right: Any, value: Any, default: Any = -1
    ) -> Any:
        """Return the smallest value at least ``value``, or ``default``."""
        value = _integer(value, "value")
        return self.next_value(left, right, value, default)


def _fenwick_from_active(
    active: list[int], packed: bool
) -> tuple[array, array | list[int]]:
    """Build count and sum Fenwick trees in linear time."""
    size = len(active)
    counts = array("i", [0])
    counts.extend(value != 0 for value in active)
    if packed:
        sums: array | list[int] = array("q", [0])
        sums.extend(active)
    else:
        sums = [0, *active]
    for index in range(1, size + 1):
        parent = index + (index & -index)
        if parent <= size:
            counts[parent] += counts[index]
            sums[parent] += sums[index]
    return counts, sums


def _sum_fenwick_from_values(
    values: Sequence[int], packed: bool
) -> array | list[int]:
    if packed:
        tree: array | list[int] = array("q", [0])
        tree.extend(values)
    else:
        tree = [0, *values]
    size = len(values)
    for index in range(1, size + 1):
        parent = index + (index & -index)
        if parent <= size:
            tree[parent] += tree[index]
    return tree


class CompressedDynamicWaveletMatrix(_ImmediateQueries):
    """Immediate point updates over predeclared per-index candidates.

    ``update_candidates`` must contain every ``(index, value)`` assignment
    that can occur.  Construction is ``O(M log sigma)`` and each update or
    query is ``O(log M log sigma)``, where ``M`` is the total number of unique
    per-index candidates.  The static candidate layout is a wavelet matrix;
    one active candidate per index is maintained with Fenwick trees.
    """

    __slots__ = (
        "n",
        "_values",
        "_coordinates",
        "_coordinate_rank",
        "_levels",
        "_domain_size",
        "_mid",
        "_blocks",
        "_prefix",
        "_count_fenwick",
        "_sum_fenwick",
        "_index_sum_fenwick",
        "_candidate_values",
        "_candidate_rank",
        "_current_slot",
        "_offsets",
        "_packed",
    )

    def __init__(
        self,
        values: Iterable[int],
        update_candidates: Iterable[tuple[int, int]] = (),
    ) -> None:
        initial = _sequence(values)
        n = len(initial)
        candidates: list[set[int]] = [{value} for value in initial]

        for update in update_candidates:
            try:
                raw_index, raw_value = update
            except (TypeError, ValueError):
                raise ValueError(
                    "each update candidate must be an (index, value) pair"
            ) from None
            index = _normalize_index(raw_index, n)
            candidates[index].add(_positive_integer(raw_value))

        rows: list[tuple[int, ...]] = []
        flat_values: list[int] = []
        offsets = [0]
        maximum_sum = 0
        for candidate_row in candidates:
            row = tuple(sorted(candidate_row))
            rows.append(row)
            flat_values.extend(row)
            offsets.append(len(flat_values))
            maximum_sum += row[-1]
        del candidates

        point_count = len(flat_values)
        if point_count >= _I32_LIMIT:
            raise OverflowError("too many distinct update candidates")

        packed = maximum_sum < _I64_LIMIT
        coordinates = tuple(sorted(set(flat_values)))
        coordinate_rank = {
            value: rank for rank, value in enumerate(coordinates)
        }
        ranks = [coordinate_rank[value] for value in flat_values]
        candidate_rank = array("i", ranks)
        active = [0] * point_count
        current_slot = array("i", [0]) * n
        for index, value in enumerate(initial):
            position = offsets[index] + bisect_left(rows[index], value)
            active[position] = value
            current_slot[index] = position
        del rows

        domain_size = len(coordinates)
        levels = max(1, (domain_size - 1).bit_length())
        mid: list[int] = []
        blocks: list[array] = []
        prefix: list[array] = []
        count_fenwick: list[array] = []
        sum_fenwick: list[array | list[int]] = []
        index_sum_fenwick = _sum_fenwick_from_values(initial, packed)

        for height in range(levels - 1, -1, -1):
            block_count = (point_count + 63) >> 6
            bit_blocks = array("Q", [0]) * block_count
            zero_ranks: list[int] = []
            one_ranks: list[int] = []
            zero_active: list[int] = []
            one_active: list[int] = []
            bit = 1 << height

            for position, value_rank in enumerate(ranks):
                if value_rank & bit:
                    bit_blocks[position >> 6] |= 1 << (position & 63)
                    one_ranks.append(value_rank)
                    one_active.append(active[position])
                else:
                    zero_ranks.append(value_rank)
                    zero_active.append(active[position])

            bit_prefix = array("i", [0]) * (block_count + 1)
            running = 0
            for block, word in enumerate(bit_blocks):
                running += word.bit_count()
                bit_prefix[block + 1] = running

            mid.append(len(zero_ranks))
            blocks.append(bit_blocks)
            prefix.append(bit_prefix)
            ranks = zero_ranks + one_ranks
            active = zero_active + one_active
            counts, sums = _fenwick_from_active(active, packed)
            count_fenwick.append(counts)
            sum_fenwick.append(sums)

        self.n = n
        self._values = initial
        self._coordinates = coordinates
        self._coordinate_rank = coordinate_rank
        self._levels = levels
        self._domain_size = domain_size
        self._mid = mid
        self._blocks = blocks
        self._prefix = prefix
        self._count_fenwick = count_fenwick
        self._sum_fenwick = sum_fenwick
        self._index_sum_fenwick = index_sum_fenwick
        self._candidate_values = tuple(flat_values)
        self._candidate_rank = candidate_rank
        self._current_slot = current_slot
        self._offsets = array("i", offsets)
        self._packed = packed

    @property
    def coordinates(self) -> tuple[int, ...]:
        """Sorted immutable value coordinates used by the matrix."""
        return self._coordinates

    @property
    def candidate_count(self) -> int:
        """Total unique ``(index, value)`` candidates stored."""
        return self._offsets[-1]

    @property
    def packed_sums(self) -> bool:
        """Whether sums use compact signed-64-bit arrays."""
        return self._packed

    def _rank1(self, level: int, position: int) -> int:
        block = position >> 6
        offset = position & 63
        result = self._prefix[level][block]
        if offset:
            result += (
                self._blocks[level][block] & ((1 << offset) - 1)
            ).bit_count()
        return result

    def _children(
        self, level: int, left: int, right: int
    ) -> tuple[int, int, int, int]:
        left_one = self._rank1(level, left)
        right_one = self._rank1(level, right)
        middle = self._mid[level]
        return (
            left - left_one,
            right - right_one,
            middle + left_one,
            middle + right_one,
        )

    def _children_zero_pair(
        self, level: int, left: int, right: int
    ) -> tuple[int, int, int, int, int, int]:
        blocks = self._blocks[level]
        prefix = self._prefix[level]
        block = left >> 6
        offset = left & 63
        left_one = prefix[block]
        if offset:
            left_one += (
                blocks[block] & ((1 << offset) - 1)
            ).bit_count()
        block = right >> 6
        offset = right & 63
        right_one = prefix[block]
        if offset:
            right_one += (
                blocks[block] & ((1 << offset) - 1)
            ).bit_count()

        left_zero = left - left_one
        right_zero = right - right_one
        counts = self._count_fenwick[level]
        sums = self._sum_fenwick[level]
        count = total = 0
        cursor = right_zero
        while cursor:
            count += counts[cursor]
            total += sums[cursor]
            cursor &= cursor - 1
        cursor = left_zero
        while cursor:
            count -= counts[cursor]
            total -= sums[cursor]
            cursor &= cursor - 1
        middle = self._mid[level]
        return (
            left_zero,
            right_zero,
            middle + left_one,
            middle + right_one,
            count,
            total,
        )

    def _children_one_pair(
        self, level: int, left: int, right: int
    ) -> tuple[int, int, int, int, int, int]:
        blocks = self._blocks[level]
        prefix = self._prefix[level]
        block = left >> 6
        offset = left & 63
        left_one_rank = prefix[block]
        if offset:
            left_one_rank += (
                blocks[block] & ((1 << offset) - 1)
            ).bit_count()
        block = right >> 6
        offset = right & 63
        right_one_rank = prefix[block]
        if offset:
            right_one_rank += (
                blocks[block] & ((1 << offset) - 1)
            ).bit_count()

        middle = self._mid[level]
        left_one = middle + left_one_rank
        right_one = middle + right_one_rank
        counts = self._count_fenwick[level]
        sums = self._sum_fenwick[level]
        count = total = 0
        cursor = right_one
        while cursor:
            count += counts[cursor]
            total += sums[cursor]
            cursor &= cursor - 1
        cursor = left_one
        while cursor:
            count -= counts[cursor]
            total -= sums[cursor]
            cursor &= cursor - 1
        return (
            left - left_one_rank,
            right - right_one_rank,
            left_one,
            right_one,
            count,
            total,
        )

    def _range_pair(self, level: int, left: int, right: int) -> tuple[int, int]:
        counts = self._count_fenwick[level - 1]
        sums = self._sum_fenwick[level - 1]
        count = total = 0
        while right:
            count += counts[right]
            total += sums[right]
            right &= right - 1
        while left:
            count -= counts[left]
            total -= sums[left]
            left &= left - 1
        return count, total

    def _range_count(self, level: int, left: int, right: int) -> int:
        tree = self._count_fenwick[level - 1]
        count = 0
        while right:
            count += tree[right]
            right &= right - 1
        while left:
            count -= tree[left]
            left &= left - 1
        return count

    def _range_matrix_sum(self, level: int, left: int, right: int) -> int:
        tree = self._sum_fenwick[level - 1]
        total = 0
        while right:
            total += tree[right]
            right &= right - 1
        while left:
            total -= tree[left]
            left &= left - 1
        return total

    def _point_replace(
        self,
        old_position: int,
        old_rank: int,
        old_value: int,
        new_position: int,
        new_rank: int,
        new_value: int,
    ) -> None:
        size = self._offsets[-1]
        levels = self._levels
        prefix = self._prefix
        blocks = self._blocks
        mid = self._mid
        count_fenwick = self._count_fenwick
        sum_fenwick = self._sum_fenwick
        shared_delta = new_value - old_value
        for level in range(levels):
            level_prefix = prefix[level]
            level_blocks = blocks[level]
            block = old_position >> 6
            offset = old_position & 63
            ones = level_prefix[block]
            if offset:
                ones += (
                    level_blocks[block] & ((1 << offset) - 1)
                ).bit_count()
            height = levels - level - 1
            if old_rank >> height & 1:
                old_position = mid[level] + ones
            else:
                old_position -= ones

            block = new_position >> 6
            offset = new_position & 63
            ones = level_prefix[block]
            if offset:
                ones += (
                    level_blocks[block] & ((1 << offset) - 1)
                ).bit_count()
            if new_rank >> height & 1:
                new_position = mid[level] + ones
            else:
                new_position -= ones

            counts = count_fenwick[level]
            sums = sum_fenwick[level]
            old_tree = old_position + 1
            new_tree = new_position + 1
            while (
                old_tree <= size
                and new_tree <= size
                and old_tree != new_tree
            ):
                if old_tree < new_tree:
                    counts[old_tree] -= 1
                    sums[old_tree] -= old_value
                    old_tree += old_tree & -old_tree
                else:
                    counts[new_tree] += 1
                    sums[new_tree] += new_value
                    new_tree += new_tree & -new_tree

            if old_tree == new_tree:
                while old_tree <= size:
                    sums[old_tree] += shared_delta
                    old_tree += old_tree & -old_tree
            else:
                while old_tree <= size:
                    counts[old_tree] -= 1
                    sums[old_tree] -= old_value
                    old_tree += old_tree & -old_tree
                while new_tree <= size:
                    counts[new_tree] += 1
                    sums[new_tree] += new_value
                    new_tree += new_tree & -new_tree

    def _make_state(self, left: int, right: int) -> tuple[int, int]:
        return self._offsets[left], self._offsets[right]

    def _split_state(
        self, state: tuple[int, int], level: int
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        left_zero, right_zero, left_one, right_one = self._children(
            level, *state
        )
        return (left_zero, right_zero), (left_one, right_one)

    def _state_pair(
        self, state: tuple[int, int], level: int
    ) -> tuple[int, int]:
        return self._range_pair(level, *state)

    def _range_total(self, left: int, right: int) -> int:
        tree = self._index_sum_fenwick
        total = 0
        while right:
            total += tree[right]
            right &= right - 1
        while left:
            total -= tree[left]
            left &= left - 1
        return total

    def _encode_bound(self, upper: int) -> int:
        return bisect_left(self._coordinates, upper)

    def _decode_value(self, code: int) -> int:
        return self._coordinates[code]

    def _count_lt_checked(self, left: int, right: int, upper: int) -> int:
        if left == right or not self._coordinates:
            return 0
        target = bisect_left(self._coordinates, upper)
        if target == 0:
            return 0
        if target == len(self._coordinates):
            return right - left
        left = self._offsets[left]
        right = self._offsets[right]
        result = 0
        for level in range(self._levels):
            left_zero, right_zero, left_one, right_one = self._children(
                level, left, right
            )
            height = self._levels - level - 1
            if target >> height & 1:
                result += self._range_count(
                    level + 1, left_zero, right_zero
                )
                left, right = left_one, right_one
            else:
                left, right = left_zero, right_zero
        return result

    def _sum_lt_checked(self, left: int, right: int, upper: int) -> int:
        if left == right or not self._coordinates:
            return 0
        target = bisect_left(self._coordinates, upper)
        if target == 0:
            return 0
        if target == len(self._coordinates):
            return self._range_total(left, right)
        left = self._offsets[left]
        right = self._offsets[right]
        result = 0
        for level in range(self._levels):
            left_zero, right_zero, left_one, right_one = self._children(
                level, left, right
            )
            height = self._levels - level - 1
            if target >> height & 1:
                result += self._range_matrix_sum(
                    level + 1, left_zero, right_zero
                )
                left, right = left_one, right_one
            else:
                left, right = left_zero, right_zero
        return result

    def _kth_checked(self, left: int, right: int, k: int) -> int:
        left = self._offsets[left]
        right = self._offsets[right]
        value_rank = 0
        for level in range(self._levels):
            left_zero, right_zero, left_one, right_one = self._children(
                level, left, right
            )
            zero_count = self._range_count(
                level + 1, left_zero, right_zero
            )
            if k < zero_count:
                left, right = left_zero, right_zero
            else:
                k -= zero_count
                value_rank |= 1 << (self._levels - level - 1)
                left, right = left_one, right_one
        return self._coordinates[value_rank]

    def sum_k_smallest(self, left: Any, right: Any, k: Any) -> int:
        """Return the sum of the ``k`` smallest values in the range."""
        left, right = _normalize_range(left, right, self.n)
        k = _normalize_k(k, right - left, inclusive=True)
        if k == 0:
            return 0
        left = self._offsets[left]
        right = self._offsets[right]
        levels = self._levels
        children_zero_pair = self._children_zero_pair
        result = value_rank = 0
        for level in range(levels):
            (
                left_zero,
                right_zero,
                left_one,
                right_one,
                zero_count,
                zero_sum,
            ) = children_zero_pair(level, left, right)
            if k <= zero_count:
                left, right = left_zero, right_zero
            else:
                result += zero_sum
                k -= zero_count
                value_rank |= 1 << (levels - level - 1)
                left, right = left_one, right_one
        return result + k * self._coordinates[value_rank]

    def sum_k_largest(self, left: Any, right: Any, k: Any) -> int:
        """Return the sum of the ``k`` largest values in the range."""
        left, right = _normalize_range(left, right, self.n)
        k = _normalize_k(k, right - left, inclusive=True)
        if k == 0:
            return 0
        left = self._offsets[left]
        right = self._offsets[right]
        levels = self._levels
        children_one_pair = self._children_one_pair
        result = value_rank = 0
        for level in range(levels):
            (
                left_zero,
                right_zero,
                left_one,
                right_one,
                one_count,
                one_sum,
            ) = children_one_pair(level, left, right)
            if k <= one_count:
                value_rank |= 1 << (levels - level - 1)
                left, right = left_one, right_one
            else:
                result += one_sum
                k -= one_count
                left, right = left_zero, right_zero
        return result + k * self._coordinates[value_rank]

    def min_count_sum_at_least(
        self, left: Any, right: Any, target: Any
    ) -> int:
        """Minimum count whose largest-value sum reaches ``target``."""
        left, right = _normalize_range(left, right, self.n)
        target = _integer(target, "target")
        if target <= 0:
            return 0
        total = self._range_total(left, right)
        if total < target:
            return -1
        left = self._offsets[left]
        right = self._offsets[right]
        levels = self._levels
        children_one_pair = self._children_one_pair
        answer = value_rank = 0
        for level in range(levels):
            (
                left_zero,
                right_zero,
                left_one,
                right_one,
                one_count,
                one_sum,
            ) = children_one_pair(level, left, right)
            if one_sum >= target:
                value_rank |= 1 << (levels - level - 1)
                left, right = left_one, right_one
            else:
                answer += one_count
                target -= one_sum
                left, right = left_zero, right_zero
        value = self._coordinates[value_rank]
        return answer + (target + value - 1) // value

    def access(self, index: Any) -> int:
        """Return the current value at ``index``."""
        return self._values[_normalize_index(index, self.n)]

    __getitem__ = access

    def set(self, index: Any, value: Any) -> None:
        """Immediately assign ``value`` to ``A[index]``."""
        index = _normalize_index(index, self.n)
        value = _positive_integer(value)
        begin = self._offsets[index]
        end = self._offsets[index + 1]
        candidate = bisect_left(
            self._candidate_values, value, begin, end
        )
        if candidate == end or self._candidate_values[candidate] != value:
            raise ValueError(
                "value was not predeclared for this index in update_candidates"
            )

        old = self._values[index]
        if old == value:
            return
        old_position = self._current_slot[index]
        self._point_replace(
            old_position,
            self._candidate_rank[old_position],
            old,
            candidate,
            self._candidate_rank[candidate],
            value,
        )

        tree_index = index + 1
        delta = value - old
        while tree_index <= self.n:
            self._index_sum_fenwick[tree_index] += delta
            tree_index += tree_index & -tree_index
        self._values[index] = value
        self._current_slot[index] = candidate

    point_set = set
    update = set

    def add(self, index: Any, delta: Any) -> None:
        """Immediately add ``delta`` to ``A[index]``."""
        index = _normalize_index(index, self.n)
        delta = _integer(delta, "delta")
        self.set(index, self._values[index] + delta)

    def __setitem__(self, index: Any, value: Any) -> None:
        self.set(index, value)

    def rank(self, left: Any, right: Any, value: Any) -> int:
        """Count occurrences of ``value`` in ``A[left:right]``."""
        left, right = _normalize_range(left, right, self.n)
        value = _integer(value, "value")
        value_rank = self._coordinate_rank.get(value)
        if value_rank is None or left == right:
            return 0

        left = self._offsets[left]
        right = self._offsets[right]
        levels = self._levels
        blocks = self._blocks
        prefix = self._prefix
        middle = self._mid
        for level in range(levels):
            block = left >> 6
            offset = left & 63
            left_one = prefix[level][block]
            if offset:
                left_one += (
                    blocks[level][block] & ((1 << offset) - 1)
                ).bit_count()

            block = right >> 6
            offset = right & 63
            right_one = prefix[level][block]
            if offset:
                right_one += (
                    blocks[level][block] & ((1 << offset) - 1)
                ).bit_count()

            if value_rank >> (levels - level - 1) & 1:
                base = middle[level]
                left = base + left_one
                right = base + right_one
            else:
                left -= left_one
                right -= right_one
        return self._range_count(levels, left, right)

    count = rank


class _PatriciaPool:
    """Array-backed pool of mutable Patricia multisets.

    Node references use the low bit as a tag: zero is an empty tree, odd
    references are leaves, and positive even references are branches.
    """

    __slots__ = (
        "packed",
        "leaf_key",
        "leaf_count",
        "leaf_free",
        "branch_bit",
        "branch_left",
        "branch_right",
        "branch_sample",
        "branch_count",
        "branch_sum",
        "branch_free",
    )

    def __init__(self, packed: bool) -> None:
        self.packed = packed
        self.leaf_key: list[int] = []
        self.leaf_count = array("i")
        self.leaf_free: list[int] = []
        self.branch_bit = array("i")
        self.branch_left = array("I")
        self.branch_right = array("I")
        self.branch_sample = array("I")
        self.branch_count = array("i")
        self.branch_sum: array | list[int] = array("q") if packed else []
        self.branch_free: list[int] = []

    def _new_leaf(self, key: int, count: int = 1) -> int:
        if self.leaf_free:
            leaf = self.leaf_free.pop()
            self.leaf_key[leaf] = key
            self.leaf_count[leaf] = count
        else:
            leaf = len(self.leaf_key)
            self.leaf_key.append(key)
            self.leaf_count.append(count)
        return (leaf << 1) | 1

    def _new_branch(self, bit: int, left: int, right: int) -> int:
        if left & 1:
            leaf = left >> 1
            sample = leaf
            count = self.leaf_count[leaf]
            total = self.leaf_key[leaf] * count
        else:
            child = (left >> 1) - 1
            sample = self.branch_sample[child]
            count = self.branch_count[child]
            total = self.branch_sum[child]
        if right & 1:
            leaf = right >> 1
            right_count = self.leaf_count[leaf]
            right_sum = self.leaf_key[leaf] * right_count
        else:
            child = (right >> 1) - 1
            right_count = self.branch_count[child]
            right_sum = self.branch_sum[child]
        count += right_count
        total += right_sum

        if self.branch_free:
            branch = self.branch_free.pop()
            self.branch_bit[branch] = bit
            self.branch_left[branch] = left
            self.branch_right[branch] = right
            self.branch_sample[branch] = sample
            self.branch_count[branch] = count
            self.branch_sum[branch] = total
        else:
            branch = len(self.branch_bit)
            self.branch_bit.append(bit)
            self.branch_left.append(left)
            self.branch_right.append(right)
            self.branch_sample.append(sample)
            self.branch_count.append(count)
            self.branch_sum.append(total)
        return (branch + 1) << 1

    def _pull_path(self, path: list[int], last: int) -> None:
        branch_left = self.branch_left
        branch_right = self.branch_right
        branch_sample = self.branch_sample
        branch_count = self.branch_count
        branch_sum = self.branch_sum
        leaf_key = self.leaf_key
        leaf_count = self.leaf_count
        for path_index in range(last, -1, -1):
            branch = path[path_index]
            left = branch_left[branch]
            if left & 1:
                leaf = left >> 1
                sample = leaf
                count = leaf_count[leaf]
                total = leaf_key[leaf] * count
            else:
                child = (left >> 1) - 1
                sample = branch_sample[child]
                count = branch_count[child]
                total = branch_sum[child]
            right = branch_right[branch]
            if right & 1:
                leaf = right >> 1
                right_count = leaf_count[leaf]
                right_sum = leaf_key[leaf] * right_count
            else:
                child = (right >> 1) - 1
                right_count = branch_count[child]
                right_sum = branch_sum[child]
            branch_sample[branch] = sample
            branch_count[branch] = count + right_count
            branch_sum[branch] = total + right_sum

    def build(self, values: Sequence[int]) -> int:
        """Build from a sorted value sequence in linear time."""
        if not values:
            return 0
        new_branch = self._new_branch

        operands: list[int] = []
        operators: list[int] = []
        index = 0
        previous: int | None = None
        length = len(values)
        while index < length:
            key = values[index]
            end = index + 1
            while end < length and values[end] == key:
                end += 1
            leaf = self._new_leaf(key, end - index)
            if previous is not None:
                bit = (previous ^ key).bit_length() - 1
                while operators and operators[-1] <= bit:
                    branch_bit = operators.pop()
                    right = operands.pop()
                    left = operands.pop()
                    operands.append(
                        new_branch(branch_bit, left, right)
                    )
                operators.append(bit)
            operands.append(leaf)
            previous = key
            index = end

        while operators:
            bit = operators.pop()
            right = operands.pop()
            left = operands.pop()
            operands.append(new_branch(bit, left, right))
        return operands[0]

    def insert(self, root: int, key: int) -> int:
        if root == 0:
            return self._new_leaf(key)
        pull_path = self._pull_path
        new_branch = self._new_branch

        path: list[int] = []
        node = root
        while not node & 1:
            branch = (node >> 1) - 1
            direction = key >> self.branch_bit[branch] & 1
            path.append(branch)
            node = (
                self.branch_right[branch]
                if direction
                else self.branch_left[branch]
            )

        leaf = node >> 1
        old_key = self.leaf_key[leaf]
        if old_key == key:
            self.leaf_count[leaf] += 1
            pull_path(path, len(path) - 1)
            return root

        different = (old_key ^ key).bit_length() - 1
        depth = 0
        path_length = len(path)
        while (
            depth < path_length
            and self.branch_bit[path[depth]] > different
        ):
            depth += 1

        if depth == 0:
            subtree = root
        else:
            parent = path[depth - 1]
            subtree = (
                self.branch_right[parent]
                if key >> self.branch_bit[parent] & 1
                else self.branch_left[parent]
            )

        new_leaf = self._new_leaf(key)
        if key >> different & 1:
            new_root = new_branch(different, subtree, new_leaf)
        else:
            new_root = new_branch(different, new_leaf, subtree)

        if depth == 0:
            return new_root

        parent = path[depth - 1]
        if key >> self.branch_bit[parent] & 1:
            self.branch_right[parent] = new_root
        else:
            self.branch_left[parent] = new_root
        pull_path(path, depth - 1)
        return root

    def delete(self, root: int, key: int) -> int:
        if root == 0:
            raise KeyError(key)
        pull_path = self._pull_path

        path: list[int] = []
        node = root
        while not node & 1:
            branch = (node >> 1) - 1
            direction = key >> self.branch_bit[branch] & 1
            path.append(branch)
            node = (
                self.branch_right[branch]
                if direction
                else self.branch_left[branch]
            )

        leaf = node >> 1
        if self.leaf_key[leaf] != key:
            raise KeyError(key)
        count = self.leaf_count[leaf]
        if count > 1:
            self.leaf_count[leaf] = count - 1
            pull_path(path, len(path) - 1)
            return root

        self.leaf_free.append(leaf)
        if not path:
            return 0

        parent = path[-1]
        sibling = (
            self.branch_left[parent]
            if key >> self.branch_bit[parent] & 1
            else self.branch_right[parent]
        )
        self.branch_free.append(parent)
        if len(path) == 1:
            return sibling

        grandparent = path[-2]
        if key >> self.branch_bit[grandparent] & 1:
            self.branch_right[grandparent] = sibling
        else:
            self.branch_left[grandparent] = sibling
        pull_path(path, len(path) - 2)
        return root

    def aggregate_sum(self, nodes: Sequence[int]) -> int:
        leaf_key = self.leaf_key
        leaf_count = self.leaf_count
        branch_sum = self.branch_sum
        total = 0
        for node in nodes:
            if node & 1:
                leaf = node >> 1
                total += leaf_key[leaf] * leaf_count[leaf]
            else:
                total += branch_sum[(node >> 1) - 1]
        return total

    def split_fast(
        self, nodes: Sequence[int], height: int
    ) -> tuple[list[int], list[int], int, int, int, int]:
        """Partition at one bit without computing child extrema."""
        leaf_key = self.leaf_key
        leaf_count = self.leaf_count
        branch_bit = self.branch_bit
        branch_left = self.branch_left
        branch_right = self.branch_right
        branch_sample = self.branch_sample
        branch_count = self.branch_count
        branch_sum = self.branch_sum
        zero: list[int] = []
        one: list[int] = []
        append_zero = zero.append
        append_one = one.append
        zero_count = zero_sum = one_count = one_sum = 0

        for node in nodes:
            if node & 1:
                leaf = node >> 1
                count = leaf_count[leaf]
                total = leaf_key[leaf] * count
                if leaf_key[leaf] >> height & 1:
                    append_one(node)
                    one_count += count
                    one_sum += total
                else:
                    append_zero(node)
                    zero_count += count
                    zero_sum += total
                continue

            branch = (node >> 1) - 1
            bit = branch_bit[branch]
            if bit == height:
                left = branch_left[branch]
                right = branch_right[branch]
                append_zero(left)
                append_one(right)
                if left & 1:
                    leaf = left >> 1
                    count = leaf_count[leaf]
                    total = leaf_key[leaf] * count
                else:
                    child = (left >> 1) - 1
                    count = branch_count[child]
                    total = branch_sum[child]
                zero_count += count
                zero_sum += total
                if right & 1:
                    leaf = right >> 1
                    count = leaf_count[leaf]
                    total = leaf_key[leaf] * count
                else:
                    child = (right >> 1) - 1
                    count = branch_count[child]
                    total = branch_sum[child]
                one_count += count
                one_sum += total
            elif bit < height:
                count = branch_count[branch]
                total = branch_sum[branch]
                sample_key = leaf_key[branch_sample[branch]]
                if sample_key >> height & 1:
                    append_one(node)
                    one_count += count
                    one_sum += total
                else:
                    append_zero(node)
                    zero_count += count
                    zero_sum += total
            else:
                raise RuntimeError("invalid Patricia traversal state")

        return zero, one, zero_count, zero_sum, one_count, one_sum

    def split_count(
        self, nodes: Sequence[int], height: int
    ) -> tuple[list[int], list[int], int, int]:
        leaf_key = self.leaf_key
        leaf_count = self.leaf_count
        branch_bit = self.branch_bit
        branch_left = self.branch_left
        branch_right = self.branch_right
        branch_sample = self.branch_sample
        branch_count = self.branch_count
        zero: list[int] = []
        one: list[int] = []
        append_zero = zero.append
        append_one = one.append
        zero_count = one_count = 0

        for node in nodes:
            if node & 1:
                leaf = node >> 1
                count = leaf_count[leaf]
                if leaf_key[leaf] >> height & 1:
                    append_one(node)
                    one_count += count
                else:
                    append_zero(node)
                    zero_count += count
                continue

            branch = (node >> 1) - 1
            bit = branch_bit[branch]
            if bit == height:
                left = branch_left[branch]
                right = branch_right[branch]
                append_zero(left)
                append_one(right)
                zero_count += (
                    leaf_count[left >> 1]
                    if left & 1
                    else branch_count[(left >> 1) - 1]
                )
                one_count += (
                    leaf_count[right >> 1]
                    if right & 1
                    else branch_count[(right >> 1) - 1]
                )
            elif bit < height:
                count = branch_count[branch]
                if leaf_key[branch_sample[branch]] >> height & 1:
                    append_one(node)
                    one_count += count
                else:
                    append_zero(node)
                    zero_count += count
            else:
                raise RuntimeError("invalid Patricia traversal state")
        return zero, one, zero_count, one_count

    def descend_zero(self, nodes: Sequence[int], height: int) -> list[int]:
        """Return only the zero-bit child frontier."""
        leaf_key = self.leaf_key
        branch_bit = self.branch_bit
        branch_left = self.branch_left
        branch_sample = self.branch_sample
        zero: list[int] = []
        append = zero.append
        for node in nodes:
            if node & 1:
                if not leaf_key[node >> 1] >> height & 1:
                    append(node)
                continue
            branch = (node >> 1) - 1
            bit = branch_bit[branch]
            if bit == height:
                append(branch_left[branch])
            elif bit < height:
                if not leaf_key[branch_sample[branch]] >> height & 1:
                    append(node)
            else:
                raise RuntimeError("invalid Patricia traversal state")
        return zero

    def descend_one_count_zero(
        self, nodes: Sequence[int], height: int
    ) -> tuple[list[int], int]:
        """Return the one frontier and the skipped zero-side count."""
        leaf_key = self.leaf_key
        leaf_count = self.leaf_count
        branch_bit = self.branch_bit
        branch_left = self.branch_left
        branch_right = self.branch_right
        branch_sample = self.branch_sample
        branch_count = self.branch_count
        one: list[int] = []
        append = one.append
        zero_count = 0
        for node in nodes:
            if node & 1:
                leaf = node >> 1
                if leaf_key[leaf] >> height & 1:
                    append(node)
                else:
                    zero_count += leaf_count[leaf]
                continue
            branch = (node >> 1) - 1
            bit = branch_bit[branch]
            if bit == height:
                left = branch_left[branch]
                append(branch_right[branch])
                zero_count += (
                    leaf_count[left >> 1]
                    if left & 1
                    else branch_count[(left >> 1) - 1]
                )
            elif bit < height:
                if leaf_key[branch_sample[branch]] >> height & 1:
                    append(node)
                else:
                    zero_count += branch_count[branch]
            else:
                raise RuntimeError("invalid Patricia traversal state")
        return one, zero_count

    def descend_one_sum_zero(
        self, nodes: Sequence[int], height: int
    ) -> tuple[list[int], int]:
        """Return the one frontier and the skipped zero-side sum."""
        leaf_key = self.leaf_key
        leaf_count = self.leaf_count
        branch_bit = self.branch_bit
        branch_left = self.branch_left
        branch_right = self.branch_right
        branch_sample = self.branch_sample
        branch_sum = self.branch_sum
        one: list[int] = []
        append = one.append
        zero_sum = 0
        for node in nodes:
            if node & 1:
                leaf = node >> 1
                if leaf_key[leaf] >> height & 1:
                    append(node)
                else:
                    zero_sum += leaf_key[leaf] * leaf_count[leaf]
                continue
            branch = (node >> 1) - 1
            bit = branch_bit[branch]
            if bit == height:
                left = branch_left[branch]
                append(branch_right[branch])
                if left & 1:
                    leaf = left >> 1
                    zero_sum += leaf_key[leaf] * leaf_count[leaf]
                else:
                    zero_sum += branch_sum[(left >> 1) - 1]
            elif bit < height:
                if leaf_key[branch_sample[branch]] >> height & 1:
                    append(node)
                else:
                    zero_sum += branch_sum[branch]
            else:
                raise RuntimeError("invalid Patricia traversal state")
        return one, zero_sum

    def split_sum(
        self, nodes: Sequence[int], height: int
    ) -> tuple[list[int], list[int], int, int]:
        leaf_key = self.leaf_key
        leaf_count = self.leaf_count
        branch_bit = self.branch_bit
        branch_left = self.branch_left
        branch_right = self.branch_right
        branch_sample = self.branch_sample
        branch_sum = self.branch_sum
        zero: list[int] = []
        one: list[int] = []
        append_zero = zero.append
        append_one = one.append
        zero_sum = one_sum = 0

        for node in nodes:
            if node & 1:
                leaf = node >> 1
                total = leaf_key[leaf] * leaf_count[leaf]
                if leaf_key[leaf] >> height & 1:
                    append_one(node)
                    one_sum += total
                else:
                    append_zero(node)
                    zero_sum += total
                continue

            branch = (node >> 1) - 1
            bit = branch_bit[branch]
            if bit == height:
                left = branch_left[branch]
                right = branch_right[branch]
                append_zero(left)
                append_one(right)
                if left & 1:
                    leaf = left >> 1
                    zero_sum += leaf_key[leaf] * leaf_count[leaf]
                else:
                    zero_sum += branch_sum[(left >> 1) - 1]
                if right & 1:
                    leaf = right >> 1
                    one_sum += leaf_key[leaf] * leaf_count[leaf]
                else:
                    one_sum += branch_sum[(right >> 1) - 1]
            elif bit < height:
                total = branch_sum[branch]
                if leaf_key[branch_sample[branch]] >> height & 1:
                    append_one(node)
                    one_sum += total
                else:
                    append_zero(node)
                    zero_sum += total
            else:
                raise RuntimeError("invalid Patricia traversal state")
        return zero, one, zero_sum, one_sum

    def split_zero_pair(
        self, nodes: Sequence[int], height: int
    ) -> tuple[list[int], list[int], int, int]:
        leaf_key = self.leaf_key
        leaf_count = self.leaf_count
        branch_bit = self.branch_bit
        branch_left = self.branch_left
        branch_right = self.branch_right
        branch_sample = self.branch_sample
        branch_count = self.branch_count
        branch_sum = self.branch_sum
        zero: list[int] = []
        one: list[int] = []
        append_zero = zero.append
        append_one = one.append
        zero_count = zero_sum = 0

        for node in nodes:
            if node & 1:
                leaf = node >> 1
                if leaf_key[leaf] >> height & 1:
                    append_one(node)
                else:
                    append_zero(node)
                    count = leaf_count[leaf]
                    zero_count += count
                    zero_sum += leaf_key[leaf] * count
                continue
            branch = (node >> 1) - 1
            bit = branch_bit[branch]
            if bit == height:
                left = branch_left[branch]
                append_zero(left)
                append_one(branch_right[branch])
                if left & 1:
                    leaf = left >> 1
                    count = leaf_count[leaf]
                    zero_count += count
                    zero_sum += leaf_key[leaf] * count
                else:
                    child = (left >> 1) - 1
                    zero_count += branch_count[child]
                    zero_sum += branch_sum[child]
            elif bit < height:
                if leaf_key[branch_sample[branch]] >> height & 1:
                    append_one(node)
                else:
                    append_zero(node)
                    zero_count += branch_count[branch]
                    zero_sum += branch_sum[branch]
            else:
                raise RuntimeError("invalid Patricia traversal state")
        return zero, one, zero_count, zero_sum

    def split_one_pair(
        self, nodes: Sequence[int], height: int
    ) -> tuple[list[int], list[int], int, int]:
        leaf_key = self.leaf_key
        leaf_count = self.leaf_count
        branch_bit = self.branch_bit
        branch_left = self.branch_left
        branch_right = self.branch_right
        branch_sample = self.branch_sample
        branch_count = self.branch_count
        branch_sum = self.branch_sum
        zero: list[int] = []
        one: list[int] = []
        append_zero = zero.append
        append_one = one.append
        one_count = one_sum = 0

        for node in nodes:
            if node & 1:
                leaf = node >> 1
                if leaf_key[leaf] >> height & 1:
                    append_one(node)
                    count = leaf_count[leaf]
                    one_count += count
                    one_sum += leaf_key[leaf] * count
                else:
                    append_zero(node)
                continue
            branch = (node >> 1) - 1
            bit = branch_bit[branch]
            if bit == height:
                right = branch_right[branch]
                append_zero(branch_left[branch])
                append_one(right)
                if right & 1:
                    leaf = right >> 1
                    count = leaf_count[leaf]
                    one_count += count
                    one_sum += leaf_key[leaf] * count
                else:
                    child = (right >> 1) - 1
                    one_count += branch_count[child]
                    one_sum += branch_sum[child]
            elif bit < height:
                if leaf_key[branch_sample[branch]] >> height & 1:
                    append_one(node)
                    one_count += branch_count[branch]
                    one_sum += branch_sum[branch]
                else:
                    append_zero(node)
            else:
                raise RuntimeError("invalid Patricia traversal state")
        return zero, one, one_count, one_sum

def _merge_sorted(first: Sequence[int], second: Sequence[int]) -> list[int]:
    # Both halves are already runs, so CPython's C-level Timsort performs the
    # merge substantially faster than a Python-level two-pointer loop.
    result = [*first, *second]
    result.sort()
    return result


class DynamicWaveletMatrix(_ImmediateQueries):
    """Fully-online point-set range order-statistics structure.

    Future values need not be declared.  Internally this uses an index segment
    tree whose nodes contain compact Patricia multisets.  (A mutable wavelet
    matrix requires dynamic bitvectors; this representation provides the same
    public operations more naturally in pure Python.)

    Updates and selection queries take ``O(log n * W)`` worst-case time, where
    ``W <= 64`` is the current maximum value's bit length.  Memory is
    ``O(n log n)``.  With ``python_int_sum=False`` sums use compact signed
    64-bit arrays and the total sequence sum must remain below ``2**63``.
    """

    __slots__ = (
        "n",
        "_size",
        "_values",
        "_roots",
        "_pool",
        "_levels",
        "_domain_size",
        "python_int_sum",
        "total",
    )

    def __init__(
        self, values: Iterable[int], python_int_sum: bool = False
    ) -> None:
        if type(python_int_sum) is not bool:
            raise TypeError("python_int_sum must be a bool")
        initial = _sequence(values)
        total = sum(initial)
        if not python_int_sum and total >= _I64_LIMIT:
            raise OverflowError(
                "use python_int_sum=True when a range sum may exceed int64"
            )

        n = len(initial)
        size = 1
        while size < n:
            size <<= 1
        roots = array("I", [0]) * (size << 1)
        levels = max(1, max(initial).bit_length() if initial else 1)
        pool = _PatriciaPool(not python_int_sum)

        rows: list[list[int]] = [[value] for value in initial]
        rows.extend([] for _ in range(size - n))
        base = size
        while True:
            for index, row in enumerate(rows):
                roots[base + index] = pool.build(row)
            if base == 1:
                break
            rows = [
                _merge_sorted(rows[index], rows[index + 1])
                for index in range(0, len(rows), 2)
            ]
            base >>= 1

        self.n = n
        self._size = size
        self._values = initial
        self._roots = roots
        self._pool = pool
        self._levels = levels
        self._domain_size = 1 << levels
        self.python_int_sum = python_int_sum
        self.total = total

    @property
    def max_bit(self) -> int:
        """Current bit width used by value traversals."""
        return self._levels

    def _range_roots(self, left: int, right: int) -> list[int]:
        left += self._size
        right += self._size
        result: list[int] = []
        while left < right:
            if left & 1:
                result.append(self._roots[left])
                left += 1
            if right & 1:
                right -= 1
                result.append(self._roots[right])
            left >>= 1
            right >>= 1
        return result

    def _make_state(
        self, left: int, right: int
    ) -> tuple[list[int], int, int, int, int]:
        return self._range_roots(left, right), 0, 0, 0, 0

    def _split_state(
        self,
        state: tuple[Sequence[int], int, int, int, int],
        level: int,
    ) -> tuple[
        tuple[list[int], int, int, int, int],
        tuple[list[int], int, int, int, int],
    ]:
        zero, one, zero_count, zero_sum, one_count, one_sum = (
            self._pool.split_fast(state[0], self._levels - level - 1)
        )
        return (
            (zero, zero_count, zero_sum, 0, 0),
            (one, one_count, one_sum, 0, 0),
        )

    @staticmethod
    def _state_pair(
        state: tuple[Sequence[int], int, int, int, int], level: int
    ) -> tuple[int, int]:
        return state[1], state[2]

    def _range_total(self, left: int, right: int) -> int:
        return self._pool.aggregate_sum(self._range_roots(left, right))

    def _encode_bound(self, upper: int) -> int:
        return upper

    @staticmethod
    def _decode_value(code: int) -> int:
        return code

    def _count_lt_checked(self, left: int, right: int, upper: int) -> int:
        if upper <= 0 or left == right:
            return 0
        if upper >= self._domain_size:
            return right - left
        pool = self._pool
        nodes = self._range_roots(left, right)
        result = 0
        for height in range(self._levels - 1, -1, -1):
            if upper >> height & 1:
                nodes, zero_count = pool.descend_one_count_zero(nodes, height)
                result += zero_count
            else:
                nodes = pool.descend_zero(nodes, height)
            if not nodes:
                break
        return result

    def _sum_lt_checked(self, left: int, right: int, upper: int) -> int:
        if upper <= 0 or left == right:
            return 0
        if upper >= self._domain_size:
            return self._range_total(left, right)
        pool = self._pool
        nodes = self._range_roots(left, right)
        result = 0
        for height in range(self._levels - 1, -1, -1):
            if upper >> height & 1:
                nodes, zero_sum = pool.descend_one_sum_zero(nodes, height)
                result += zero_sum
            else:
                nodes = pool.descend_zero(nodes, height)
            if not nodes:
                break
        return result

    def _kth_checked(self, left: int, right: int, k: int) -> int:
        nodes = self._range_roots(left, right)
        result = 0
        for height in range(self._levels - 1, -1, -1):
            zero, one, zero_count, _ = self._pool.split_count(nodes, height)
            if k < zero_count:
                nodes = zero
            else:
                k -= zero_count
                result |= 1 << height
                nodes = one
        return result

    def rank(self, left: Any, right: Any, value: Any) -> int:
        """Count occurrences of ``value`` in ``A[left:right]``."""
        left, right = _normalize_range(left, right, self.n)
        value = _integer(value, "value")
        if left == right or value <= 0:
            return 0
        pool = self._pool
        branch_bit = pool.branch_bit
        branch_left = pool.branch_left
        branch_right = pool.branch_right
        leaf_key = pool.leaf_key
        leaf_count = pool.leaf_count
        result = 0
        for node in self._range_roots(left, right):
            while not node & 1:
                branch = (node >> 1) - 1
                node = (
                    branch_right[branch]
                    if value >> branch_bit[branch] & 1
                    else branch_left[branch]
                )
            leaf = node >> 1
            if leaf_key[leaf] == value:
                result += leaf_count[leaf]
        return result

    count = rank

    def sum_k_smallest(self, left: Any, right: Any, k: Any) -> int:
        """Return the sum of the ``k`` smallest values in the range."""
        left, right = _normalize_range(left, right, self.n)
        k = _normalize_k(k, right - left, inclusive=True)
        if k == 0:
            return 0
        nodes = self._range_roots(left, right)
        result = value = 0
        for height in range(self._levels - 1, -1, -1):
            zero, one, zero_count, zero_sum = self._pool.split_zero_pair(
                nodes, height
            )
            if k <= zero_count:
                nodes = zero
            else:
                result += zero_sum
                k -= zero_count
                value |= 1 << height
                nodes = one
        return result + k * value

    def sum_k_largest(self, left: Any, right: Any, k: Any) -> int:
        """Return the sum of the ``k`` largest values in the range."""
        left, right = _normalize_range(left, right, self.n)
        k = _normalize_k(k, right - left, inclusive=True)
        if k == 0:
            return 0
        nodes = self._range_roots(left, right)
        result = value = 0
        for height in range(self._levels - 1, -1, -1):
            zero, one, one_count, one_sum = self._pool.split_one_pair(
                nodes, height
            )
            if k <= one_count:
                value |= 1 << height
                nodes = one
            else:
                result += one_sum
                k -= one_count
                nodes = zero
        return result + k * value

    def min_count_sum_at_least(
        self, left: Any, right: Any, target: Any
    ) -> int:
        """Minimum count whose largest-value sum reaches ``target``."""
        left, right = _normalize_range(left, right, self.n)
        target = _integer(target, "target")
        if target <= 0:
            return 0
        nodes = self._range_roots(left, right)
        if self._pool.aggregate_sum(nodes) < target:
            return -1
        answer = value = 0
        for height in range(self._levels - 1, -1, -1):
            zero, one, one_count, one_sum = self._pool.split_one_pair(
                nodes, height
            )
            if one_sum >= target:
                value |= 1 << height
                nodes = one
            else:
                answer += one_count
                target -= one_sum
                nodes = zero
        return answer + (target + value - 1) // value

    def access(self, index: Any) -> int:
        """Return the current value at ``index``."""
        return self._values[_normalize_index(index, self.n)]

    __getitem__ = access

    def set(self, index: Any, value: Any) -> None:
        """Immediately assign ``value`` to ``A[index]``."""
        index = _normalize_index(index, self.n)
        value = _positive_integer(value)
        old = self._values[index]
        if old == value:
            return

        new_total = self.total - old + value
        if not self.python_int_sum and new_total >= _I64_LIMIT:
            raise OverflowError(
                "use python_int_sum=True when a range sum may exceed int64"
            )

        node = self._size + index
        roots = self._roots
        pool = self._pool
        while node:
            root = pool.delete(roots[node], old)
            roots[node] = pool.insert(root, value)
            node >>= 1

        self._values[index] = value
        self.total = new_total
        root = roots[1]
        while not root & 1:
            root = pool.branch_right[(root >> 1) - 1]
        maximum_leaf = root >> 1
        levels = max(1, pool.leaf_key[maximum_leaf].bit_length())
        self._levels = levels
        self._domain_size = 1 << levels

    point_set = set
    update = set

    def add(self, index: Any, delta: Any) -> None:
        """Immediately add ``delta`` to ``A[index]``."""
        index = _normalize_index(index, self.n)
        delta = _integer(delta, "delta")
        self.set(index, self._values[index] + delta)

    def __setitem__(self, index: Any, value: Any) -> None:
        self.set(index, value)


class OfflineDynamicWaveletMatrix:
    """Record point updates and solve selected range queries in one batch.

    Query methods return integer query IDs rather than answers.  ``solve()``
    returns answers in ID order and is idempotent.  The implementation uses
    iterative parallel value divide-and-conquer with count/sum Fenwick trees;
    it avoids constructing ``O(n log sigma)`` persistent nodes.

    Supported batch queries are ``range_sum``, ``kth_smallest``,
    ``kth_largest``, and ``min_count_sum_at_least``.
    """

    __slots__ = (
        "n",
        "_current",
        "_events",
        "_mod_position",
        "_mod_value",
        "_mod_delta",
        "_query_type",
        "_query_left",
        "_query_right",
        "_query_argument",
        "_answers",
    )

    _MIN_COUNT = 0
    _KTH_SMALLEST = 1
    _KTH_LARGEST = 2
    _RANGE_SUM = 3

    def __init__(self, values: Iterable[int]) -> None:
        initial = _sequence(values)
        n = len(initial)
        self.n = n
        self._current = initial[:]
        self._mod_position = array("i", range(n))
        self._mod_value = initial[:]
        self._mod_delta = array("b", [1]) * n
        self._events: list[int] = list(range(n))
        self._query_type = bytearray()
        self._query_left = array("i")
        self._query_right = array("i")
        self._query_argument: list[int] = []
        self._answers: list[int] | None = None

    def __len__(self) -> int:
        return self.n

    @property
    def query_count(self) -> int:
        """Number of registered queries."""
        return len(self._query_type)

    @property
    def solved(self) -> bool:
        """Whether ``solve()`` has already been called."""
        return self._answers is not None

    def _check_open(self) -> None:
        if self._answers is not None:
            raise RuntimeError("operations cannot be added after solve()")

    def _add_query(
        self, kind: int, left: Any, right: Any, argument: int
    ) -> int:
        self._check_open()
        left, right = _normalize_range(left, right, self.n)
        query_id = len(self._query_type)
        if query_id >= _I32_LIMIT:
            raise OverflowError("too many offline queries")
        self._query_type.append(kind)
        self._query_left.append(left)
        self._query_right.append(right)
        self._query_argument.append(argument)
        self._events.append(~query_id)
        return query_id

    def access(self, index: Any) -> int:
        """Return the value after all updates registered so far."""
        return self._current[_normalize_index(index, self.n)]

    __getitem__ = access

    def __iter__(self) -> Iterator[int]:
        return iter(self._current)

    def tolist(self) -> list[int]:
        """Return values after all updates registered so far."""
        return self._current[:]

    def __str__(self) -> str:
        return str(self.tolist())

    def __repr__(self) -> str:
        return "OfflineDynamicWaveletMatrix(%r)" % self.tolist()

    def set(self, index: Any, value: Any) -> None:
        """Register ``A[index] = value``."""
        self._check_open()
        index = _normalize_index(index, self.n)
        value = _positive_integer(value)
        old = self._current[index]
        if old == value:
            return

        modification = len(self._mod_position)
        if modification + 1 >= _I32_LIMIT:
            raise OverflowError("too many offline modifications")
        self._mod_position.append(index)
        self._mod_value.append(old)
        self._mod_delta.append(-1)
        self._events.append(modification)
        modification += 1
        self._mod_position.append(index)
        self._mod_value.append(value)
        self._mod_delta.append(1)
        self._events.append(modification)
        self._current[index] = value

    point_set = set
    update = set

    def add(self, index: Any, delta: Any) -> None:
        """Register ``A[index] += delta``."""
        self._check_open()
        index = _normalize_index(index, self.n)
        delta = _integer(delta, "delta")
        self.set(index, self._current[index] + delta)

    def __setitem__(self, index: Any, value: Any) -> None:
        self.set(index, value)

    def min_count_sum_at_least(
        self, left: Any, right: Any, target: Any
    ) -> int:
        """Register the minimum-count largest-values threshold query."""
        target = _integer(target, "target")
        return self._add_query(self._MIN_COUNT, left, right, target)

    def kth_smallest(self, left: Any, right: Any, k: Any) -> int:
        """Register the zero-indexed k-th smallest query."""
        self._check_open()
        left, right = _normalize_range(left, right, self.n)
        k = _normalize_k(k, right - left, inclusive=False)
        return self._add_query(self._KTH_SMALLEST, left, right, k)

    quantile = kth_smallest

    def kth_largest(self, left: Any, right: Any, k: Any) -> int:
        """Register the zero-indexed k-th largest query."""
        self._check_open()
        left, right = _normalize_range(left, right, self.n)
        k = _normalize_k(k, right - left, inclusive=False)
        return self._add_query(self._KTH_LARGEST, left, right, k)

    def range_sum(self, left: Any, right: Any) -> int:
        """Register ``sum(A[left:right])``."""
        return self._add_query(self._RANGE_SUM, left, right, 0)

    sum = range_sum

    def answer(self, query_id: Any) -> int:
        """Return one answer after ``solve()`` has completed."""
        if self._answers is None:
            raise RuntimeError("solve() has not been called")
        query_id = _normalize_index(query_id, len(self._answers))
        return self._answers[query_id]

    def solve(self) -> list[int]:
        """Evaluate all operations and return answers in query-ID order."""
        if self._answers is not None:
            return self._answers[:]

        query_type = self._query_type
        query_count = len(query_type)
        if query_count == 0:
            self._answers = []
            return []

        n = self.n
        query_left = self._query_left
        query_right = self._query_right
        remaining = self._query_argument[:]
        answers: list[int | None] = [None] * query_count
        active = bytearray(query_count)

        events = self._events
        mod_position = self._mod_position
        mod_value = self._mod_value
        mod_delta = self._mod_delta
        needs_sum_pass = (
            self._MIN_COUNT in query_type or self._RANGE_SUM in query_type
        )
        if not needs_sum_pass:
            active[:] = b"\x01" * query_count
        else:
            # Resolve range sums and trivial/impossible threshold queries in
            # one chronological pass.
            bit_sum = [0, *mod_value[:n]]
            for index in range(1, n + 1):
                parent = index + (index & -index)
                if parent <= n:
                    bit_sum[parent] += bit_sum[index]

            for event_index in range(n, len(events)):
                event = events[event_index]
                if event >= 0:
                    position = mod_position[event] + 1
                    delta = mod_delta[event] * mod_value[event]
                    while position <= n:
                        bit_sum[position] += delta
                        position += position & -position
                    continue

                query_id = ~event
                kind = query_type[query_id]
                if kind in (self._KTH_SMALLEST, self._KTH_LARGEST):
                    active[query_id] = 1
                    continue

                position = query_right[query_id]
                total = 0
                while position:
                    total += bit_sum[position]
                    position &= position - 1
                position = query_left[query_id]
                while position:
                    total -= bit_sum[position]
                    position &= position - 1
                if kind == self._RANGE_SUM:
                    answers[query_id] = total
                elif remaining[query_id] <= 0:
                    answers[query_id] = 0
                elif total < remaining[query_id]:
                    answers[query_id] = -1
                else:
                    active[query_id] = 1

        if not any(active):
            result = [int(answer) for answer in answers]
            self._answers = result
            return result[:]

        needs_value_sums = any(
            active[query_id] and query_type[query_id] == self._MIN_COUNT
            for query_id in range(query_count)
        )

        coordinates = sorted(set(mod_value))
        rank = {value: index for index, value in enumerate(coordinates)}
        mod_rank = array("i", (rank[value] for value in mod_value))
        del rank
        order = [
            event
            for event in events
            if event >= 0 or active[~event]
        ]

        # Each group owns a coordinate interval and a chronological slice of
        # ``order``.  Queries move to one child; modifications are copied only
        # to children whose coordinate interval contains their value.
        groups = [(0, len(coordinates), 0, len(order))]
        accumulated = [0] * query_count
        population = [
            query_right[index] - query_left[index]
            for index in range(query_count)
        ]
        bit_count = [0] * (n + 1)
        bit_sum = [0] * (n + 1) if needs_value_sums else None
        mark = [0] * (n + 1)
        token = 0

        while groups:
            next_order: list[int] = []
            next_groups: list[tuple[int, int, int, int]] = []
            for lower, upper, begin, end in groups:
                if upper - lower == 1:
                    value = coordinates[lower]
                    for order_index in range(begin, end):
                        event = order[order_index]
                        if event >= 0:
                            continue
                        query_id = ~event
                        if query_type[query_id] == self._MIN_COUNT:
                            needed = remaining[query_id]
                            answers[query_id] = (
                                accumulated[query_id]
                                + (needed + value - 1) // value
                            )
                        else:
                            answers[query_id] = value
                    continue

                middle = (lower + upper) >> 1
                token += 1
                touched: list[int] = []
                high_order: list[int] = []
                low_order: list[int] = []
                high_queries = low_queries = 0

                for order_index in range(begin, end):
                    event = order[order_index]
                    if event >= 0:
                        high = mod_rank[event] >= middle
                        if high:
                            high_order.append(event)
                        else:
                            low_order.append(event)
                            continue
                        position = mod_position[event] + 1
                        delta_count = mod_delta[event]
                        if needs_value_sums:
                            delta_sum = delta_count * mod_value[event]
                            while position <= n:
                                if mark[position] != token:
                                    mark[position] = token
                                    touched.append(position)
                                bit_count[position] += delta_count
                                bit_sum[position] += delta_sum
                                position += position & -position
                        else:
                            while position <= n:
                                if mark[position] != token:
                                    mark[position] = token
                                    touched.append(position)
                                bit_count[position] += delta_count
                                position += position & -position
                        continue

                    query_id = ~event
                    kind = query_type[query_id]
                    position = query_right[query_id]
                    high_count = 0
                    if kind == self._MIN_COUNT:
                        high_sum = 0
                        while position:
                            high_count += bit_count[position]
                            high_sum += bit_sum[position]
                            position &= position - 1
                        position = query_left[query_id]
                        while position:
                            high_count -= bit_count[position]
                            high_sum -= bit_sum[position]
                            position &= position - 1
                    else:
                        while position:
                            high_count += bit_count[position]
                            position &= position - 1
                        position = query_left[query_id]
                        while position:
                            high_count -= bit_count[position]
                            position &= position - 1
                    argument = remaining[query_id]

                    if kind == self._MIN_COUNT:
                        if high_sum >= argument:
                            high = 1
                        else:
                            high = 0
                            remaining[query_id] = argument - high_sum
                            accumulated[query_id] += high_count
                    elif kind == self._KTH_LARGEST:
                        if argument < high_count:
                            high = 1
                            population[query_id] = high_count
                        else:
                            high = 0
                            remaining[query_id] = argument - high_count
                            population[query_id] -= high_count
                    else:
                        low_count = population[query_id] - high_count
                        if argument < low_count:
                            high = 0
                            population[query_id] = low_count
                        else:
                            high = 1
                            remaining[query_id] = argument - low_count
                            population[query_id] = high_count

                    if high:
                        high_queries += 1
                        high_order.append(event)
                    else:
                        low_queries += 1
                        low_order.append(event)

                for position in touched:
                    bit_count[position] = 0
                    if needs_value_sums:
                        bit_sum[position] = 0

                if high_queries:
                    child_begin = len(next_order)
                    next_order.extend(high_order)
                    next_groups.append(
                        (middle, upper, child_begin, len(next_order))
                    )
                if low_queries:
                    child_begin = len(next_order)
                    next_order.extend(low_order)
                    next_groups.append(
                        (lower, middle, child_begin, len(next_order))
                    )

            order = next_order
            groups = next_groups

        if any(answer is None for answer in answers):
            raise RuntimeError("internal error: unresolved offline query")
        result = [int(answer) for answer in answers]
        self._answers = result
        return result[:]


def dynamic_range_min_count_sum_at_least(
    values: Iterable[int],
    queries: Iterable[tuple[int, int, int, int, int]],
    one_indexed: bool = False,
) -> list[int]:
    """Solve update-then-threshold queries in input order.

    In zero-indexed mode, each tuple is ``(index, value, left, right, target)``
    and uses ``[left, right)``.  In one-indexed mode it is ``(c, x, l, r, k)``
    and uses the inclusive range ``[l, r]``.
    """
    if type(one_indexed) is not bool:
        raise TypeError("one_indexed must be a bool")
    solver = OfflineDynamicWaveletMatrix(values)
    for query in queries:
        try:
            index, value, left, right, target = query
        except (TypeError, ValueError):
            raise ValueError(
                "each query must contain (index, value, left, right, target)"
            ) from None
        if one_indexed:
            solver.set(_integer(index, "index") - 1, value)
            solver.min_count_sum_at_least(
                _integer(left, "left") - 1, right, target
            )
        else:
            solver.set(index, value)
            solver.min_count_sum_at_least(left, right, target)
    return solver.solve()


solve_dynamic_wavelet_matrix_queries = dynamic_range_min_count_sum_at_least
