"""子孫を参照するマージ用に、構築・一点更新・右からの区間結合を行う。"""

def build(size, pull):
    """葉を配置済みの木を、子から親の順にpull(node)で構築する。"""
    if size < 1 or size & size - 1:
        raise ValueError('size must be a positive power of two')
    for node in range(size - 1, 0, -1):
        pull(node)

def update(size, index, pull):
    """変更済みの葉indexから根まで、親の情報をpull(node)で再計算する。"""
    if not 0 <= index < size:
        raise IndexError('index outside leaves')
    node = size + index >> 1
    while node:
        pull(node)
        node >>= 1

def fold(size, left, right, prepend, initial):
    """半開区間[left, right)を右から結合し、prepend(node, result)の累積値を返す。"""
    if not 0 <= left <= right <= size:
        raise IndexError('invalid half-open range')
    left += size
    right += size
    result = initial
    while left < right:
        height = min((right & -right).bit_length(), (right - left).bit_length()) - 1
        result = prepend((right >> height) - 1, result)
        right -= 1 << height
    return result
from array import array
import sys

class Keyboard:
    __slots__ = ('n', 'size', 'back', 'length', 'value', 'head', 'power')

    def __init__(self, text):
        if isinstance(text, str):
            text = text.encode()
        n = len(text)
        size = 1 << (n - 1).bit_length() if n else 1
        self.n = n
        self.size = size
        self.back = back = array('I', [0]) * (size << 1)
        self.length = length = array('I', [0]) * (size << 1)
        self.value = value = array('I', [0]) * (size << 1)
        self.head = array('I', [0]) * size
        self.power = power = array('I', [1]) * (n + 1)
        p = 1
        for i in range(n):
            c = text[i]
            if c == 66:
                back[size + i] = 1
            elif 49 <= c <= 57:
                length[size + i] = 1
                value[size + i] = c - 48
            else:
                raise ValueError('expected digits 1..9 or B')
            p = p * 10 % 998244353
            power[i + 1] = p
        build(size, self._pull)

    def _prefix(self, node, count):
        length = self.length
        value = self.value
        head = self.head
        power = self.power
        result = 0
        while count and count != length[node]:
            right = node << 1 | 1
            kept = length[node] - length[right]
            if count <= kept:
                node <<= 1
            else:
                result = (result * power[kept] + head[node]) % 998244353
                count -= kept
                node = right
        if count:
            result = (result * power[count] + value[node]) % 998244353
        return result

    def _pull(self, node):
        left = node << 1
        right = left | 1
        back = self.back
        length = self.length
        value = self.value
        kept = length[left] - back[right]
        if kept <= 0:
            back[node] = back[left] - kept
            length[node] = length[right]
            value[node] = value[right]
            self.head[node] = 0
        else:
            prefix = value[left] if kept == length[left] else self._prefix(left, kept)
            back[node] = back[left]
            length[node] = kept + length[right]
            self.head[node] = prefix
            value[node] = (prefix * self.power[length[right]] + value[right]) % 998244353

    def _prepend(self, node, result):
        (back, length, value) = result
        kept = self.length[node] - back
        if kept <= 0:
            return (self.back[node] - kept, length, value)
        prefix = self.value[node] if kept == self.length[node] else self._prefix(node, kept)
        return (self.back[node], kept + length, (prefix * self.power[length] + value) % 998244353)

    def set(self, index, char):
        if not 0 <= index < self.n:
            raise IndexError('index outside string')
        if isinstance(char, (str, bytes)):
            char = ord(char)
        if char != 66 and (not 49 <= char <= 57):
            raise ValueError('expected a digit 1..9 or B')
        node = self.size + index
        self.back[node] = int(char == 66)
        self.length[node] = int(char != 66)
        self.value[node] = 0 if char == 66 else char - 48
        update(self.size, index, self._pull)

    def prod(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError('invalid half-open range')
        return fold(self.size, left, right, self._prepend, (0, 0, 0))

    def tolist(self):
        size = self.size
        return ['B' if self.back[size + i] else str(self.value[size + i]) for i in range(self.n)]

    def __str__(self):
        return ''.join(self.tolist())

    def __repr__(self):
        return 'Keyboard(%r)' % str(self)

def main():
    stream = sys.stdin.buffer
    (n, q) = map(int, stream.readline().split())
    tree = Keyboard(stream.readline().strip())
    if tree.n != n:
        raise ValueError('unexpected string length')
    answers = []
    for _ in range(q):
        (kind, first, second) = stream.readline().split()
        if kind == b'1':
            tree.set(int(first) - 1, second)
        else:
            (_, length, value) = tree.prod(int(first) - 1, int(second))
            answers.append(str(value if length else -1))
    sys.stdout.write('\n'.join(answers) + '\n')
if __name__ == '__main__':
    main()
