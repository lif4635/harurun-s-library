import argparse
import json
import platform
import random
import sys
from pathlib import Path
from statistics import median
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.optimization.MongeShortestPaths import (
    _monge_fixed_layers, _monge_penalty,
    monge_d_edge_shortest_path, monge_shortest_paths,
)


def golden_maximum(value, lower, upper):
    left = lower - 1
    small, large = 1, 2
    while large < upper - lower + 2:
        small, large = large, small + large
    point, right = left + large - small, left + large
    best = value(point)
    while left + right != 2 * point:
        other = left + right - point
        if other > upper:
            left, right = other, left
        else:
            candidate = value(other)
            if best > candidate:
                left, right = other, left
            else:
                left, point, best = point, other, candidate
    return best


def objective(n, k, cost, penalty):
    def shifted(i, j):
        value = cost(i, j)
        if not isinstance(value, int):
            raise TypeError("integer costs required")
        return value + penalty

    return monge_shortest_paths(n, shifted)[n] - penalty * k


def golden_bounded(n, k, cost, bound):
    return golden_maximum(lambda p: objective(n, k, cost, p), -bound, bound)


def binary_bounded(n, k, cost, bound):
    lower, upper = -bound, bound
    while upper - lower > 1:
        penalty = (lower + upper) // 2
        value, count = _monge_penalty(n, cost, penalty)
        if count == k:
            return value - penalty * k
        if count > k:
            lower = penalty
        else:
            upper = penalty
    return _monge_penalty(n, cost, upper)[0] - upper * k


class BudgetExceeded(Exception):
    pass


def golden_auto(n, k, cost, bound=None):
    if k <= 2 or k == n or not 0 <= k <= n:
        return monge_d_edge_shortest_path(n, k, cost)
    attempts = 0

    def value(p):
        nonlocal attempts
        if attempts >= k:
            raise BudgetExceeded
        attempts += 1
        return objective(n, k, cost, p)

    try:
        center = value(0)
        next_value = value(1)
        if next_value == center:
            return center
        direction = 1
        if next_value < center:
            next_value = value(-1)
            if next_value <= center:
                return center
            direction = -1
        previous, point = 0, direction
        while True:
            other = 2 * point
            other_value = value(other)
            if other_value <= next_value:
                return golden_maximum(value, min(previous, other), max(previous, other))
            previous, point, next_value = point, other, other_value
    except BudgetExceeded:
        return _monge_fixed_layers(n, k, cost, float("inf"))


def cases(n):
    yield "square", n // 2, lambda i, j: (j - i) ** 2, n * n + 1
    yield "square_small_k", 7, lambda i, j: (j - i) ** 2, n * n + 1
    yield "biased", n // 2, lambda i, j: (j - i) ** 2 + (j * 7919) % 2001 - 1000, n * n + 2001
    yield "negative_penalty", n // 2, lambda i, j: (j - i) ** 2 + 1000000, n * n + 1000001
    yield "positive_penalty", n // 2, lambda i, j: (j - i) ** 2 - 1000000, n * n + 1000001
    yield "ties", n // 2, lambda i, j: 0, 1
    yield "bigint", n // 2, lambda i, j: 10 ** 30 * (j - i) ** 2, 10 ** 30 * (n * n + 1)
    rng = random.Random(912)
    prefix = [0]
    for _ in range(n):
        prefix.append(prefix[-1] + rng.randrange(1, 10))
    yield "irregular", n // 3, lambda i, j: (prefix[j] - prefix[i]) ** 2, prefix[-1] ** 2 + 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", type=int, nargs="+", default=[512, 4096])
    parser.add_argument("--repeat", type=int, default=7)
    args = parser.parse_args()
    methods = {
        "binary_bounded": binary_bounded,
        "golden_bounded": golden_bounded,
        "binary_auto": lambda n, k, c, b: monge_d_edge_shortest_path(n, k, c),
        "golden_auto": golden_auto,
    }
    print(json.dumps({"runtime": platform.python_implementation(), "version": platform.python_version()}), flush=True)
    for n in args.sizes:
        for label, k, cost, bound in cases(n):
            expected = monge_d_edge_shortest_path(n, k, cost)
            for method in methods.values():
                for _ in range(3):
                    assert method(n, k, cost, bound) == expected
            samples = {name: [] for name in methods}
            names = list(methods)
            for repeat in range(args.repeat):
                order = names[repeat % len(names):] + names[:repeat % len(names)]
                for name in order:
                    start = perf_counter()
                    assert methods[name](n, k, cost, bound) == expected
                    samples[name].append(perf_counter() - start)
            calls = {}
            for name, method in methods.items():
                count = 0

                def counted_cost(i, j):
                    nonlocal count
                    count += 1
                    return cost(i, j)

                assert method(n, k, counted_cost, bound) == expected
                calls[name] = count
            print(json.dumps({"case": label, "n": n, "k": k, "costCalls": calls, "milliseconds": {
                name: round(median(times) * 1000, 3) for name, times in samples.items()
            }}), flush=True)


if __name__ == "__main__":
    main()
