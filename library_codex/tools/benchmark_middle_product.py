"""Compare the specialized 998244353 middle product with full convolution."""

import argparse
import random
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.convolution.MiddleProduct import middle_product
from library_codex.convolution.NTT import convolution


def median_time(function, repeats):
    samples = []
    result = None
    for _ in range(repeats):
        started = time.perf_counter()
        result = function()
        samples.append(time.perf_counter() - started)
    return result, statistics.median(samples)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--first-size", type=int, default=131_072)
    parser.add_argument("--second-size", type=int, default=65_536)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if not 0 < args.second_size <= args.first_size:
        parser.error("require 0 < second-size <= first-size")

    rng = random.Random(20260810)
    first = [rng.randrange(998244353) for _ in range(args.first_size)]
    second = [rng.randrange(998244353) for _ in range(args.second_size)]
    specialized, specialized_time = median_time(
        lambda: middle_product(first, second), args.repeats
    )
    full, full_time = median_time(
        lambda: convolution(first, list(reversed(second)))[
            args.second_size - 1:args.first_size
        ],
        args.repeats,
    )
    if specialized != full:
        raise AssertionError("middle product differs from full convolution")
    print("middle_product_ms,full_convolution_ms,ratio")
    print(
        "%.3f,%.3f,%.3f"
        % (specialized_time * 1000, full_time * 1000, specialized_time / full_time)
    )


if __name__ == "__main__":
    main()
