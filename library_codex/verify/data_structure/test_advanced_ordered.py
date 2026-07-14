import bisect
import random

from library_codex.data_structure.AdvancedOrdered import OrderedMap, PersistentRBSTSet


def test_ordered_map_against_dict_and_sorted_keys():
    rng = random.Random(111)
    ordered = OrderedMap(default_factory=int)
    expected = {}
    for _ in range(20000):
        key = rng.randrange(1000)
        operation = rng.randrange(4)
        if operation == 0:
            value = rng.randrange(100000)
            ordered[key] = value
            expected[key] = value
        elif operation == 1:
            assert ordered.erase(key) == (expected.pop(key, None) is not None)
        elif operation == 2:
            ordered[key] += 1
            expected[key] = expected.get(key, 0) + 1
        else:
            assert ordered.get(key) == expected.get(key)
        keys = sorted(expected)
        assert len(ordered) == len(keys)
        assert ordered.lower_bound(key) == bisect.bisect_left(keys, key)
        assert ordered.upper_bound(key) == bisect.bisect_right(keys, key)
        if keys:
            index = rng.randrange(len(keys))
            assert ordered.kth_element(index) == (keys[index], expected[keys[index]])


def test_persistent_rbst_set_branching_versions():
    rng = random.Random(112)
    tree = PersistentRBSTSet()
    versions = [set()]
    for _ in range(10000):
        base = rng.randrange(len(versions))
        key = rng.randrange(500)
        expected = versions[base].copy()
        if rng.randrange(2):
            version = tree.insert(key, base)
            expected.add(key)
        else:
            version = tree.erase(key, base)
            expected.discard(key)
        versions.append(expected)
        assert version == len(versions) - 1
        keys = sorted(expected)
        assert tree.to_list(version) == keys
        assert tree.contains(key, version) == (key in expected)
        assert tree.lower_bound(key, version) == bisect.bisect_left(keys, key)
        assert tree.upper_bound(key, version) == bisect.bisect_right(keys, key)
        if keys:
            index = rng.randrange(len(keys))
            assert tree.kth(index, version) == keys[index]
