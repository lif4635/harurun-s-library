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


def skip_identity_pull(self, node):
    left, right = self._left[node], self._right[node]
    self._size[node] = self._size[left] + self._size[right] + 1
    op, value = self.op, self._values[node]
    if not left:
        self._forward[node] = op(value, self._forward[right]) if right else value
        self._backward[node] = op(self._backward[right], value) if right else value
    elif not right:
        self._forward[node] = op(self._forward[left], value)
        self._backward[node] = op(value, self._backward[left])
    else:
        self._forward[node] = op(op(self._forward[left], value), self._forward[right])
        self._backward[node] = op(op(self._backward[right], value), self._backward[left])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', choices=('skip_identity', 'full_pull'))
    parser.add_argument('--official', type=Path)
    parser.add_argument('--repeat', type=int, default=5)
    parser.add_argument('--cases', nargs='+', default=['max_random_01', 'many_1_query_01', 'many_3_query_01'])
    args = parser.parse_args()
    driver = ROOT / 'verify/library_checker/drivers/point_set_range_sort_range_composite.py'
    if args.worker:
        from library_codex.sequence_structure.SortableArray import SortableArray
        if args.worker == 'skip_identity':
            SortableArray._pull = skip_identity_pull
        runpy.run_path(str(driver), run_name='__main__')
        return
    from library_codex.benchmarks.official_comparison import measure
    from library_codex.benchmarks.official_benchmark import runtime_info
    from library_codex.tools.check_library_checker import file_digest, save_json, solution
    if args.official is None or args.repeat < 1:
        parser.error('require --official and repeat >= 1')
    name = 'point_set_range_sort_range_composite'
    problem = args.official / 'data_structure' / name
    hashes = json.loads((problem / 'hash.json').read_text())
    source, _ = solution(name)
    report = dict(measuredAt=datetime.now(timezone.utc).isoformat(),
                  environment=runtime_info(sys.executable), problem=name, repeat=args.repeat,
                  sourceSha256=hashlib.sha256(source.encode()).hexdigest(),
                  harnessSha256=hashlib.sha256(Path(__file__).read_text().encode()).hexdigest(),
                  checkerSha256=file_digest(problem / 'checker'),
                  upstreamRevision=subprocess.check_output(['git', '-C', str(args.official), 'rev-parse', 'HEAD'], text=True).strip(),
                  protocol='sequential fresh PyPy processes, shuffled order, startup/JIT/I/O included, official checker, GNU time RSS',
                  variants={'skip_identity': 'skip identity operands', 'full_pull': 'always compute four monoid products; adopted'}, results=[])
    output = ROOT / 'library_codex/benchmarks/results/sortable_array_comparison.json'
    with tempfile.TemporaryDirectory(prefix='harurun-sortable-') as directory:
        temporary = Path(directory)
        for case in args.cases:
            if Path(case).name != case:
                raise ValueError('invalid case')
            stdin = problem / 'in' / (case + '.in')
            expected = problem / 'out' / (case + '.out')
            for path in (stdin, expected):
                if file_digest(path) != hashes.get(path.name):
                    raise ValueError('official case hash mismatch')
            samples = {variant: [] for variant in report['variants']}
            for iteration in range(args.repeat):
                order = list(samples)
                random.Random(76359 + iteration).shuffle(order)
                for variant in order:
                    actual = temporary / 'actual'
                    seconds, rss = measure([sys.executable, str(Path(__file__).resolve()), '--worker', variant],
                                           stdin, actual, temporary / 'rss', 30)
                    checked = subprocess.run([str(problem / 'checker'), str(stdin), str(actual), str(expected)],
                                             capture_output=True, timeout=30)
                    if checked.returncode:
                        raise ValueError(checked.stderr.decode(errors='replace'))
                    samples[variant].append(dict(seconds=seconds, peakRssKiB=rss, outputSha256=file_digest(actual)))
            row = dict(case=case, inputSha256=file_digest(stdin), expectedSha256=file_digest(expected),
                       implementations={variant: dict(samples=values,
                           medianSeconds=statistics.median(x['seconds'] for x in values),
                           peakRssKiB=max(x['peakRssKiB'] for x in values)) for variant, values in samples.items()})
            report['results'].append(row)
            save_json(output, report)
            print(json.dumps(row), flush=True)


if __name__ == '__main__':
    main()
