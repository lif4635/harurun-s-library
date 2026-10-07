import sys

from library_codex.linear_algebra.XorBasis import XorBasis

read = sys.stdin.buffer.readline
answers = []
for _ in range(int(read())):
    first = XorBasis(list(map(int, read().split()))[1:])
    second = XorBasis(list(map(int, read().split()))[1:])
    common = first.intersection(second).basis
    answers.append(" ".join(map(str, [len(common)] + common)))
sys.stdout.write("\n".join(answers))
