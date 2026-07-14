import itertools
import math
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parent))

from library_codex.math.Structures import (  # noqa: E402
    Affine,
    SternBrocotNode,
    XorBasis,
    grundy_numbers,
)


def test_affine_composition():
    rng = random.Random(120)
    for mod in (None, 998244353):
        for _ in range(10_000):
            left = Affine(rng.randrange(-100, 101), rng.randrange(-100, 101), mod)
            right = Affine(rng.randrange(-100, 101), rng.randrange(-100, 101), mod)
            value = rng.randrange(-100, 101)
            assert (left * right)(value) == right(left(value))


def test_xor_basis_all_generated_values():
    rng = random.Random(121)
    for n in range(13):
        for _ in range(500):
            values = [rng.randrange(1 << 14) for _ in range(n)]
            basis = XorBasis(values)
            generated = {0}
            for value in values:
                generated |= {x ^ value for x in tuple(generated)}
            ordered = sorted(generated)
            assert len(ordered) == 1 << len(basis)
            assert [basis.kth_smallest(i) for i in range(len(ordered))] == ordered
            for i, value in enumerate(ordered):
                assert basis.contains(value)
                assert basis.rank(value) == i
            for xor in (0, rng.randrange(1 << 14), rng.randrange(1 << 14)):
                transformed = sorted(value ^ xor for value in ordered)
                assert basis.minimum(xor) == transformed[0]
                assert basis.maximum(xor) == transformed[-1]
                assert [basis.xor_kth(xor, i) for i in range(len(ordered))] == transformed


def test_stern_brocot_fraction_path_parent_and_lca():
    nodes = {}
    for numerator in range(1, 100):
        for denominator in range(1, 100):
            divisor = math.gcd(numerator, denominator)
            reduced = (numerator // divisor, denominator // divisor)
            node = SternBrocotNode(numerator, denominator)
            assert node.get() == reduced
            assert SternBrocotNode(path=node.path).get() == reduced
            nodes[reduced] = node
    rng = random.Random(122)
    items = list(nodes.values())
    for _ in range(10_000):
        first = rng.choice(items)
        second = rng.choice(items)
        common = []
        for left, right in zip(first.path, second.path):
            if (left < 0) != (right < 0):
                break
            amount = min(abs(left), abs(right))
            common.append(amount if left > 0 else -amount)
            if left != right:
                break
        lca = SternBrocotNode.lca(first, second)
        assert lca.path == common
        copy = SternBrocotNode(path=first.path)
        depth = rng.randrange(copy.depth() + 1)
        expected_path = []
        remain = copy.depth() - depth
        for run in copy.path:
            take = min(remain, abs(run))
            if take:
                expected_path.append(take if run > 0 else -take)
            remain -= take
        assert copy.go_parent(depth)
        assert copy.path == expected_path


def test_grundy_numbers_random_dag():
    rng = random.Random(123)
    for n in range(100):
        for _ in range(20):
            graph = [[] for _ in range(n)]
            for u in range(n):
                for v in range(u + 1, n):
                    if rng.randrange(20) == 0:
                        graph[u].append(v)
            grundy = grundy_numbers(graph)
            for v in range(n - 1, -1, -1):
                reachable = {grundy[to] for to in graph[v]}
                expected = 0
                while expected in reachable:
                    expected += 1
                assert grundy[v] == expected
    assert grundy_numbers([[1], [0]]) is None
