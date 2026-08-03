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
    """Return the 0-indexed k-th smallest value by iterative quickselect."""
    values = list(values)
    if not 0 <= index < len(values):
        raise IndexError("index out of range")
    left = 0
    right = len(values) - 1
    while left < right:
        pivot = values[(left + right) >> 1]
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
