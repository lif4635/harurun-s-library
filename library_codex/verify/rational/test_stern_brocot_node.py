import math
import random

import pytest

from library_codex.rational.SternBrocotNode import SternBrocotNode


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


def test_bounds_depth_and_failed_parent():
    node = SternBrocotNode(6, 4)
    assert node.get() == (3, 2)
    assert node.lower_bound() == (1, 1)
    assert node.upper_bound() == (2, 1)
    assert node.path == [1, -1]
    assert node.depth() == 2
    assert not node.go_parent(3)
    assert not node.go_parent(-1)
    assert node.get() == (3, 2)
    assert node.depth() == 2
    other = SternBrocotNode(5, 3)
    common = SternBrocotNode.lca(node, other)
    assert isinstance(common, SternBrocotNode)
    assert common.get() == (3, 2)
    assert node.go_parent(2)
    assert node.get() == (1, 1)
    assert node.lower_bound() == (0, 1)
    assert node.upper_bound() == (1, 0)
    assert node.depth() == 0
    assert node.go_right(10 ** 20) is node
    assert node.depth() == 10 ** 20
    assert len(node.path) == 1
    assert node.go_parent(10 ** 20)
    for run in [3, -5, 2, -1, -4, 7]:
        (node.go_right if run > 0 else node.go_left)(abs(run))
        assert node.depth() == sum(map(abs, node.path))
    with pytest.raises(ValueError):
        SternBrocotNode(0, 1)
    with pytest.raises(ValueError):
        SternBrocotNode(path=[0])


def test_catalog_contract_and_standalone(tmp_path):
    import json
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    catalog = json.loads((root / "library-catalog.json").read_text())
    module = next(m for m in catalog["modules"] if m["modulePath"] == "library_codex.rational.SternBrocotNode")
    assert module["article"]
    methods = {m["name"]: m for m in module["classes"][0]["methods"]}
    assert methods['lower_bound']['returnFormat'] == 'tuple[int, int]'
    assert methods['upper_bound']['returnFormat'] == 'tuple[int, int]'
    assert methods['lca']['returnFormat'] == 'SternBrocotNode'
    assert methods['depth']['complexity'] == 'O(1)'
    script = tmp_path / "standalone.py"
    script.write_text(module["standaloneCode"] + "\nnode = SternBrocotNode(3, 2)\nassert node.lower_bound() == (1, 1)\nassert node.upper_bound() == (2, 1)\nassert node.depth() == 2\n")
    subprocess.run([sys.executable, "-I", str(script)], cwd=tmp_path, check=True, timeout=20)
