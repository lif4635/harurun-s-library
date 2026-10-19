import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import runpy
import statistics
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker')
    parser.add_argument('--official', type=Path)
    parser.add_argument('--repeat', type=int, default=5)
    parser.add_argument('--variants', nargs='+', default=['generic', '8', '16', '32'])
    parser.add_argument('--cases', nargs='+', default=['max_random_00', 'many_affine_queries_00', 'issue_1298_00'])
    parser.add_argument('--output', type=Path, default=ROOT / 'library_codex/benchmarks/results/rectangle_affine_sum_comparison.json')
    args = parser.parse_args()
    name = 'dynamic_point_set_rectangle_affine_rectangle_sum'
    if args.worker:
        if args.worker == 'generic':
            runpy.run_path(str(ROOT / 'library_codex/benchmarks/rectangle_affine_sum_generic.py'), run_name='__main__')
        else:
            import importlib
            module = importlib.import_module('library_codex.spatial_structure.RectangleAffineSum')
            module._ADAPTIVE_AXES = not args.worker.startswith('alternating_')
            module._BUCKET_SIZE = int(args.worker.removeprefix('alternating_'))
            runpy.run_path(str(ROOT / 'verify/library_checker/drivers' / (name + '.py')), run_name='__main__')
        return
    from library_codex.benchmarks.official_comparison import measure
    from library_codex.benchmarks.official_benchmark import runtime_info
    from library_codex.tools.check_library_checker import file_digest, save_json, solution
    if args.official is None or args.repeat < 1:
        parser.error('require --official and repeat >= 1')
    if any(v != 'generic' and (not v.removeprefix('alternating_').isdigit() or int(v.removeprefix('alternating_')) < 1) for v in args.variants):
        parser.error('variants must be generic or a positive bucket size')
    problem = args.official / 'data_structure' / name
    hashes = json.loads((problem / 'hash.json').read_text())
    source, _ = solution(name)
    report = dict(measuredAt=datetime.now(timezone.utc).isoformat(),
                  environment=runtime_info(sys.executable), problem=name, repeat=args.repeat,
                  sourceSha256=hashlib.sha256(source.encode()).hexdigest(), harnessSha256=file_digest(__file__),
                  genericSourceSha256=file_digest(ROOT / 'library_codex/benchmarks/rectangle_affine_sum_generic.py'),
                  checkerSha256=file_digest(problem / 'checker'),
                  upstreamRevision=subprocess.check_output(['git', '-C', str(args.official), 'rev-parse', 'HEAD'], text=True).strip(),
                  protocol='sequential fresh PyPy processes, shuffled order, startup/JIT/I/O included, official checker, GNU time RSS, 90 second measurement timeout',
                  variants=args.variants, results=[])
    with tempfile.TemporaryDirectory(prefix='harurun-rectangle-') as directory:
        temporary = Path(directory)
        for case in args.cases:
            if Path(case).name != case:
                raise ValueError('invalid case')
            stdin = problem / 'in' / (case + '.in')
            expected = problem / 'out' / (case + '.out')
            for path in (stdin, expected):
                if file_digest(path) != hashes.get(path.name):
                    raise ValueError('official case hash mismatch')
            samples = {variant: [] for variant in args.variants}
            for iteration in range(args.repeat):
                order = list(samples)
                random.Random(20261019 + iteration).shuffle(order)
                for variant in order:
                    actual = temporary / 'actual'
                    seconds, rss = measure([sys.executable, str(Path(__file__).resolve()), '--worker', variant],
                                           stdin, actual, temporary / 'rss', 90)
                    checked = subprocess.run([str(problem / 'checker'), str(stdin), str(actual), str(expected)],
                                             capture_output=True, timeout=30)
                    if checked.returncode:
                        raise ValueError(checked.stderr.decode(errors='replace'))
                    samples[variant].append(dict(seconds=seconds, peakRssKiB=rss, outputSha256=file_digest(actual)))
                    print(json.dumps(dict(case=case, variant=variant, iteration=iteration, seconds=seconds)), flush=True)
            row = dict(case=case, inputSha256=file_digest(stdin), expectedSha256=file_digest(expected),
                       implementations={variant: dict(samples=values,
                           medianSeconds=statistics.median(x['seconds'] for x in values),
                           peakRssKiB=max(x['peakRssKiB'] for x in values)) for variant, values in samples.items()})
            report['results'].append(row)
            save_json(args.output, report)


if __name__ == '__main__':
    main()
