import heapq
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.sequence_structure.SkewHeap import SkewHeap  # noqa: E402
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
