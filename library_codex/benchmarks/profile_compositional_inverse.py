import argparse
import hashlib
import io
import json
from pathlib import Path
import runpy
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.fps998 import Composition, PowerProjection


def measure(call, namespace, names, values):
    totals = {}
    originals = {name: namespace[name] for name in names}

    def wrap(name, function):
        def measured(*args, **kwargs):
            started = perf_counter()
            result = function(*args, **kwargs)
            elapsed = perf_counter() - started
            totals[name] = totals.get(name, 0) + elapsed
            return result
        return measured

    for name, function in originals.items():
        namespace[name] = wrap(name, function)
    try:
        started = perf_counter()
        result = call(values[:])
        totals["total"] = perf_counter() - started
    finally:
        namespace.update(originals)
    return result, totals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--reviewed-sha256", required=True)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    if hashlib.sha256(args.reference.read_bytes()).hexdigest() != args.reviewed_sha256:
        raise ValueError("reference source differs from the reviewed hash")
    saved_input, saved_output = sys.stdin, sys.stdout
    try:
        sys.stdin, sys.stdout = io.StringIO("2\n0 1\n"), io.StringIO()
        reference = runpy.run_path(str(args.reference))
    finally:
        sys.stdin, sys.stdout = saved_input, saved_output
    with args.input.open() as stream:
        size = int(stream.readline())
        values = list(map(int, stream.readline().split()))
    first, reference_times = measure(reference["fps_compsite_inv"], reference["fps_compsite_inv"].__globals__,
                                     ("power_projection", "fps_pow"), values)
    second, library_times = measure(Composition.fps_compositional_inv, Composition.__dict__,
                                   ("power_coefficient", "fps_log", "fps_exp"), values)
    assert first == second
    _, transform_times = measure(Composition.fps_compositional_inv, PowerProjection.__dict__,
                                ("_butterfly", "_butterfly_inv"), values)
    print(json.dumps(dict(size=size, reference=reference_times, library=library_times,
                          projectionTransforms=transform_times), indent=2))


if __name__ == "__main__":
    main()
