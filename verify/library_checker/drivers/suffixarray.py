import sys

from library_codex.string.SuffixArray import suffix_array

print(*suffix_array(sys.stdin.buffer.readline().strip()))
