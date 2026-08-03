"""0/1 knapsackを分枝限定法で解く。"""

def knapsack_branch_and_bound(values, weights, capacity):
    """Exact 0/1 knapsack using an iterative fractional-bound search."""
    if len(values) != len(weights) or capacity < 0:
        raise ValueError("invalid knapsack input")
    free_value = 0
    items = []
    for value, weight in zip(values, weights):
        if weight < 0:
            raise ValueError("weights must be nonnegative")
        if value <= 0:
            continue
        if weight == 0:
            free_value += value
        elif weight <= capacity:
            items.append((value, weight))
    items.sort(key=lambda item: item[0] / item[1], reverse=True)
    size = len(items)

    def bound(index, value, remaining):
        result = value
        while index < size and remaining:
            item_value, item_weight = items[index]
            if item_weight <= remaining:
                result += item_value
                remaining -= item_weight
                index += 1
            else:
                return result + item_value * remaining / item_weight
        return result

    best = free_value
    stack = [(0, free_value, capacity)]
    while stack:
        index, value, remaining = stack.pop()
        if index == size:
            if value > best:
                best = value
            continue
        if bound(index, value, remaining) <= best:
            continue
        item_value, item_weight = items[index]
        stack.append((index + 1, value, remaining))
        if item_weight <= remaining:
            candidate = value + item_value
            if candidate > best:
                best = candidate
            stack.append((index + 1, candidate, remaining - item_weight))
    return best

