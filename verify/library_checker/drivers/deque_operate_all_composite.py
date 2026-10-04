import sys

from library_codex.sequence_structure.SWAGDeque import SWAGDeque


def compose(first, second):
    a, b = first
    c, d = second
    return a * c % 998244353, (b * c + d) % 998244353


def solve():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    q = next(data)
    queue = SWAGDeque(compose, (1, 0))
    answer = []
    for _ in range(q):
        kind = next(data)
        if kind == 0:
            queue.appendleft((next(data), next(data)))
        elif kind == 1:
            queue.append((next(data), next(data)))
        elif kind == 2:
            queue.popleft()
        elif kind == 3:
            queue.pop()
        else:
            a, b = queue.fold()
            answer.append(str((a * next(data) + b) % 998244353))
    print("\n".join(answer))


if __name__ == "__main__":
    solve()
