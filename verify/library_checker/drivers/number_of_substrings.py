import sys

from library_codex.string.SuffixArray import suffix_array, lcp_array

sequence = sys.stdin.buffer.readline().strip()
n = len(sequence)
print(n * (n + 1) // 2 - sum(lcp_array(sequence, suffix_array(sequence))))
