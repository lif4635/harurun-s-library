import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.string.PersistentString import (
    PersistentString,
    _Branch,
    _CHUNK_SIZE,
    _Leaf,
)
from library_codex.string.StaticString import (
    MergedStaticString,
    StaticString,
    StaticStringBase,
    init_suffix_array,
    to_static_strings,
)
from library_codex.string.StringSearch import lcp_naive


def compare(first, second):
    return (first > second) - (first < second)


def validate_structure(rope):
    seen = set()
    stack = [] if rope._root is None else [rope._root]
    while stack:
        node = stack.pop()
        identity = id(node)
        if identity in seen:
            continue
        seen.add(identity)
        if isinstance(node, _Leaf):
            assert 0 < node.size <= _CHUNK_SIZE
            assert node.size == len(node.data)
            assert node.height == 0
        else:
            assert isinstance(node, _Branch)
            assert node.size == node.left.size + node.right.size
            assert node.height == max(node.left.height, node.right.height) + 1
            assert abs(node.left.height - node.right.height) <= 1
            stack.append(node.left)
            stack.append(node.right)


def validate_rope(rope, expected, materialize=True):
    assert len(rope) == rope.size() == len(expected)
    assert rope.empty() == (len(expected) == 0)
    if materialize:
        assert rope.to_sequence() == expected
        assert list(rope) == list(expected)
    if expected:
        for index in (0, len(expected) // 2, len(expected) - 1, -1):
            assert rope[index] == expected[index]
    validate_structure(rope)


def test_persistent_random_operations():
    rng = random.Random(0)
    versions = [(PersistentString(""), "")]
    for _ in range(20000):
        base, value = rng.choice(versions)
        operation = rng.randrange(6)
        if operation == 0:
            added = "".join(
                rng.choice("abcd") for _ in range(rng.randrange(20))
            )
            result = base + PersistentString(added)
            expected = value + added
        elif operation == 1:
            left = rng.randrange(len(value) + 1)
            right = rng.randrange(left, len(value) + 1)
            result = base.substr(left, right - left)
            expected = value[left:right]
        elif operation == 2:
            added = "".join(
                rng.choice("abcd") for _ in range(rng.randrange(15))
            )
            position = rng.randrange(len(value) + 1)
            result = base.inserted(PersistentString(added), position)
            expected = value[:position] + added + value[position:]
        elif operation == 3:
            left = rng.randrange(len(value) + 1)
            right = rng.randrange(left, len(value) + 1)
            result = base.deleted(left, right)
            expected = value[:left] + value[right:]
        elif operation == 4:
            repeat = rng.randrange(6)
            result = base * repeat
            expected = value * repeat
        else:
            left = rng.randrange(len(value) + 1)
            right = rng.randrange(left, len(value) + 1)
            added = "".join(
                rng.choice("abcd") for _ in range(rng.randrange(10))
            )
            result = base.replaced(left, right, PersistentString(added))
            expected = value[:left] + added + value[right:]
        if len(expected) > 300:
            result = result[:300]
            expected = expected[:300]
        validate_rope(base, value)
        validate_rope(result, expected)
        for _ in range(3):
            left = rng.randrange(len(expected) + 1)
            right = rng.randrange(left, len(expected) + 1)
            assert result[left:right].to_sequence() == expected[left:right]
        versions.append((result, expected))
        if len(versions) > 1000:
            del versions[:500]


def test_persistent_types_mutation_and_comparison():
    for value in (
        "abracadabra",
        bytes((0, 1, 2, 1, 0)),
        (3, -1, 4, -1, 5),
    ):
        rope = PersistentString(value)
        validate_rope(rope, value)
        assert rope[::-1].to_sequence() == value[::-1]
        copied = rope.copy()
        inserted = value[:2] + value + value[2:]
        rope.insert(copied, 2)
        assert rope.to_sequence() == inserted
        assert copied.to_sequence() == value
        rope *= 2
        assert rope.to_sequence() == inserted * 2

    rng = random.Random(1)
    for _ in range(10000):
        first = "".join(
            rng.choice("abc") for _ in range(rng.randrange(100))
        )
        second = "".join(
            rng.choice("abc") for _ in range(rng.randrange(100))
        )
        left = PersistentString(first)
        right = PersistentString(second)
        assert left.lcp(right) == lcp_naive(first, second)
        assert left.compare(right) == compare(first, second)
        assert (left == right) == (first == second)
        assert (left < right) == (first < second)
    assert PersistentString("a") != PersistentString(b"a")
    assert PersistentString("") != PersistentString(b"")


def test_huge_shared_string_without_materialization():
    unit = PersistentString("ab")
    huge = unit * (1 << 59)
    assert len(huge) == 1 << 60
    assert huge.depth < 100
    assert huge[0] == "a"
    assert huge[(1 << 60) - 1] == "b"
    assert huge.substr((1 << 59) - 3, 10).to_sequence() == "bababababa"
    validate_structure(huge)
    with pytest.raises(OverflowError):
        _ = huge + PersistentString("a")
    with pytest.raises(ValueError):
        _ = unit * -1


def test_deep_sequential_concat_without_recursion():
    size = 300000
    rope = PersistentString("")
    a = PersistentString("a")
    for _ in range(size):
        rope += a
    assert len(rope) == size
    assert rope.depth < 30
    assert rope.substr(size - 1000, 1000).to_sequence() == "a" * 1000
    assert rope.to_sequence() == "a" * size
    validate_rope(rope, "a" * size, False)


def validate_static_view(view, expected):
    assert len(view) == len(expected)
    assert view.materialize() == expected
    if expected:
        assert view[0] == expected[0]
        assert view[-1] == expected[-1]
    for left in range(min(len(expected), 5) + 1):
        right = len(expected) - left
        if right >= left:
            assert view[left:right].materialize() == expected[left:right]


def test_static_string_random_views():
    rng = random.Random(2)
    for _ in range(3000):
        value = "".join(
            rng.choice("abcd") for _ in range(rng.randrange(60))
        )
        base = StaticStringBase(value)
        whole = base.view()
        validate_static_view(whole, value)
        for _ in range(50):
            left1 = rng.randrange(len(value) + 1)
            right1 = rng.randrange(left1, len(value) + 1)
            left2 = rng.randrange(len(value) + 1)
            right2 = rng.randrange(left2, len(value) + 1)
            first = whole[left1:right1]
            second = whole[left2:right2]
            expected_first = value[left1:right1]
            expected_second = value[left2:right2]
            assert first.lcp(second) == lcp_naive(
                expected_first, expected_second
            )
            assert first.compare(second) == compare(
                expected_first, expected_second
            )
            assert (first == second) == (expected_first == expected_second)
            assert first.startswith(second) == expected_first.startswith(
                expected_second
            )
        suffixes = init_suffix_array(base)
        assert [part.materialize() for part in suffixes] == sorted(
            value[index:] for index in range(len(value))
        )


def test_static_strings_and_merged_views():
    rng = random.Random(3)
    for _ in range(5000):
        values = [
            "".join(rng.choice("abc") for _ in range(rng.randrange(20)))
            for _ in range(rng.randrange(1, 12))
        ]
        views = to_static_strings(values)
        for first, first_value in zip(views, values):
            for second, second_value in zip(views, values):
                assert first.lcp(second) == lcp_naive(first_value, second_value)
                assert first.compare(second) == compare(first_value, second_value)
        order = list(range(len(views)))
        rng.shuffle(order)
        merged = MergedStaticString(views[index] for index in order)
        expected = "".join(values[index] for index in order)
        assert merged.materialize() == expected
        for _ in range(20):
            left = rng.randrange(len(expected) + 1)
            right = rng.randrange(left, len(expected) + 1)
            assert merged[left:right].materialize() == expected[left:right]
            if left < len(expected):
                assert merged[left] == expected[left]
        reverse = MergedStaticString(reversed(views))
        reverse_value = "".join(reversed(values))
        assert merged.lcp(reverse) == lcp_naive(expected, reverse_value)
        assert merged.compare(reverse) == compare(expected, reverse_value)


def test_static_types_and_many_parts():
    for value in (bytes((0, 1, 0, 2)), (3, -1, 3, 4)):
        view = StaticString.from_sequence(value)
        validate_static_view(view, value)
        assert (view + view[::-1]).materialize() == value + value[::-1]
        assert MergedStaticString((view[:0],)).materialize() == value[:0]

    base = StaticStringBase("ab")
    first = base.view(0, 1)
    second = base.view(1, 2)
    parts = [first, second] * 50000
    merged = MergedStaticString(parts)
    assert len(merged) == 100000
    assert merged[99999] == "b"
    assert merged.lcp(merged) == len(merged)
    assert merged[12345:98765].materialize() == ("ab" * 50000)[12345:98765]


if __name__ == "__main__":
    test_persistent_random_operations()
    test_persistent_types_mutation_and_comparison()
    test_huge_shared_string_without_materialization()
    test_deep_sequential_concat_without_recursion()
    test_static_string_random_views()
    test_static_strings_and_merged_views()
    test_static_types_and_many_parts()
