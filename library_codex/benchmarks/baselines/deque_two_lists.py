"""両端の追加・削除と、任意位置の取得・変更ができる両端キュー。"""

class Deque:
    __slots__ = ('front', 'back')

    def __init__(self, values=()):
        self.front = []
        self.back = list(values)

    def appendleft(self, value):
        self.front.append(value)

    def append(self, value):
        self.back.append(value)

    def popleft(self):
        if not self.front:
            if not self.back:
                raise IndexError('pop from empty Deque')
            split = len(self.back) + 1 >> 1
            self.front = self.back[:split][::-1]
            self.back = self.back[split:]
        return self.front.pop()

    def pop(self):
        if not self.back:
            if not self.front:
                raise IndexError('pop from empty Deque')
            split = len(self.front) + 1 >> 1
            self.back = self.front[:split][::-1]
            self.front = self.front[split:]
        return self.back.pop()

    def __len__(self):
        return len(self.front) + len(self.back)

    def __getitem__(self, index):
        size = len(self.front) + len(self.back)
        if index < 0:
            index += size
        if not 0 <= index < size:
            raise IndexError('index out of range')
        first = len(self.front)
        return self.front[first - 1 - index] if index < first else self.back[index - first]

    def __setitem__(self, index, value):
        size = len(self.front) + len(self.back)
        if index < 0:
            index += size
        if not 0 <= index < size:
            raise IndexError('index out of range')
        first = len(self.front)
        if index < first:
            self.front[first - 1 - index] = value
        else:
            self.back[index - first] = value

    def tolist(self):
        return self.front[::-1] + self.back

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'Deque(' + str(self.tolist()) + ')'
import sys
read = sys.stdin.buffer.readline
queue = Deque()
answer = []
for _ in range(int(read())):
    row = read().split()
    kind = row[0]
    if kind == b'0':
        queue.appendleft(int(row[1]))
    elif kind == b'1':
        queue.append(int(row[1]))
    elif kind == b'2':
        queue.popleft()
    elif kind == b'3':
        queue.pop()
    else:
        answer.append(queue[int(row[1])])
print('\n'.join(map(str, answer)))
