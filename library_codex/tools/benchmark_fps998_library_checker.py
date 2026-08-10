"""Benchmark FPS998 operations at Library Checker input sizes."""

import argparse
import gc
import json
import random
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
    fps_exp,
    fps_inv,
    fps_log,
    fps_pow,
    fps_product,
    fps_sqrt,
    taylor_shift,
)
from library_codex.fps998.LinearRecurrence import (
    berlekamp_massey,
    linear_recurrence_nth,
)
from library_codex.fps998.MultipointEvaluation import (
    multipoint_evaluation,
    polynomial_interpolation,
)
from library_codex.fps998.PowerProjection import power_coefficient
from library_codex.polynomial.PolynomialDivision998 import poly_divmod


SIZES = {
    "quick": {
        "convolution": 1 << 14,
        "fps": 1 << 14,
        "composition": 1 << 12,
        "multipoint": 1 << 12,
        "taylor_shift": 1 << 14,
        "product": 1 << 14,
        "recurrence": 2000,
    },
    "library-checker": {
        "convolution": 524288,
        "fps": 500000,
        "composition": 131072,
        "multipoint": 131072,
        "taylor_shift": 524288,
        "product": 500000,
        "recurrence": 10000,
    },
}


def _dense(size, constant=1):
    return [constant] + [
        (index * index + 7 * index + 11) % MOD
        for index in range(1, size)
    ]


def _checksum(value):
    if isinstance(value, tuple):
        total = 0
        for item in value:
            total += sum(item) if isinstance(item, list) else item
        return total % MOD
    if isinstance(value, list):
        return sum(value) % MOD
    return value % MOD


def _build_case(name, sizes):
    if name == "convolution":
        size = sizes["convolution"]
        first = _dense(size)
        second = [
            (3 * index * index + 5 * index + 1) % MOD
            for index in range(size)
        ]
        return multiply, (first, second), size

    if name in {"inv", "log", "exp", "pow", "sqrt"}:
        size = sizes["fps"]
        dense = _dense(size)
        if name == "inv":
            return fps_inv, (dense, size), size
        if name == "log":
            return fps_log, (dense, size), size
        if name == "exp":
            dense[0] = 0
            return fps_exp, (dense, size), size
        if name == "pow":
            return fps_pow, (dense, 123456789, size), size
        root = _dense(size, 11)
        square = multiply(root, root)[:size]
        return fps_sqrt, (square, size), size

    if name == "division":
        size = sizes["fps"]
        dividend = _dense(size)
        divisor = _dense((size >> 1) + 1)
        return poly_divmod, (dividend, divisor), size

    if name in {"composition", "composition_inv", "power_projection"}:
        size = sizes["composition"]
        inner = [0, 1] + [
            (index * index + 3 * index + 7) % MOD
            for index in range(2, size)
        ]
        if name == "composition":
            outer = _dense(size)
            return fps_compose, (outer, inner, size), size
        if name == "composition_inv":
            return fps_compositional_inv, (inner, size), size
        return power_coefficient, (inner, None, size), size

    if name in {"multipoint", "interpolation"}:
        size = sizes["multipoint"]
        points = list(range(1, size + 1))
        polynomial = _dense(size)
        if name == "multipoint":
            return multipoint_evaluation, (polynomial, points), size
        values = multipoint_evaluation(polynomial, points)
        return polynomial_interpolation, (points, values), size

    if name == "taylor_shift":
        size = sizes["taylor_shift"]
        return taylor_shift, (_dense(size), 123456789), size

    if name == "product":
        size = sizes["product"]
        polynomials = [[index + 1, 1] for index in range(size)]
        return fps_product, (polynomials,), size

    if name == "berlekamp_massey":
        size = sizes["recurrence"]
        rng = random.Random(0)
        sequence = [rng.randrange(MOD) for _ in range(size)]
        return berlekamp_massey, (sequence,), size

    if name == "recurrence_nth":
        size = sizes["recurrence"] >> 1
        initial = _dense(size)
        coefficients = [
            (5 * index * index + 11) % MOD for index in range(size)
        ]
        return (
            linear_recurrence_nth,
            (initial, coefficients, 10**18 + 39),
            size,
        )
    raise ValueError(f"unknown operation: {name}")


OPERATIONS = (
    "convolution",
    "inv",
    "log",
    "exp",
    "pow",
    "sqrt",
    "division",
    "composition",
    "composition_inv",
    "power_projection",
    "multipoint",
    "interpolation",
    "taylor_shift",
    "product",
    "berlekamp_massey",
    "recurrence_nth",
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile", choices=SIZES, default="quick"
    )
    parser.add_argument("--operations", default=",".join(OPERATIONS))
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be positive")
    requested = tuple(
        name.strip() for name in args.operations.split(",") if name.strip()
    )
    unknown = set(requested) - set(OPERATIONS)
    if unknown:
        parser.error(f"unknown operations: {', '.join(sorted(unknown))}")

    rows = []
    sizes = SIZES[args.profile]
    for name in requested:
        function, arguments, size = _build_case(name, sizes)
        samples = []
        result = None
        for _ in range(args.repeat):
            gc.collect()
            started = time.perf_counter()
            result = function(*arguments)
            samples.append(time.perf_counter() - started)
        row = {
            "operation": name,
            "size": size,
            "seconds": statistics.median(samples),
            "checksum": _checksum(result),
        }
        rows.append(row)
        if not args.json:
            print(
                f"{name:20} N={size:<7} "
                f"{row['seconds']:.6f}s checksum={row['checksum']}"
            )
        del function, arguments, result
        gc.collect()
    if args.json:
        print(json.dumps({"profile": args.profile, "results": rows}, indent=2))


if __name__ == "__main__":
    main()
