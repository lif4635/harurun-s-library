"""静的配列の区間k番目を一括処理し、Wavelet Matrixの全段を保持せずに答える。"""


def offline_range_kth(values, queries):
    """queriesの(left, right, k)に対し、values[left:right]のk番目の値を返す。"""
    queries = list(queries)
    if not queries:
        return []
    n, q = len(values), len(queries)
    left, right, ranks = [0] * q, [0] * q, [0] * q
    for i, (l, r, k) in enumerate(queries):
        if not 0 <= l < r <= n or not 0 <= k < r - l:
            raise ValueError("invalid range or rank")
        left[i], right[i], ranks[i] = l, r, k
    increasing = all(values[i - 1] <= values[i] for i in range(1, n))
    if increasing:
        return [values[l + k] for l, r, k in queries]
    decreasing = all(values[i - 1] >= values[i] for i in range(1, n))
    if decreasing:
        return [values[r - 1 - k] for l, r, k in queries]
    alphabet = sorted(set(values))
    codes = {value: i for i, value in enumerate(alphabet)}
    current = [codes[value] for value in values]
    prefix, following, answer = [0] * (n + 1), [0] * n, [0] * q
    for bit in range((len(alphabet) - 1).bit_length() - 1, -1, -1):
        mask, count = 1 << bit, 0
        for i, value in enumerate(current):
            count += bool(value & mask)
            prefix[i + 1] = count
        zeros = n - count
        for i in range(q):
            l, r = left[i], right[i]
            a, b = prefix[l], prefix[r]
            zero_count = r - l - b + a
            if ranks[i] < zero_count:
                left[i], right[i] = l - a, r - b
            else:
                left[i], right[i] = zeros + a, zeros + b
                ranks[i] -= zero_count
                answer[i] |= mask
        if bit:
            zero, one = 0, zeros
            for value in current:
                if value & mask:
                    following[one] = value
                    one += 1
                else:
                    following[zero] = value
                    zero += 1
            current, following = following, current
    return [alphabet[value] for value in answer]
