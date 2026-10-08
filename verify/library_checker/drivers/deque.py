import sys

from library_codex.sequence_structure.Deque import Deque


read = sys.stdin.buffer.readline
queue = Deque()
answer = []
for _ in range(int(read())):
    row = read().split()
    kind = row[0]
    if kind == b"0":
        queue.appendleft(int(row[1]))
    elif kind == b"1":
        queue.append(int(row[1]))
    elif kind == b"2":
        queue.popleft()
    elif kind == b"3":
        queue.pop()
    else:
        answer.append(queue[int(row[1])])
print("\n".join(map(str, answer)))
