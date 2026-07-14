def count_distinct_subsequences(sequence, mod=None, include_empty=False):
    if mod is not None and mod <= 0:
        raise ValueError("mod must be positive")
    total = 1
    last = {}
    fallback = None
    for value in sequence:
        if fallback is None:
            try:
                previous = last.get(value, 0)
                last[value] = total
            except TypeError:
                fallback = list(last.items())
                last = None
                previous = 0
                for index, (key, old_total) in enumerate(fallback):
                    if key == value:
                        previous = old_total
                        fallback[index] = (key, total)
                        break
                else:
                    fallback.append((value, total))
        else:
            previous = 0
            for index, (key, old_total) in enumerate(fallback):
                if key == value:
                    previous = old_total
                    fallback[index] = (key, total)
                    break
            else:
                fallback.append((value, total))
        total = (total << 1) - previous
        if mod is not None:
            total %= mod
    if include_empty:
        return total
    result = total - 1
    return result % mod if mod is not None else result


number_of_subsequences = count_distinct_subsequences


def is_subsequence(subsequence, sequence):
    iterator = iter(sequence)
    for value in subsequence:
        for current in iterator:
            if current == value:
                break
        else:
            return False
    return True
