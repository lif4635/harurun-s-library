import sys

from library_codex.string.Manacher import enumerate_palindrome_lengths

print(*enumerate_palindrome_lengths(sys.stdin.buffer.readline().strip()))
