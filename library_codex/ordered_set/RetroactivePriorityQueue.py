"""過去のpush/popを編集し、全操作の実行後に残る整数を管理する。"""


class RetroactivePriorityQueue:
    __slots__ = ("n", "_base", "_maximum", "_kind", "_value", "_alive", "_balance", "_prefix", "_remaining", "_removed", "_dummy", "_count", "_total", "_pushed")

    def __init__(self, n, maximum=False):
        if n < 0:
            raise ValueError("capacity must be nonnegative")
        self.n, self._maximum = n, maximum
        self._base = base = 1 << n.bit_length()
        self._kind, self._alive = bytearray(n + 1), bytearray(n + 1)
        self._value = [0] * (n + 1)
        self._balance, self._prefix = [0] * (2 * base), [0] * (2 * base)
        self._remaining, self._removed = [-1] * (2 * base), [-1] * (2 * base)
        self._dummy = self._count = self._total = self._pushed = 0
        self._refresh(0)

    def _before(self, a, b):
        if a == 0:
            return False
        if b == 0:
            return True
        x, y = self._value[a], self._value[b]
        return (x > y if self._maximum else x < y) if x != y else a < b

    def _choose(self, a, b, remaining):
        if a < 0:
            return b
        if b < 0:
            return a
        return a if self._before(a, b) == remaining else b

    def _refresh(self, t):
        i = self._base + t
        balance, prefix = self._balance, self._prefix
        remaining, removed = self._remaining, self._removed
        balance[i], remaining[i], removed[i] = 0, -1, -1
        if t == 0:
            balance[i] = self._dummy
            if self._dummy < self.n:
                remaining[i] = 0
            if self._dummy:
                removed[i] = 0
        elif self._kind[t] == 1:
            if self._alive[t]:
                remaining[i] = t
            else:
                removed[i], balance[i] = t, 1
        elif self._kind[t] == 2:
            balance[i] = -1
        prefix[i] = balance[i]
        while i > 1:
            i >>= 1
            a, b = i * 2, i * 2 + 1
            balance[i] = balance[a] + balance[b]
            prefix[i] = min(prefix[a], balance[a] + prefix[b])
            remaining[i] = self._choose(remaining[a], remaining[b], True)
            removed[i] = self._choose(removed[a], removed[b], False)

    def _bridge(self, t, first):
        stack = [(1, 0, self._base, 0)]
        while stack:
            node, left, right, total = stack.pop()
            if (right < t if first else left >= t) or total + self._prefix[node] > 0:
                continue
            if right - left == 1:
                return right
            middle = (left + right) >> 1
            a = (node * 2, left, middle, total)
            b = (node * 2 + 1, middle, right, total + self._balance[node * 2])
            stack.extend((b, a) if first else (a, b))
        return -1 if first else 0

    def _candidate(self, left, right, remaining):
        left += self._base
        right += self._base
        data = self._remaining if remaining else self._removed
        answer = -1
        while left < right:
            if left & 1:
                answer = self._choose(answer, data[left], remaining)
                left += 1
            if right & 1:
                right -= 1
                answer = self._choose(answer, data[right], remaining)
            left >>= 1
            right >>= 1
        return answer

    def _change(self, t, remains, added, removed):
        if t == 0:
            self._dummy += -1 if remains else 1
        else:
            self._alive[t] = remains
            entry = (t - 1, self._value[t])
            if remains:
                self._count += 1
                self._total += entry[1]
                added.append(entry)
            else:
                self._count -= 1
                self._total -= entry[1]
                if entry in added:
                    added.remove(entry)
                else:
                    removed.append(entry)
        self._refresh(t)

    def _erase(self, t, added, removed):
        kind = self._kind[t]
        if kind == 0:
            return
        if kind == 1:
            self._pushed -= self._value[t]
            if self._alive[t]:
                self._change(t, False, added, removed)
            else:
                bridge = self._bridge(t + 1, True)
                self._change(self._candidate(0, bridge, True), False, added, removed)
        else:
            bridge = self._bridge(t, False)
            self._change(self._candidate(bridge, self.n + 1, False), True, added, removed)
        self._kind[t], self._value[t], self._alive[t] = 0, 0, 0
        self._refresh(t)

    def _index(self, time):
        if not 0 <= time < self.n:
            raise IndexError(time)
        return time + 1

    def set_push(self, time, value):
        if not isinstance(value, int):
            raise TypeError("value must be an integer")
        t = self._index(time)
        added, removed = [], []
        self._erase(t, added, removed)
        bridge = self._bridge(t, False)
        x = self._candidate(bridge, self.n + 1, False)
        self._kind[t], self._value[t] = 1, value
        self._pushed += value
        if x < 0 or self._before(x, t):
            self._change(t, True, added, removed)
        else:
            self._alive[t] = 0
            self._refresh(t)
            self._change(x, True, added, removed)
        return removed, added

    def set_pop(self, time):
        t = self._index(time)
        added, removed = [], []
        if self._kind[t] != 2:
            self._erase(t, added, removed)
            bridge = self._bridge(t, True)
            self._change(self._candidate(0, bridge, True), False, added, removed)
            self._kind[t] = 2
            self._refresh(t)
        return removed, added

    def erase(self, time):
        added, removed = [], []
        self._erase(self._index(time), added, removed)
        return removed, added

    def peek(self):
        index = self._remaining[1]
        return self._value[index] if index > 0 else None

    def contains(self, time):
        t = self._index(time)
        return self._kind[t] == 1 and bool(self._alive[t])

    def sum(self):
        return self._total

    def popped_sum(self):
        return self._pushed - self._total

    def items(self):
        return [(t - 1, self._value[t]) for t in range(1, self.n + 1) if self._kind[t] == 1 and self._alive[t]]

    def __len__(self):
        return self._count

    def __str__(self):
        return str(self.items())

    def __repr__(self):
        return "RetroactivePriorityQueue(%r)" % self.items()
