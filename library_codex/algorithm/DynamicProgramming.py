"""0/1 knapsack and subset-sum algorithms."""


def knapsack_01(weights, values, capacity):
    """Return the best exact-weight value for every weight up to capacity."""
    if len(weights) != len(values):
        raise ValueError("weights and values have different lengths")
    dp = [None] * (capacity + 1)
    dp[0] = 0
    for weight, value in zip(weights, values):
        if weight < 0:
            raise ValueError("weights must be nonnegative")
        for total in range(capacity, weight - 1, -1):
            previous = dp[total - weight]
            if previous is not None:
                candidate = previous + value
                if dp[total] is None or candidate > dp[total]:
                    dp[total] = candidate
    return dp


def knapsack_01_max(weights, values, capacity):
    """Return the best value whose total weight is at most capacity."""
    return max(
        value
        for value in knapsack_01(weights, values, capacity)
        if value is not None
    )


def subset_sum_possible(values, limit=None):
    """Return an integer bitset whose bit i says whether sum i is reachable."""
    bits = 1
    mask = None if limit is None else (1 << (limit + 1)) - 1
    for value in values:
        if value < 0:
            raise ValueError("values must be nonnegative")
        bits |= bits << value
        if mask is not None:
            bits &= mask
    return bits


def subset_sum_restore(values, target):
    """Return indices of one subset totaling target, or None."""
    values = list(values)
    reachable = 1
    previous_item = [-1] * (target + 1)
    previous_sum = [-1] * (target + 1)
    mask = (1 << (target + 1)) - 1
    for item, value in enumerate(values):
        if value < 0:
            raise ValueError("values must be nonnegative")
        new = (reachable << value) & ~reachable & mask
        bits = new
        while bits:
            bit = bits & -bits
            total = bit.bit_length() - 1
            previous_item[total] = item
            previous_sum[total] = total - value
            bits ^= bit
        reachable |= new
    if not reachable >> target & 1:
        return None
    result = []
    while target:
        result.append(previous_item[target])
        target = previous_sum[target]
    result.reverse()
    return result
