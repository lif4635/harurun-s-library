import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import pickle
import random
import statistics
import sys
import tempfile
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.benchmarks.baselines.max_flow import MaxFlowGraph as Previous
from library_codex.benchmarks.official_benchmark import runtime_info
from library_codex.benchmarks.official_comparison import measure
from library_codex.graph_flow.MaxFlow import MaxFlowGraph
from library_codex.graph_flow.PushRelabel import PushRelabel
from library_codex.tools.benchmark_advanced_flow import suite
from library_codex.tools.check_library_checker import file_digest, save_json


class EarlyBFS(Previous):
    def flow(self, source, sink, flow_limit=None):
        graph = self.graph
        if flow_limit is None:
            flow_limit = sum(edge[2] for edge in graph[source])
        total = 0
        n = self.n
        while total < flow_limit:
            level = [-1] * n
            level[source] = 0
            queue = [source]
            for v in queue:
                next_level = level[v] + 1
                for edge in graph[v]:
                    if edge[2] and level[edge[0]] < 0:
                        level[edge[0]] = next_level
                        queue.append(edge[0])
                        if edge[0] == sink:
                            break
                if level[sink] >= 0:
                    break
            if level[sink] < 0:
                break
            current = [0] * n
            while total < flow_limit:
                pushed = self._send_one(source, sink, flow_limit - total, level, current)
                if pushed == 0:
                    break
                total += pushed
        return total


class ReverseDFS(EarlyBFS):
    def _send_one(self, source, sink, limit, level, current):
        graph = self.graph
        vertices = [sink]
        path = []
        while vertices:
            v = vertices[-1]
            if v == source:
                pushed = limit
                for edge in path:
                    if edge[2] < pushed:
                        pushed = edge[2]
                for edge in path:
                    edge[2] -= pushed
                    graph[edge[0]][edge[1]][2] += pushed
                return pushed
            row = graph[v]
            index = current[v]
            wanted = level[v] - 1
            while index < len(row):
                edge = row[index]
                reverse = graph[edge[0]][edge[1]]
                if level[edge[0]] == wanted and reverse[2]:
                    break
                index += 1
            current[v] = index
            if index < len(row):
                vertices.append(edge[0])
                path.append(reverse)
            else:
                vertices.pop()
                if path:
                    path.pop()
                level[v] = self.n
        return 0


def interval_graph(n, intervals):
    intervals = sorted(intervals)
    ml = [0] * (n + 1)
    mr = list(range(n + 1))
    ng = [0] * (n + 1)
    for left, right in intervals:
        mr[left] = max(mr[left], right)
        ml[right] = max(ml[right], left)
        ng[right] = 1
    edges = [(i - 1, i, 2) for i in range(1, n + 1) if not ng[i]]
    for i in range(n):
        ml[i + 1] = max(ml[i], ml[i + 1])
    for i in range(n):
        right = mr[i]
        if ml[right] <= i:
            edges.append((i, right, 1))
        mr[i + 1] = max(mr[i], mr[i + 1])
    return n + 1, edges, 2


def cases(size, seed):
    yield 'arc232_short_interval', interval_graph(size, [(0, 2)])
    yield 'arc232_whole_interval', interval_graph(size, [(0, size)])
    yield 'arc232_windows', interval_graph(size, [(i, i + 32) for i in range(size - 31)])
    yield 'arc232_infeasible', interval_graph(size, [(0, 2), (1, 3), (0, 3)])
    for name, n, edges in suite(seed):
        yield name, (n, edges, None)


def worker(variant, input_path):
    if variant == 'acl':
        from atcoder.maxflow import MFGraph
        cls = MFGraph
    else:
        cls = {'previous': Previous, 'early_bfs': EarlyBFS, 'reverse_dfs': ReverseDFS,
               'candidate': MaxFlowGraph, 'push_relabel': PushRelabel}[variant]
    n, edges, limit = pickle.loads(input_path.read_bytes())
    started = perf_counter()
    graph = cls(n)
    for first, second, capacity in edges:
        graph.add_edge(first, second, capacity)
    built = perf_counter()
    value = graph.flow(0, n - 1, limit)
    finished = perf_counter()
    balance = [0] * n
    for first, second, capacity, flow in graph.edges():
        assert 0 <= flow <= capacity
        balance[first] -= flow
        balance[second] += flow
    assert balance[0] == -value and balance[-1] == value
    assert all(x == 0 for x in balance[1:-1])
    if limit is None or value < limit:
        side = graph.min_cut(0)
        assert not side[-1]
        assert sum(c for u, v, c in edges if side[u] and not side[v]) == value
    print(json.dumps(dict(value=value, buildSeconds=built-started, flowSeconds=finished-built)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker')
    parser.add_argument('--input', type=Path)
    parser.add_argument('--size', type=int, default=500000)
    parser.add_argument('--seed', type=int, default=4635)
    parser.add_argument('--repeat', type=int, default=5)
    parser.add_argument('--cases', nargs='+')
    parser.add_argument('--variants', nargs='+', default=['previous', 'early_bfs', 'reverse_dfs', 'acl', 'candidate', 'push_relabel'])
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('results')/'flow.json')
    args = parser.parse_args()
    if args.worker:
        worker(args.worker, args.input)
        return
    if args.size < 32 or args.repeat < 1:
        parser.error('size must be at least 32 and repeat positive')
    import atcoder.maxflow
    root = Path(__file__).resolve().parents[1]
    paths = [Path(__file__), root/'benchmarks/baselines/max_flow.py',
             root/'graph_flow/MaxFlow.py', root/'graph_flow/PushRelabel.py',
             root/'tools/benchmark_advanced_flow.py', Path(atcoder.maxflow.__file__)]
    report = dict(measuredAt=datetime.now(timezone.utc).isoformat(),
        environment=runtime_info(sys.executable), repeat=args.repeat, seed=args.seed,
        size=args.size, sourceSha256={str(p.relative_to(root)) if p.is_relative_to(root) else 'atcoder/maxflow.py': file_digest(p) for p in paths},
        aclVersion=importlib.metadata.version('ac-library-python'),
        protocol='generated graphs, sequential fresh PyPy processes, shuffled order, flow conservation and cut certificate checked; build/flow timings exclude input and validation; process time and peak RSS include both; no official AtCoder tests',
        results=[])
    with tempfile.TemporaryDirectory(prefix='harurun-flow-') as directory:
        temp = Path(directory)
        for name, data in cases(args.size, args.seed):
            if args.cases and name not in args.cases:
                continue
            raw = pickle.dumps(data, protocol=4)
            input_path = temp/'graph.pickle'
            input_path.write_bytes(raw)
            samples = {variant: [] for variant in args.variants}
            expected = None
            for iteration in range(args.repeat):
                order = args.variants[:]
                random.Random(args.seed + iteration).shuffle(order)
                for variant in order:
                    output = temp/'out.json'
                    seconds, rss = measure([sys.executable, str(Path(__file__).resolve()), '--worker', variant, '--input', str(input_path)], input_path, output, temp/'rss.txt', 120)
                    row = json.loads(output.read_text())
                    if expected is None:
                        expected = row['value']
                    assert row['value'] == expected
                    row.update(seconds=seconds, peakRssKiB=rss)
                    samples[variant].append(row)
            result = dict(case=name, vertices=data[0], edges=len(data[1]), flowLimit=data[2], value=expected,
                inputSha256=hashlib.sha256(raw).hexdigest(), implementations={})
            for variant, values in samples.items():
                result['implementations'][variant] = dict(samples=values,
                    medianSeconds=statistics.median(v['seconds'] for v in values),
                    medianBuildSeconds=statistics.median(v['buildSeconds'] for v in values),
                    medianFlowSeconds=statistics.median(v['flowSeconds'] for v in values),
                    peakRssKiB=max(v['peakRssKiB'] for v in values))
            report['results'].append(result)
            save_json(args.output, report)
            print(name, {v: round(r['medianFlowSeconds'], 4) for v, r in result['implementations'].items()}, flush=True)


if __name__ == '__main__':
    main()
