import argparse
from collections import Counter
import importlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from library_codex.benchmarks.bivariate_candidates import colored_inverse, row_inverse
from library_codex.benchmarks.compare_bivariate_methods import coefficients
from library_codex.benchmarks.library_checker import atomic_write, json_bytes


def profile(width, height, operation, mode):
    module = importlib.import_module("library_codex.fps.MultivariateFPS")
    ntt = importlib.import_module("library_codex.convolution.NTT998")
    multiplication = importlib.import_module("library_codex.convolution.MultivariateMultiplication")
    fps = importlib.import_module("library_codex.fps998.FPS")
    source = module.MultivariateFormalPowerSeries(
        coefficients(width, height, operation, "dense", 0, 92471), (width, height))
    counts = Counter()
    forward, inverse = ntt._butterfly, ntt._butterfly_inv
    old_inverse, old_sparse = module._inverse_prefix, module._sparse_2d
    old_fps = fps._butterfly
    old_multiply = multiplication._multiply998
    boundaries = []

    def counted_multiply(first, second):
        if min(len(first), len(second)) > 60:
            longer, shorter = (first, second) if len(first) >= len(second) else (second, first)
            size = len(longer) + len(shorter) - 1
            excess = size - (1 << (size.bit_length() - 1))
            lower = 1 << (size.bit_length() - 1)
            if 0 < excess <= 128 and (excess * len(shorter) <= 2 * lower or lower == 1 << 23):
                boundaries.append(dict(lengths=[len(longer), len(shorter)], excess=excess,
                                       coefficientProducts=sum(bool(x) for x in longer[-excess:]) * len(shorter)))
        return old_multiply(first, second)

    def counted_forward(values, *args, **kwargs):
        counts[("forward", len(values))] += 1
        return forward(values, *args, **kwargs)

    def counted_inverse(values, *args, **kwargs):
        counts[("inverse", len(values))] += 1
        return inverse(values, *args, **kwargs)

    try:
        ntt._butterfly = fps._butterfly = counted_forward
        ntt._butterfly_inv = counted_inverse
        multiplication._multiply998 = counted_multiply
        module._sparse_2d = lambda *a, **k: None
        if mode == "colored":
            module._inverse_prefix = colored_inverse
        elif mode == "row":
            module._inverse_prefix = row_inverse
        getattr(source, operation)()
    finally:
        ntt._butterfly, ntt._butterfly_inv = forward, inverse
        fps._butterfly = old_fps
        multiplication._multiply998 = old_multiply
        module._inverse_prefix, module._sparse_2d = old_inverse, old_sparse
    return dict(shape=[width, height], operation=operation, mode=mode,
                transforms=[dict(direction=d, length=n, count=c) for (d, n), c in sorted(counts.items())],
                calls=sum(counts.values()),
                boundaryCorrections=boundaries,
                boundaryCoefficientProducts=sum(row["coefficientProducts"] for row in boundaries),
                lengthLog2Length=sum(n * (n.bit_length()-1) * c for (_, n), c in counts.items()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shapes", nargs="+", default=["256x256", "127x521"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = [profile(*map(int, shape.split("x")), operation, mode)
             for shape in args.shapes for operation in ("inverse", "exponential")
             for mode in ("current", "colored", "row")]
    atomic_write(args.output, json_bytes(dict(cases=cases, note="transform counts only; instrumented runs are not timings")))


if __name__ == "__main__":
    main()
