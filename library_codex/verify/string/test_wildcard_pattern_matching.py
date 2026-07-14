import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.string.WildcardPatternMatching import (
    wildcard_match_positions,
    wildcard_pattern_matching,
)


def brute(text, pattern, wildcard):
    if len(pattern) == 0:
        return [1] * (len(text) + 1)
    if len(text) < len(pattern):
        return []
    result = []
    for start in range(len(text) - len(pattern) + 1):
        result.append(int(all(
            text[start + index] == wildcard
            or pattern[index] == wildcard
            or text[start + index] == pattern[index]
            for index in range(len(pattern))
        )))
    return result


def test_small_random_against_brute():
    rng = random.Random(0)
    for _ in range(20000):
        text = "".join(
            rng.choice("abc?") for _ in range(rng.randrange(80))
        )
        pattern = "".join(
            rng.choice("abc?") for _ in range(rng.randrange(30))
        )
        expected = brute(text, pattern, "?")
        assert wildcard_pattern_matching(text, pattern, "?") == expected
        assert wildcard_match_positions(text, pattern, "?") == [
            index for index, value in enumerate(expected) if value
        ]


def test_ntt_path_random_against_brute():
    rng = random.Random(1)
    for _ in range(300):
        text = tuple(rng.randrange(20) for _ in range(1800))
        pattern = tuple(
            0 if rng.randrange(7) == 0 else rng.randrange(1, 20)
            for _ in range(180)
        )
        assert wildcard_pattern_matching(text, pattern) == brute(
            text, pattern, 0
        )


def test_two_moduli_and_unhashable_symbols():
    text = tuple(range(2000))
    pattern = tuple(range(500, 800))
    assert wildcard_match_positions(text, pattern, -1) == [500]

    wildcard = [-1]
    text = [[index % 7] for index in range(1000)]
    pattern = [
        wildcard if index % 11 == 0 else [(index + 300) % 7]
        for index in range(300)
    ]
    assert wildcard_pattern_matching(text, pattern, wildcard) == brute(
        text, pattern, wildcard
    )


def test_edge_cases():
    assert wildcard_pattern_matching("abc", "", "?") == [1, 1, 1, 1]
    assert wildcard_pattern_matching("", "a", "?") == []
    assert wildcard_pattern_matching("????", "abcd", "?") == [1]
    assert wildcard_pattern_matching("abcd", "????", "?") == [1]
    assert wildcard_pattern_matching("abc", "abc", "?") == [1]
    assert wildcard_pattern_matching("abc", "abd", "?") == [0]


def test_large_without_recursion():
    text_size = 200000
    pattern_size = 100000
    text = ("abac" * ((text_size + 3) // 4))[:text_size]
    pattern = ("abac" * ((pattern_size + 3) // 4))[:pattern_size]
    result = wildcard_pattern_matching(text, pattern, "?")
    assert len(result) == text_size - pattern_size + 1
    assert sum(result) == (len(result) + 3) // 4
    assert result[0] == result[4] == 1


if __name__ == "__main__":
    test_small_random_against_brute()
    test_ntt_path_random_against_brute()
    test_two_moduli_and_unhashable_symbols()
    test_edge_cases()
    test_large_without_recursion()
