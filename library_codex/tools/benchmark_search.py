"""Reproducible benchmark for order-statistic selection."""

import argparse
import random
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.algorithm.Search import kth_element


def measure(function, values, index, repeats):
    samples = []
    expected = sorted(values)[index]
    for _ in range(repeats):
        started = time.perf_counter()
        actual = function(values, index)
        samples.append(time.perf_counter() - started)
        if actual != expected:
            raise AssertionError((actual, expected))
    return statistics.median(samples)


def sorted_select(values, index):
    return sorted(values)[index]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=200_000)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()

    rng = random.Random(20260810)
    random_values = [rng.randrange(1 << 60) for _ in range(args.size)]
    cases = {
        "random": random_values,
        "sorted": sorted(random_values),
        "reversed": sorted(random_values, reverse=True),
        "duplicates": [rng.randrange(64) for _ in range(args.size)],
    }
    index = args.size // 2
    print("case,kth_element_ms,sorted_ms,ratio")
    for name, values in cases.items():
        quick = measure(kth_element, values, index, args.repeats)
        ordered = measure(sorted_select, values, index, args.repeats)
        print(
            "%s,%.3f,%.3f,%.3f"
            % (name, quick * 1000, ordered * 1000, quick / ordered)
        )


if __name__ == "__main__":
    main()
