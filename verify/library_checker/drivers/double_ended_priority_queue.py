import sys
from library_codex.sequence_structure.ErasableHeap import ErasableHeap


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    values = list(map(int, read().split()))
    lower = ErasableHeap(values)
    upper = ErasableHeap(values, maximize=True)
    answer = []
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            lower.push(query[1])
            upper.push(query[1])
        elif query[0] == 1:
            value = lower.pop()
            upper.erase(value)
            answer.append(str(value))
        else:
            value = upper.pop()
            lower.erase(value)
            answer.append(str(value))
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
