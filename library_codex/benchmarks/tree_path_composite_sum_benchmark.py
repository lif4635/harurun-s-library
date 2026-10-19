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


class GenericTreePathCompositeSum:
    def __init__(self, values, edges, mod=998244353):
        from library_codex.tree.StaticTopTree import StaticTopTree, DynamicRerootingDP
        graph = [[] for _ in values]
        for u, v, b, c in edges:
            graph[u].append(v)
            graph[v].append(u)
        tree = StaticTopTree(graph)
        self.values = values[:]
        self.child = [v if tree.tree_parent[v] == u else u for u, v, b, c in edges]
        self.a = [1] * len(values)
        self.b = [0] * len(values)
        self.mod = mod
        for i, v in enumerate(self.child):
            self.a[v], self.b[v] = edges[i][2:]

        def compress(x, y):
            a, b, s, c = x
            d, e, t, f = y
            return a*d % mod, (a*e+b) % mod, (s+a*t+b*f) % mod, c+f

        def rake(x, y):
            return x[0], x[1], (x[2]+y[2]) % mod, x[3]+y[3]

        def reverse_rake(x, y):
            return x[0], x[1], (x[2]+x[0]*y[2]+x[1]*y[3]) % mod, x[3]+y[3]

        self.dp = DynamicRerootingDP(tree, self.leaf, rake, reverse_rake, compress, lambda: (1,0,0,0))
        self.dp.set(0, self.leaf(0))

    def leaf(self, v):
        a, b, value = self.a[v], self.b[v], self.values[v]
        return (a, b, (a*value+b) % self.mod, 1), (a, b, value, 1)

    def set(self, vertex, value):
        self.values[vertex] = value
        self.dp.set(vertex, self.leaf(vertex))

    def set_edge(self, edge, b, c):
        v = self.child[edge]
        self.a[v], self.b[v] = b, c
        self.dp.set(v, self.leaf(v))

    def query(self, root):
        return self.dp.get(root)[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', choices=('flat', 'generic'))
    parser.add_argument('--official', type=Path)
    parser.add_argument('--repeat', type=int, default=5)
    parser.add_argument('--cases', nargs='+', default=['typical_tree_max_01', 'typical_tree_max_02', 'typical_tree_max_degree_02'])
    args = parser.parse_args()
    name = 'point_set_tree_path_composite_sum'
    if args.worker:
        import importlib
        module = importlib.import_module('library_codex.tree.TreePathCompositeSum')
        if args.worker == 'generic':
            module.TreePathCompositeSum = GenericTreePathCompositeSum
        runpy.run_path(str(ROOT / 'verify/library_checker/drivers' / (name + '.py')), run_name='__main__')
        return
    from library_codex.benchmarks.official_comparison import measure
    from library_codex.benchmarks.official_benchmark import runtime_info
    from library_codex.tools.check_library_checker import file_digest, save_json, solution
    if args.official is None or args.repeat < 1:
        parser.error('require --official and repeat >= 1')
    problem = args.official / 'tree' / name
    hashes = json.loads((problem / 'hash.json').read_text())
    source, _ = solution(name)
    report = dict(measuredAt=datetime.now(timezone.utc).isoformat(),
                  environment=runtime_info(sys.executable), problem=name, repeat=args.repeat,
                  sourceSha256=hashlib.sha256(source.encode()).hexdigest(), harnessSha256=file_digest(__file__),
                  checkerSha256=file_digest(problem / 'checker'),
                  upstreamRevision=subprocess.check_output(['git', '-C', str(args.official), 'rev-parse', 'HEAD'], text=True).strip(),
                  protocol='sequential fresh PyPy processes, shuffled order, startup/JIT/I/O included, official checker, GNU time RSS',
                  variants={'flat': 'specialized parallel arrays', 'generic': 'DynamicRerootingDP with tuple callbacks'}, results=[])
    output = ROOT / 'library_codex/benchmarks/results/tree_path_composite_sum_comparison.json'
    with tempfile.TemporaryDirectory(prefix='harurun-tree-sum-') as directory:
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
                random.Random(8106 + iteration).shuffle(order)
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
