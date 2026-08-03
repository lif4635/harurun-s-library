from library_codex.data_structure.BinaryTrie import BinaryTrie
from library_codex.data_structure.DualSegmentTree import DualSegmentTree
from library_codex.data_structure.DynamicWaveletMatrix import (
    CompressedDynamicWaveletMatrix,
    OfflineDynamicWaveletMatrix,
)
from library_codex.data_structure.DynamicSegmentTree import DynamicSegmentTree
from library_codex.data_structure.ErasableHeap import ErasableHeap
from library_codex.data_structure.FastSet import FastSet
from library_codex.data_structure.FenwickTree import FenwickTree
from library_codex.data_structure.LazySegmentTree import LazySegmentTree
from library_codex.data_structure.ImplicitTreap import ImplicitTreap
from library_codex.data_structure.OrderedMap import OrderedMap
from library_codex.data_structure.PersistentArray import PersistentArray
from library_codex.data_structure.PersistentSegmentTree import PersistentSegmentTree
from library_codex.data_structure.SegmentTree import SegmentTree
from library_codex.data_structure.SegmentTree2D import SegmentTree2D
from library_codex.data_structure.SegmentTreeBeats import SegmentTreeBeats
from library_codex.data_structure.SWAGDeque import SWAGDeque
from library_codex.data_structure.SWAGQueue import SWAGQueue
from library_codex.data_structure.TreapSet import TreapSet
from library_codex.data_structure.UnionFind import UnionFind


def test_dense_tree_debug_output_uses_logical_values():
    segment = SegmentTree([1, 2, 3], lambda a, b: a + b, 0)
    segment.add(1, 5)
    assert segment.tolist() == [1, 7, 3]
    assert str(segment) == "[1, 7, 3]"
    assert repr(segment) == "SegmentTree([1, 7, 3])"

    lazy = LazySegmentTree(
        [1, 2, 3],
        lambda a, b: a + b,
        0,
        lambda action, value, length: value + action * length,
        lambda new, old: new + old,
    )
    lazy.apply(0, 2, 10)
    assert lazy.tolist() == [11, 12, 3]
    assert str(lazy) == "[11, 12, 3]"
    assert lazy.prod(0, 3) == 26

    dual = DualSegmentTree(
        [1, 2, 3],
        lambda action, value: value + action,
        lambda new, old: new + old,
    )
    dual.apply(1, 3, 4)
    assert dual.tolist() == [1, 6, 7]
    assert repr(dual) == "DualSegmentTree([1, 6, 7])"

    beats = SegmentTreeBeats([5, 1, 8])
    beats.range_add(0, 3, 2)
    beats.range_chmin(0, 3, 6)
    assert beats.tolist() == [6, 3, 6]
    assert str(beats) == "[6, 3, 6]"


def test_sparse_persistent_and_2d_tree_debug_output():
    dynamic = DynamicSegmentTree(-10, 10, lambda a, b: a + b, "")
    dynamic.set(4, "old")
    dynamic.add(4, "new-")
    dynamic.set(-2, "left")
    assert dynamic.items() == [(-2, "left"), (4, "new-old")]
    assert str(dynamic) == "{-2: 'left', 4: 'new-old'}"

    persistent = PersistentSegmentTree([1, 2, 3], lambda a, b: a + b, 0)
    version = persistent.set(1, 9)
    assert persistent.tolist(0) == [1, 2, 3]
    assert persistent.tolist(version) == [1, 9, 3]
    assert repr(persistent) == "PersistentSegmentTree([1, 9, 3])"

    matrix = SegmentTree2D([[1, 2], [3, 4]], lambda a, b: a + b, 0)
    matrix.set(1, 0, 8)
    assert matrix.tolist() == [[1, 2], [8, 4]]
    assert str(matrix) == "[[1, 2], [8, 4]]"

    array = PersistentArray(["a", "b", "c"], "")
    array.set(0, "A")
    assert str(array) == "['A', 'b', 'c']"


def test_linear_container_debug_output():
    fenwick = FenwickTree([3, 1, 4, 1, 5])
    fenwick.add(2, 10)
    assert fenwick.tolist() == [3, 1, 14, 1, 5]
    assert repr(fenwick) == "FenwickTree([3, 1, 14, 1, 5])"

    queue = SWAGQueue(lambda a, b: a + b, "")
    for value in "abcd":
        queue.append(value)
    assert queue.popleft() == "a"
    assert queue.tolist() == ["b", "c", "d"]
    assert str(queue) == "['b', 'c', 'd']"

    deque = SWAGDeque(lambda a, b: a + b, "")
    deque.append("b")
    deque.appendleft("a")
    deque.append("c")
    assert deque.tolist() == ["a", "b", "c"]
    assert repr(deque) == "SWAGDeque(['a', 'b', 'c'])"

    heap = ErasableHeap([3, 1, 1, 2])
    heap.erase(1)
    assert heap.tolist() == [1, 2, 3]
    assert str(heap) == "[1, 2, 3]"


def test_set_trie_and_union_find_debug_output():
    ordered = FastSet(20, [9, 2, 5])
    assert ordered.tolist() == [2, 5, 9]
    assert str(ordered) == "[2, 5, 9]"

    trie = BinaryTrie(4)
    trie.add(1, 2)
    trie.add(7)
    trie.xor_all(3)
    assert trie.tolist() == [2, 2, 4]
    assert repr(trie) == "BinaryTrie([2, 2, 4])"

    union_find = UnionFind(5)
    union_find.merge(0, 2)
    union_find.merge(3, 4)
    assert str(union_find) == "[[0, 2], [1], [3, 4]]"
    assert repr(union_find) == "UnionFind([[0, 2], [1], [3, 4]])"


def test_sequence_and_ordered_structure_debug_output():
    treap = ImplicitTreap([1, 2, 3], lambda a, b: a + b, 0)
    treap.reverse(0, 3)
    assert treap.tolist() == [3, 2, 1]
    assert repr(treap) == "ImplicitTreap([3, 2, 1])"

    ordered_set = TreapSet([5, 2, 9])
    assert str(ordered_set) == "[2, 5, 9]"

    ordered_map = OrderedMap([(5, "e"), (2, "b")])
    assert str(ordered_map) == "{2: 'b', 5: 'e'}"

    wavelet = CompressedDynamicWaveletMatrix([4, 1, 3], [(1, 2)])
    wavelet.set(1, 2)
    assert str(wavelet) == "[4, 2, 3]"
    assert repr(wavelet) == "CompressedDynamicWaveletMatrix([4, 2, 3])"

    offline = OfflineDynamicWaveletMatrix([3, 1, 4])
    offline.set(0, 2)
    assert str(offline) == "[2, 1, 4]"
