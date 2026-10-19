import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import random
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
    parser.add_argument('--variants', nargs='+', default=['scan', '2048', '4096', '8192'])
    parser.add_argument('--cases', nargs='+', default=['random_00', 'near_max_00', 'many_bits_01'])
    parser.add_argument('--output', type=Path, default=ROOT / 'library_codex/benchmarks/results/factorial_queries_comparison.json')
    args = parser.parse_args()
    if args.worker:
        indices = list(map(int, sys.stdin.buffer.read().split()))[1:]
        if args.worker == 'scan':
            result = [0] * len(indices)
            previous = 0
            value = 1
            for n, i in sorted((n, i) for i, n in enumerate(indices)):
                for x in range(previous + 1, n + 1):
                    value = value * x % 998244353
                previous = n
                result[i] = value
        else:
            module = importlib.import_module('library_codex.combinatorics.FactorialQueries')
            module._BLOCK_SIZE = int(args.worker)
            result = module.factorials(indices)
        print('\n'.join(map(str, result)))
        return
    from library_codex.benchmarks.official_comparison import measure
    from library_codex.benchmarks.official_benchmark import runtime_info
    from library_codex.tools.check_library_checker import file_digest, save_json, solution
    if args.official is None or args.repeat < 1:
        parser.error('require --official and repeat >= 1')
    for variant in args.variants:
        if variant == 'scan':
            continue
        if not variant.isdigit() or int(variant) < 1 or int(variant) & (int(variant) - 1):
            parser.error('variants must be scan or positive powers of two')
    name = 'many_factorials'
    problem = args.official / 'enumerative_combinatorics' / name
    hashes = json.loads((problem / 'hash.json').read_text())
    source, _ = solution(name)
    report = dict(measuredAt=datetime.now(timezone.utc).isoformat(),
                  environment=runtime_info(sys.executable), problem=name, repeat=args.repeat,
                  sourceSha256=hashlib.sha256(source.encode()).hexdigest(), harnessSha256=file_digest(__file__),
                  checkerSha256=file_digest(problem / 'checker'),
                  upstreamRevision=subprocess.check_output(['git', '-C', str(args.official), 'rev-parse', 'HEAD'], text=True).strip(),
                  protocol='sequential fresh PyPy processes, shuffled order, startup/JIT/I/O included, official checker, GNU time RSS, 30 second measurement timeout',
                  variants=args.variants, results=[])
    with tempfile.TemporaryDirectory(prefix='harurun-factorials-') as directory:
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
                                           stdin, actual, temporary / 'rss', 30)
                    checked = subprocess.run([str(problem / 'checker'), str(stdin), str(actual), str(expected)],
                                             capture_output=True, timeout=30)
                    if checked.returncode:
                        raise ValueError(checked.stderr.decode(errors='replace'))
                    samples[variant].append(dict(seconds=seconds, peakRssKiB=rss, outputSha256=file_digest(actual)))
                    print(json.dumps(dict(case=case, variant=variant, iteration=iteration, seconds=seconds)), flush=True)
            report['results'].append(dict(case=case, inputSha256=file_digest(stdin), expectedSha256=file_digest(expected),
                implementations={variant: dict(samples=values,
                    medianSeconds=statistics.median(x['seconds'] for x in values),
                    peakRssKiB=max(x['peakRssKiB'] for x in values)) for variant, values in samples.items()}))
            save_json(args.output, report)


if __name__ == '__main__':
    main()
