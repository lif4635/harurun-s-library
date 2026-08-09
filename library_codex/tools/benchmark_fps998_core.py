"""Benchmark the public 998244353 FPS operations on one deterministic input."""

import argparse
import statistics
import sys
import time
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[2]))

from library_codex.convolution.NTT998 import MOD, multiply
from library_codex.fps998.Composition import (
    fps_compose,
    fps_compositional_inv,
)
from library_codex.fps998.FPS import (
    fps_div,
    fps_exp,
    fps_inv,
    fps_log,
    fps_pow,
    fps_sqrt,
)
from library_codex.fps998.LinearRecurrence import linear_recurrence_nth
from library_codex.fps998.PowerProjection import power_coefficient


def measure(function, repeat, *args):
    times = []
    result = None
    for _ in range(repeat):
        started = time.perf_counter()
        result = function(*args)
        times.append(time.perf_counter() - started)
    return statistics.median(times), result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=4096)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--only")
    args = parser.parse_args()
    size = args.size
    repeat = args.repeat
    dense = [1] + [
        (index * index + 5 * index + 3) % MOD
        for index in range(1, size)
    ]
    zero = [0] + dense[1:]
    root = [
        (index * index + 7 * index + 11) % MOD
        for index in range(size)
    ]
    square = multiply(root, root)[:size]
    outer = [
        (3 * index * index + index + 9) % MOD
        for index in range(size)
    ]
    inner = [0, 1] + [
        (index * index + 3 * index + 7) % MOD
        for index in range(2, size)
    ]
    sparse_unit = [0] * size
    sparse_zero = [0] * size
    sparse_unit[0] = 1
    for index in (1, 3, 17, 65, 257, 1025, 4097):
        if index < size:
            value = (index * index + 13) % MOD
            sparse_unit[index] = value
            sparse_zero[index] = value
    recurrence_initial = dense
    recurrence_coefficients = [
        (5 * index * index + 11) % MOD for index in range(size)
    ]
    cases = (
        ("inv", fps_inv, (dense, size)),
        ("log", fps_log, (dense, size)),
        ("exp", fps_exp, (zero, size)),
        ("pow", fps_pow, (dense, 123456789, size)),
        ("sqrt", fps_sqrt, (square, size)),
        ("div", fps_div, (dense, dense, size)),
        ("compose", fps_compose, (outer, inner, size)),
        ("compose_inv", fps_compositional_inv, (inner, size)),
        ("power_coeff", power_coefficient, (inner, None, size)),
        (
            "linear_recurrence",
            linear_recurrence_nth,
            (recurrence_initial, recurrence_coefficients, 10**18 + 39),
        ),
        ("sparse_log", fps_log, (sparse_unit, size)),
        ("sparse_exp", fps_exp, (sparse_zero, size)),
        ("sparse_pow", fps_pow, (sparse_unit, 123456789, size)),
    )
    for name, function, arguments in cases:
        if args.only is not None and name != args.only:
            continue
        seconds, result = measure(function, repeat, *arguments)
        if isinstance(result, list):
            checksum = sum(result) % MOD
        else:
            checksum = result
        print(f"{name}={seconds:.6f}s checksum={checksum}")


if __name__ == "__main__":
    main()
