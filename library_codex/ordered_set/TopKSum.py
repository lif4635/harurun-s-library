"""要素の追加・削除をしながら大きい方または小さい方k個の和を保つ構造。"""

from library_codex.sequence_structure.ErasableHeap import ErasableHeap

class TopKSum:
    __slots__ = ("k", "largest", "selected", "rest", "selected_count", "total")

    def __init__(self, k, largest=True):
        self.k = k
        self.largest = largest
        self.selected = ErasableHeap(maximize=not largest)
        self.rest = ErasableHeap(maximize=largest)
        self.selected_count = {}
        self.total = 0

    def _selected_add(self, value):
        self.selected.push(value)
        self.selected_count[value] = self.selected_count.get(value, 0) + 1
        self.total += value

    def _selected_remove(self, value):
        self.selected.erase(value)
        count = self.selected_count[value] - 1
        if count:
            self.selected_count[value] = count
        else:
            del self.selected_count[value]
        self.total -= value

    def _rebalance(self):
        while len(self.selected) > self.k:
            value = self.selected.pop()
            count = self.selected_count[value] - 1
            if count:
                self.selected_count[value] = count
            else:
                del self.selected_count[value]
            self.total -= value
            self.rest.push(value)
        while len(self.selected) < self.k and len(self.rest):
            value = self.rest.pop()
            self._selected_add(value)
        if len(self.selected) and len(self.rest):
            selected_worst = self.selected.top()
            rest_best = self.rest.top()
            wrong = rest_best > selected_worst if self.largest else rest_best < selected_worst
            while wrong:
                self._selected_remove(selected_worst)
                self.rest.erase(rest_best)
                self._selected_add(rest_best)
                self.rest.push(selected_worst)
                if not len(self.selected) or not len(self.rest):
                    break
                selected_worst = self.selected.top()
                rest_best = self.rest.top()
                wrong = rest_best > selected_worst if self.largest else rest_best < selected_worst

    def add(self, value):
        if len(self.selected) < self.k:
            self._selected_add(value)
        else:
            self.rest.push(value)
        self._rebalance()

    def discard(self, value):
        if self.selected_count.get(value, 0):
            self._selected_remove(value)
        else:
            self.rest.erase(value)
        self._rebalance()

    def sum(self):
        return self.total
