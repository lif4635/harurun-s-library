import argparse
import json
import platform
import sys
from pathlib import Path
from statistics import median
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.optimization.MongeShortestPaths import monge_d_edge_shortest_path
from library_codex.optimization.MonotoneMinima import monotone_minima


def previous_implementation(n, k, cost):
    infinity = 10 ** 100
    previous = [0] + [infinity] * n
    for _ in range(k):
        def value(j, i):
            if i >= j or previous[i] == infinity:
                return infinity
            return previous[i] + cost(i, j)

        indices = monotone_minima(n + 1, n + 1, value=value)
        current = [infinity] * (n + 1)
        for j in range(1, n + 1):
            i = indices[j]
            if i < j and previous[i] != infinity:
                current[j] = previous[i] + cost(i, j)
        previous = current
    return previous[n]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", type=int, default=[2000, 8000])
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--biased", action="store_true")
    args = parser.parse_args()
    print(json.dumps({"runtime": platform.python_implementation(), "version": platform.python_version()}))
    for n in args.sizes:
        k = n // 2
        cost = (lambda i, j: (j - i) ** 2 + ((j * 7919) % 2001 - 1000)) if args.biased else (lambda i, j: (j - i) ** 2)
        q, r = divmod(n, k)
        expected = (k - r) * q * q + r * (q + 1) ** 2
        if args.biased:
            expected = previous_implementation(n, k, cost)
        results = {}
        for name, solve in (("previous", previous_implementation), ("current", monge_d_edge_shortest_path)):
            for _ in range(3):
                solve(128, 64, cost)
            times = []
            for _ in range(args.repeat):
                start = perf_counter()
                assert solve(n, k, cost) == expected
                times.append(perf_counter() - start)
            results[name] = median(times)
        print(json.dumps({"n": n, "k": k, "biased": args.biased, "seconds": results,
                          "speedup": results["previous"] / results["current"]}), flush=True)


if __name__ == "__main__":
    main()
