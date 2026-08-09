"""Boundary binary search and order-statistic selection."""


def binary_search_int(predicate, false_value, true_value):
    """Return the true-side integer boundary from known false/true endpoints."""
    while abs(true_value - false_value) > 1:
        middle = (true_value + false_value) // 2
        if predicate(middle):
            true_value = middle
        else:
            false_value = middle
    return true_value


def binary_search_float(predicate, false_value, true_value, iterations=80):
    """Approximate the true-side real boundary by fixed-count bisection."""
    for _ in range(iterations):
        middle = (false_value + true_value) * 0.5
        if predicate(middle):
            true_value = middle
        else:
            false_value = middle
    return true_value


def kth_element(values, index):
    """Return the 0-indexed k-th smallest value by introspective quickselect."""
    values = list(values)
    size = len(values)
    if not 0 <= index < size:
        raise IndexError("index out of range")

    ascending = True
    descending = True
    for position in range(1, size):
        previous = values[position - 1]
        current = values[position]
        if previous > current:
            ascending = False
        elif previous < current:
            descending = False
        if not ascending and not descending:
            break
    if ascending:
        return values[index]
    if descending:
        return values[size - 1 - index]

    left = 0
    right = size - 1
    depth_limit = 2 * size.bit_length()
    while left < right:
        if right - left <= 64 or depth_limit == 0:
            remaining = values[left:right + 1]
            remaining.sort()
            return remaining[index - left]
        depth_limit -= 1

        middle = (left + right) >> 1
        first = values[left]
        center = values[middle]
        last = values[right]
        if first < center:
            pivot = center if center < last else (last if first < last else first)
        else:
            pivot = first if first < last else (last if center < last else center)
        lower = left
        current = left
        upper = right
        while current <= upper:
            if values[current] < pivot:
                values[lower], values[current] = values[current], values[lower]
                lower += 1
                current += 1
            elif values[current] > pivot:
                values[current], values[upper] = values[upper], values[current]
                upper -= 1
            else:
                current += 1
        if index < lower:
            right = lower - 1
        elif index > upper:
            left = upper + 1
        else:
            return pivot
    return values[left]
