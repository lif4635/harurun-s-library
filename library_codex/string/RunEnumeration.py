from library_codex.string.ZAlgorithm import z_algorithm


def run_enumerate(sequence):
    n = len(sequence)
    if n < 2:
        return []
    by_period = [None] * (n + 1)
    stack = [(0, n)]

    def add_crossing(left, right, middle, reflected):
        left_size = len(left)
        right_size = len(right)
        reversed_left = left[::-1]
        joined = right + left + right
        left_z = z_algorithm(reversed_left)
        joined_z = z_algorithm(joined)
        base = left_size + right_size
        for period in range(1, left_size + 1):
            if period == left_size:
                left_extension = period
            else:
                left_extension = left_z[period] + period
                if left_extension > left_size:
                    left_extension = left_size
            right_extension = joined_z[base - period]
            if right_extension > right_size:
                right_extension = right_size
            if left_extension + right_extension < period << 1:
                continue
            if reflected:
                interval = (
                    middle - right_extension,
                    middle + left_extension,
                )
            else:
                interval = (
                    middle - left_extension,
                    middle + right_extension,
                )
            bucket = by_period[period]
            if bucket is None:
                by_period[period] = [interval]
            else:
                bucket.append(interval)

    while stack:
        left_bound, right_bound = stack.pop()
        size = right_bound - left_bound
        if size <= 1:
            continue
        if size == 2:
            if sequence[left_bound] == sequence[left_bound + 1]:
                bucket = by_period[1]
                interval = (left_bound, right_bound)
                if bucket is None:
                    by_period[1] = [interval]
                else:
                    bucket.append(interval)
            continue
        middle = (left_bound + right_bound) >> 1
        stack.append((left_bound, middle))
        stack.append((middle, right_bound))
        left = sequence[left_bound:middle]
        right = sequence[middle:right_bound]
        add_crossing(left, right, middle, False)
        add_crossing(right[::-1], left[::-1], middle, True)

    result = []
    done = set()
    width = n + 1
    for period in range(1, n + 1):
        intervals = by_period[period]
        if intervals is None:
            continue
        intervals.sort(key=lambda interval: (interval[0], -interval[1]))
        covered_right = -1
        for left, right in intervals:
            if covered_right >= right:
                continue
            covered_right = right
            key = left * width + right
            if key in done:
                continue
            done.add(key)
            result.append((period, left, right))
    return result


enumerate_runs = run_enumerate
runs = run_enumerate
