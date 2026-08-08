"""Measure the fixed-998 FPS path against the parameterized implementation."""

import argparse
import statistics
import sys
import time
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[2]))


def load_backend(name):
    if name == "specialized":
        from library_codex.convolution.NTT998 import multiply
        from library_codex.fps998.Composition import fps_compositional_inv
        from library_codex.fps998.FPS import fps_exp, fps_inv
        return multiply, fps_inv, fps_exp, fps_compositional_inv
    from library_codex.fps.PolynomialComposition import (
        fps_compositional_inverse,
    )
    from library_codex.fps.FormalPowerSeries import (
        fps_exponential,
        fps_inverse,
        fps_multiply,
    )

    def compositional_inverse(series, degree):
        return fps_compositional_inverse(series, degree, 998244353)

    return fps_multiply, fps_inverse, fps_exponential, compositional_inverse


def measure(function, repeat, *args):
    measurements = []
    result = None
    for _ in range(repeat):
        started = time.perf_counter()
        result = function(*args)
        measurements.append(time.perf_counter() - started)
    return statistics.median(measurements), result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("specialized", "generic"), required=True)
    parser.add_argument("--size", type=int, default=16384)
    parser.add_argument("--composition-size", type=int, default=4096)
    parser.add_argument("--repeat", type=int, default=3)
    args = parser.parse_args()
    multiply, inverse, exponential, compositional_inverse = load_backend(
        args.backend
    )
    size = args.size
    source = [(index * index + 3 * index + 1) % 998244353 for index in range(size)]
    invertible = source[:]
    invertible[0] = 1
    logarithm = source[:]
    logarithm[0] = 0
    composition_source = [0, 1] + [
        (index * index + 3 * index + 7) % 998244353
        for index in range(2, args.composition_size)
    ]

    multiply(source, source)
    inverse(invertible, size)
    exponential(logarithm, size)
    compositional_inverse(composition_source, args.composition_size)

    multiply_seconds, product = measure(multiply, args.repeat, source, source)
    inverse_seconds, reciprocal = measure(inverse, args.repeat, invertible, size)
    exponential_seconds, exponentiated = measure(
        exponential, args.repeat, logarithm, size
    )
    composition_seconds, compositional_reciprocal = measure(
        compositional_inverse,
        args.repeat,
        composition_source,
        args.composition_size,
    )
    total = (
        multiply_seconds
        + inverse_seconds
        + exponential_seconds
        + composition_seconds
    )
    checksum = (
        product[size - 1]
        + reciprocal[size - 1]
        + exponentiated[size - 1]
        + compositional_reciprocal[-1]
    ) % 998244353
    print(
        f"{args.backend}: multiply={multiply_seconds:.6f}s "
        f"inverse={inverse_seconds:.6f}s exp={exponential_seconds:.6f}s "
        f"composition_inv={composition_seconds:.6f}s "
        f"total={total:.6f}s checksum={checksum}"
    )


if __name__ == "__main__":
    main()
