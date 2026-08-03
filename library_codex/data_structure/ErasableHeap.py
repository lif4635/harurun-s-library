"""heapから任意の既存値を遅延削除できるpriority queue。"""

import heapq

class ErasableHeap:
    __slots__ = ("heap", "erased", "sign", "size")

    def __init__(self, values=(), maximize=False):
        self.sign = -1 if maximize else 1
        self.heap = [self.sign * value for value in values]
        heapq.heapify(self.heap)
        self.erased = []
        self.size = len(self.heap)

    def _clean(self):
        heap = self.heap
        erased = self.erased
        while erased and heap and erased[0] == heap[0]:
            heapq.heappop(erased)
            heapq.heappop(heap)

    def push(self, value):
        heapq.heappush(self.heap, self.sign * value)
        self.size += 1

    def erase(self, value):
        heapq.heappush(self.erased, self.sign * value)
        self.size -= 1
        self._clean()

    remove = erase

    def top(self):
        self._clean()
        if not self.heap:
            raise IndexError("top from empty ErasableHeap")
        return self.sign * self.heap[0]

    def pop(self):
        value = self.top()
        heapq.heappop(self.heap)
        self.size -= 1
        self._clean()
        return value

    def __len__(self):
        return self.size
