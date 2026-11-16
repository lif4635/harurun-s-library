import random
import pytest
from library_codex.sequence_structure.PersistentDeque import PersistentDeque


def test_branching_operations_and_balance():
    rng = random.Random(71633)
    tree = PersistentDeque(range(100))
    versions = [list(range(100))]
    for _ in range(1600):
        version = rng.randrange(len(versions))
        values = versions[version]
        kind = rng.randrange(7)
        value = rng.randrange(100)
        if kind < 2:
            result = tree.push_front(value, version) if kind == 0 else tree.push_back(value, version)
            versions.append([value] + values if kind == 0 else values + [value])
        elif kind < 4 and values:
            result = tree.pop_front(version) if kind == 2 else tree.pop_back(version)
            versions.append(values[1:] if kind == 2 else values[:-1])
        elif kind == 4 and values:
            i = rng.randrange(len(values))
            result = tree.set(i, value, version)
            updated = values.copy()
            updated[i] = value
            versions.append(updated)
        elif kind == 5:
            i = rng.randrange(len(values) + 1)
            first, result = tree.split(i, version)
            assert first == len(versions)
            versions.extend((values[:i], values[i:]))
        else:
            other = rng.randrange(len(versions))
            if len(values) + len(versions[other]) > 500:
                continue
            result = tree.concat(version, other)
            versions.append(values + versions[other])
        assert result == len(versions) - 1
        assert tree.tolist(result) == versions[result]
        assert tree.tolist(version) == values
        before = tree.node_count()
        assert tree.size(version) == len(values)
        if values:
            i = rng.randrange(len(values))
            assert tree.get(i, version) == values[i]
        assert before == tree.node_count()
    for v in range(1, tree.node_count() + 1):
        if tree._height[v]:
            a, b = tree._left[v], tree._right[v]
            assert abs(tree._height[a] - tree._height[b]) <= 1
            assert tree._size[v] == tree._size[a] + tree._size[b]
    assert str(tree) == str(versions[-1])
    assert repr(tree) == "PersistentDeque(%r)" % versions[-1]


def test_self_concat_large_shared_sequence_and_empty():
    tree = PersistentDeque([7])
    version = 0
    for _ in range(45):
        version = tree.concat(version, version)
    assert tree.size(version) == 1 << 45
    assert tree.get((1 << 44) + 3, version) == 7
    before = tree.node_count()
    changed = tree.set(12345, 9, version)
    assert tree.get(12345, changed) == 9 and tree.get(12345, version) == 7
    assert tree.node_count() - before < 100
    empty = PersistentDeque()
    assert empty.tolist() == []
    assert empty.split(0) == (1, 2)
    for call in (lambda: empty.get(0), lambda: empty.set(0, 1), empty.pop_front, empty.pop_back, lambda: empty.split(-1)):
        with pytest.raises(IndexError):
            call()
