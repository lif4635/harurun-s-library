import sys
from library_codex.sequence_structure.SWAGQueue import SWAGQueue


def compose(first, second):
    return (first[0] * second[0] % 998244353,
            (first[1] * second[0] + second[1]) % 998244353)


read = sys.stdin.buffer.readline
queue = SWAGQueue(compose, (1, 0))
answers = []
for _ in range(int(read())):
    query = list(map(int, read().split()))
    if query[0] == 0:
        queue.append((query[1], query[2]))
    elif query[0] == 1:
        queue.popleft()
    else:
        a, b = queue.fold()
        answers.append(str((a * query[1] + b) % 998244353))
sys.stdout.write("\n".join(answers) + "\n")
