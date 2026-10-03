import sys
from library_codex.range_query.WaveletMatrix import WaveletMatrix

read = sys.stdin.buffer.readline
n, q = map(int, read().split())
table = WaveletMatrix(list(map(int, read().split())))
answers = [str(table.kth_smallest(*map(int, read().split()))) for _ in range(q)]
sys.stdout.write("\n".join(answers) + "\n")
