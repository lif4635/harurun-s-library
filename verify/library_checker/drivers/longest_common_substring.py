import sys

from library_codex.string_sequence.LongestCommonSubstring import longest_common_substring

read = sys.stdin.buffer.readline
_, first, second = longest_common_substring(read().strip(), read().strip())
print(*first, *second)
