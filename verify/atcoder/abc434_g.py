from array import array
import sys

from library_codex.segment_tree.SegTreeTraversal import SegTreeTraversal


class _KeyboardData:
    __slots__ = ("back", "length", "value", "head", "power")

    def __init__(self, capacity, n):
        self.back = array("I", [0]) * capacity
        self.length = array("I", [0]) * capacity
        self.value = array("I", [0]) * capacity
        self.head = array("I", [0]) * (capacity >> 1)
        self.power = power = array("I", [1]) * (n + 1)
        p = 1
        for i in range(n):
            p = p * 10 % 998244353
            power[i + 1] = p

    def __len__(self):
        return len(self.back)

    def __getitem__(self, node):
        return self.back[node], self.length[node], self.value[node], self.head[node] if node < len(self.head) else 0

    def __setitem__(self, node, value):
        if isinstance(value, int):
            if value != 66 and not 49 <= value <= 57:
                raise ValueError("expected digits 1..9 or B")
            back, length, value, head = (1, 0, 0, 0) if value == 66 else (0, 1, value - 48, 0)
        else:
            back, length, value, head = value
        self.back[node] = back
        self.length[node] = length
        self.value[node] = value
        if node < len(self.head):
            self.head[node] = head


def _merge(data, node, right):
    back, length, value, _ = right
    kept = data.length[node] - back
    if kept <= 0:
        return data.back[node] - kept, length, value, 0
    back = data.back[node]
    power = data.power
    prefix = data.value[node]
    if kept != data.length[node]:
        count = kept
        prefix = 0
        lengths = data.length
        values = data.value
        head = data.head
        while count and count != lengths[node]:
            child = node << 1 | 1
            first = lengths[node] - lengths[child]
            if count <= first:
                node <<= 1
            else:
                prefix = (prefix * power[first] + head[node]) % 998244353
                count -= first
                node = child
        if count:
            prefix = (prefix * power[count] + values[node]) % 998244353
    return back, kept + length, (prefix * power[length] + value) % 998244353, prefix


class Keyboard:
    __slots__ = ("tree", "n")

    def __init__(self, text):
        if isinstance(text, str):
            text = text.encode()
        self.n = n = len(text)
        self.tree = SegTreeTraversal(_merge, (0, 0, 0, 0), text,
                                     storage=lambda capacity, identity: _KeyboardData(capacity, n))

    def set(self, index, char):
        if isinstance(char, (str, bytes)):
            char = ord(char)
        self.tree.set(index, char)

    def prod(self, left, right):
        back, length, value, _ = self.tree.prod(left, right)
        return back, length, value

    def tolist(self):
        data = self.tree.data
        size = self.tree.size
        return ["B" if data.back[size + i] else str(data.value[size + i]) for i in range(self.n)]

    def __str__(self):
        return "".join(self.tolist())

    def __repr__(self):
        return "Keyboard(%r)" % str(self)


def main():
    stream = sys.stdin.buffer
    n, q = map(int, stream.readline().split())
    tree = Keyboard(stream.readline().strip())
    if tree.n != n:
        raise ValueError("unexpected string length")
    answers = []
    for _ in range(q):
        kind, first, second = stream.readline().split()
        if kind == b"1":
            tree.set(int(first) - 1, second)
        else:
            _, length, value = tree.prod(int(first) - 1, int(second))
            answers.append(str(value if length else -1))
    sys.stdout.write("\n".join(answers) + "\n")


if __name__ == "__main__":
    main()
