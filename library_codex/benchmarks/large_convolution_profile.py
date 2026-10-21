import argparse
import importlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.tools.check_library_checker import SUITE, file_digest, save_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    path = SUITE / "drivers/convolution_mod_large.py"
    spec = importlib.util.spec_from_file_location("convolution_driver", path)
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    module = importlib.import_module("library_codex.convolution.LargeConvolution")
    timings = {}
    calls = {}

    def track(owner, name, label):
        original = getattr(owner, name)

        def timed(*args, **kwargs):
            started = perf_counter()
            result = original(*args, **kwargs)
            timings[label] = timings.get(label, 0.0) + perf_counter() - started
            calls[label] = calls.get(label, 0) + 1
            return result

        setattr(owner, name, timed)

    track(driver, "read_coefficients", "read")
    track(driver, "multiply", "multiply_including_transforms")
    track(module, "_butterfly", "forward")
    track(module, "_butterfly_inv", "inverse")
    track(module, "_butterfly8", "forward")
    track(module, "_butterfly8_inv", "inverse")
    track(module, "_pad_forward", "padded_forward_including_transforms")
    started = perf_counter()
    driver.main()
    sys.stdout.flush()
    total = perf_counter() - started
    report = dict(
        protocol="instrumented import execution; nested phase wall times, not standalone submission benchmark",
        driverSha256=file_digest(path),
        moduleSha256=file_digest(Path(module.__file__)),
        nttSha256=file_digest(Path(importlib.import_module("library_codex.convolution.NTT998").__file__)),
        runtime=sys.version, platform=platform.platform(),
        totalSeconds=total, phaseSeconds=timings, phaseCalls=calls,
        allocationAndOutputSeconds=total - timings["read"] - timings["multiply_including_transforms"],
    )
    save_json(args.report, report)
    print(json.dumps(report), file=sys.stderr)


if __name__ == "__main__":
    main()
