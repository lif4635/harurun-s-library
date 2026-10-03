import sys
from library_codex.sequence_structure.PersistentQueue import PersistentQueue

read = sys.stdin.buffer.readline
queue = PersistentQueue()
answers = []
for _ in range(int(read())):
    query = list(map(int, read().split()))
    version = query[1] + 1
    if query[0] == 0:
        queue.append(query[2], version)
    else:
        answers.append(str(queue.front(version)))
        queue.popleft(version)
sys.stdout.write("\n".join(answers) + "\n")
