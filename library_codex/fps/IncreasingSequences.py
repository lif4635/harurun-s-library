"""各位置の下限・上限を満たす広義単調増加列を数える。"""

from bisect import bisect_right

from library_codex.convolution.NTT998 import intt, multiply, ntt

DEFAULT_MOD = 998244353


def _cross(values, length, factorial, inverse):
    size = len(values)
    if length == 1:
        return [sum(values) % DEFAULT_MOD]
    if size == 1:
        return values * length
    weighted = [value * inverse[size - 1 - i] % DEFAULT_MOD
                for i, value in enumerate(values)]
    if min(size, length) <= 32:
        product = multiply(weighted, factorial[:size + length - 1])
    else:
        count = size + length - 1
        transform_size = 1 << (count - 1).bit_length()
        product = factorial[:count] + [0] * (transform_size - count)
        weighted.extend([0] * (transform_size - size))
        ntt(product)
        ntt(weighted)
        for i in range(transform_size):
            product[i] = product[i] * weighted[i] % DEFAULT_MOD
        intt(product)
    return [product[size - 1 + i] * inverse[i] % DEFAULT_MOD
            for i in range(length)]


def _parallel(values, distance, factorial, inverse):
    size = len(values)
    if distance == 0:
        result = []
        total = 0
        for value in values:
            total = (total + value) % DEFAULT_MOD
            result.append(total)
        return result
    scale = inverse[distance]
    kernel = [factorial[distance + i] * inverse[i] % DEFAULT_MOD * scale % DEFAULT_MOD
              for i in range(size)]
    return multiply(values, kernel)[:size]


def _staircase(heights, start, factorial, inverse):
    stack = [(0, heights, start)]
    result = []
    mod = DEFAULT_MOD
    while stack:
        task = stack.pop()
        stage = task[0]
        if stage == 2:
            result = task[1] + result
            continue
        heights, start = task[1:3]
        size = len(heights)
        height = heights[-1]
        if stage == 0:
            if size == 1:
                result = [start[0]] * (height + 1)
            elif size == 2:
                result = [(start[0] * min(i + 1, heights[0] + 1) + start[1]) % mod
                          for i in range(height + 1)]
            elif size * (height + 1) <= 4096:
                result = [0] * (height + 1)
                for limit, value in zip(heights, start):
                    for i in range(limit + 1):
                        value += result[i]
                        if value >= mod:
                            value -= mod
                        result[i] = value
            elif heights[0] == height:
                result = _cross(start, height + 1, factorial, inverse)
            else:
                middle = size // 2
                stack.append((1, heights, start))
                stack.append((0, heights[:middle + 1], start[:middle] + [0]))
        else:
            middle = size // 2
            split = heights[middle]
            for i in range(len(result) - 1, 0, -1):
                result[i] = (result[i] - result[i - 1]) % mod
            bottom = start[middle:]
            top = _cross(result, size - middle, factorial, inverse)
            right = _parallel(result, size - middle - 1, factorial, inverse)
            bottom_right = _cross(bottom, split + 1, factorial, inverse)
            bottom_top = _parallel(bottom, split, factorial, inverse)
            prefix = [(right[i] + bottom_right[i]) % mod for i in range(split)]
            top = [(x + y) % mod for x, y in zip(top, bottom_top)]
            for i in range(len(top) - 1, 0, -1):
                top[i] = (top[i] - top[i - 1]) % mod
            stack.append((2, prefix))
            stack.append((0, [value - split for value in heights[middle:]], top))
    return result


def _count_fast(lower, upper):
    mod = DEFAULT_MOD
    size = len(lower)
    lower = [lower[0]] + lower
    upper = [value - 1 for value in upper] + [upper[-1]]
    bound = size + upper[-1] + 2
    if bound > 1 << 22:
        raise ValueError("len(lower) + normalized width + 2 must not exceed 2^22")
    factorial = [1] * bound
    for i in range(1, bound):
        factorial[i] = factorial[i - 1] * i % mod
    inverse = [1] * bound
    inverse[-1] = pow(factorial[-1], mod - 2, mod)
    for i in range(bound - 1, 0, -1):
        inverse[i - 1] = inverse[i] * i % mod
    left = 0
    bottom = lower[0]
    right = bisect_right(lower, bottom) - 1
    top = bottom if right else upper[0]
    values = [1] + [0] * (right - left + top - bottom)
    while right != size or top != upper[-1]:
        for i in range(len(values) - 1, 0, -1):
            if i == 1 and left == 0 and bottom == 0:
                break
            values[i] = (values[i] - values[i - 1]) % mod
        if bottom == top:
            heights = [value - bottom for value in upper[left:right + 1]]
            values = _staircase(heights, values, factorial, inverse)
            left = right
            bottom = top
            top = upper[right]
        else:
            heights = [bisect_right(lower, i) - left for i in range(bottom, top + 1)]
            offset = heights[0]
            heights = [value - offset for value in heights]
            values = _staircase(heights, values, factorial, inverse)
            left = right
            bottom = top
            right = bisect_right(lower, top) - 1
    return values[-1]


def count_increasing_sequences(lower, upper, mod=DEFAULT_MOD):
    """Count lower[i] <= x[i] < upper[i] with x nondecreasing, modulo mod."""
    if mod <= 0:
        raise ValueError("mod must be positive")
    if len(lower) != len(upper):
        raise ValueError("bound lengths differ")
    size = len(lower)
    if size == 0:
        return 1 % mod
    lower = list(lower)
    upper = list(upper)
    for index in range(1, size):
        if lower[index] < lower[index - 1]:
            lower[index] = lower[index - 1]
    for index in range(size - 2, -1, -1):
        if upper[index] > upper[index + 1]:
            upper[index] = upper[index + 1]
    for left, right in zip(lower, upper):
        if left >= right:
            return 0
    if size == 1:
        return (upper[0] - lower[0]) % mod
    offset = lower[0]
    lower = [value - offset for value in lower]
    upper = [value - offset for value in upper]
    width = upper[-1]
    if width == 1:
        return 1 % mod
    if mod == DEFAULT_MOD and size * width > 4096:
        return _count_fast(lower, upper)
    values = [0] * width
    for value in range(lower[0], upper[0]):
        values[value] = 1
    for index in range(1, size):
        running = 0
        left = lower[index]
        right = upper[index]
        for value in range(width):
            running += values[value]
            if running >= mod:
                running -= mod
            values[value] = running if left <= value < right else 0
    return sum(values) % mod
