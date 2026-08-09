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
import library_codex.fps998.FPS as fps_module


def measure(function, repeat, *args):
    times = []
    result = None
    for _ in range(repeat):
        started = time.perf_counter()
        result = function(*args)
        times.append(time.perf_counter() - started)
    return statistics.median(times), result


def sparse_sweep(size, repeat):
    operations = (
        ("inv", fps_module._fps_inv_sparse, lambda series, terms: (
            series, size, 1, terms
        ), fps_inv),
        ("div", fps_module._fps_div_sparse, lambda series, terms: (
            dense_numerator, size, 1, terms
        ), fps_div),
        ("log", fps_module._fps_log_sparse, lambda series, terms: (
            series, size, terms
        ), fps_log),
        ("exp", fps_module._fps_exp_sparse, lambda series, terms: (
            size, terms
        ), fps_exp),
        ("pow", fps_module._fps_power_unit_sparse, lambda series, terms: (
            size, 123456789, terms
        ), fps_pow),
    )
    term_counts = (
        4, 8, 16, 24, 32, 48, 64, 96, 128, 160, 192, 256, 320, 384, 512,
    )
    dense_numerator = [
        (index * index + 5 * index + 3) % MOD for index in range(size)
    ]
    threshold_names = (
        "_SPARSE_INV_THRESHOLD",
        "_SPARSE_DIV_THRESHOLD",
        "_SPARSE_LOG_THRESHOLD",
        "_SPARSE_EXP_THRESHOLD",
        "_SPARSE_POWER_THRESHOLD",
    )
    original_thresholds = {
        name: getattr(fps_module, name) for name in threshold_names
    }
    try:
        for count in term_counts:
            if count >= size:
                continue
            unit = [0] * size
            unit[0] = 1
            terms = []
            for index in range(1, count + 1):
                value = (index * index + 13) % MOD
                unit[index] = value
                terms.append((index, value))
            for name, sparse, arguments, dense in operations:
                source = unit
                if name == "exp":
                    source = unit[:]
                    source[0] = 0
                sparse_seconds, sparse_result = measure(
                    sparse, repeat, *arguments(source, terms)
                )
                for threshold_name in threshold_names:
                    setattr(fps_module, threshold_name, -1)
                if name == "pow":
                    dense_arguments = (source, 123456789, size)
                elif name == "div":
                    dense_arguments = (dense_numerator, source, size)
                else:
                    dense_arguments = (source, size)
                dense_seconds, dense_result = measure(
                    dense, repeat, *dense_arguments
                )
                for threshold_name, threshold in original_thresholds.items():
                    setattr(fps_module, threshold_name, threshold)
                if sparse_result != dense_result:
                    raise AssertionError(f"{name} mismatch for K={count}")
                print(
                    f"{name} K={count} sparse={sparse_seconds:.6f}s "
                    f"dense={dense_seconds:.6f}s "
                    f"ratio={dense_seconds / sparse_seconds:.3f}x"
                )
    finally:
        for threshold_name, threshold in original_thresholds.items():
            setattr(fps_module, threshold_name, threshold)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=4096)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--only")
    parser.add_argument("--sparse-sweep", action="store_true")
    args = parser.parse_args()
    size = args.size
    repeat = args.repeat
    if args.sparse_sweep:
        sparse_sweep(size, repeat)
        return
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
