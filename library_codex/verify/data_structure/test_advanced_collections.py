import heapq
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.data_structure.AdvancedCollections import (  # noqa: E402
    SkewHeap,
    UnionRectangle,
    union_rectangle_area,
)
from library_codex.graph.MinimumSpanningTree import (  # noqa: E402
    manhattan_mst,
    minimum_spanning_tree,
)


def test_manhattan_mst_against_complete_graph_kruskal():
    rng = random.Random(130)
    for n in range(1, 80):
        for _ in range(100):
            points = [(rng.randrange(-100, 101), rng.randrange(-100, 101))
                      for _ in range(n)]
            complete = [
                (u, v, abs(points[u][0] - points[v][0])
                 + abs(points[u][1] - points[v][1]))
                for u in range(n) for v in range(u + 1, n)
            ]
            expected, _ = minimum_spanning_tree(n, complete)
            value, edges = manhattan_mst(points)
            assert value == expected
            assert len(edges) == n - 1
            assert value == sum(abs(points[u][0] - points[v][0])
                                + abs(points[u][1] - points[v][1])
                                for u, v in edges)


def test_union_rectangle_area_against_unit_cells():
    rng = random.Random(131)
    for _ in range(20_000):
        rectangles = []
        cells = set()
        for _ in range(rng.randrange(20)):
            left, right = sorted((rng.randrange(-10, 11), rng.randrange(-10, 11)))
            bottom, top = sorted((rng.randrange(-10, 11), rng.randrange(-10, 11)))
            rectangles.append((left, right, bottom, top))
            cells.update((x, y) for x in range(left, right)
                         for y in range(bottom, top))
        assert union_rectangle_area(rectangles) == len(cells)
        solver = UnionRectangle()
        for rectangle in rectangles:
            solver.add(*rectangle)
        assert solver.run() == len(cells)


def test_skew_heap_meld_lazy_and_deep_nonrecursive():
    rng = random.Random(132)
    heap = SkewHeap()
    roots = [-1] * 100
    models = [[] for _ in roots]
    for operation in range(100_000):
        bucket = rng.randrange(len(roots))
        kind = rng.randrange(4)
        if kind == 0 or not models[bucket]:
            key = rng.randrange(-10**9, 10**9)
            roots[bucket] = heap.push(roots[bucket], key, operation)
            heapq.heappush(models[bucket], (key, operation))
        elif kind == 1:
            delta = rng.randrange(-1000, 1001)
            roots[bucket] = heap.add_all(roots[bucket], delta)
            models[bucket] = [(key + delta, value)
                              for key, value in models[bucket]]
            heapq.heapify(models[bucket])
        elif kind == 2:
            other = rng.randrange(len(roots))
            if other != bucket:
                roots[bucket] = heap.meld(roots[bucket], roots[other])
                roots[other] = -1
                models[bucket].extend(models[other])
                models[other] = []
                heapq.heapify(models[bucket])
        else:
            assert heap.top(roots[bucket]) == models[bucket][0]
            roots[bucket] = heap.pop(roots[bucket])
            heapq.heappop(models[bucket])
        if models[bucket]:
            assert heap.top(roots[bucket]) == models[bucket][0]
