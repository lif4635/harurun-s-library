import sys
read = sys.stdin.buffer.readline
values = {}
answer = []
for _ in range(int(read())):
    query = list(map(int, read().split()))
    if query[0] == 0:
        values[str(query[1])] = query[2]
    else:
        answer.append(values.get(str(query[1]), 0))
print('\n'.join(map(str, answer)))
