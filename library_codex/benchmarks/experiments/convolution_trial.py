import importlib
import json
from pathlib import Path
import random
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


def main():
    name, height = sys.argv[1], int(sys.argv[2])
    module = importlib.import_module(name)
    rng = random.Random(92471)
    from library_codex.convolution.BinaryFieldConvolution import multiply
    for n, m in ((9, 9), (17, 31), (65, 63), (257, 129)):
        a, b = ([rng.getrandbits(64) for _ in range(size)] for size in (n, m))
        assert module.multiply(a, b) == multiply(a, b), (n, m)
    a = [rng.getrandbits(64) for _ in range(1 << height)]
    b = [rng.getrandbits(64) for _ in range(1 << height)]
    timings = {}
    if "--profile" in sys.argv:
        def instrument(key, function):
            def wrapped(*args, **kwargs):
                start = perf_counter()
                result = function(*args, **kwargs)
                timings[key] = timings.get(key, 0) + perf_counter() - start
                return result
            return wrapped
        for key in ("_convert", "_transform", "_wide_transform", "_low_transform", "_pack", "_unpack"):
            if hasattr(module, key):
                setattr(module, key, instrument(key, getattr(module, key)))
    start = perf_counter()
    result = module.multiply(a, b)
    print(json.dumps(dict(module=name, height=height, seconds=perf_counter() - start,
                          first=result[0], last=result[-1], timings=timings)), flush=True)


if __name__ == "__main__":
    main()
