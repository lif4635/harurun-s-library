"""Binary lifting for a functional graph."""


class Doubling:
    """Jump through successors, optionally accumulating per-vertex values."""

    __slots__ = ("table", "sums")

    def __init__(self, successor, max_steps, values=None):
        levels = max(1, max_steps.bit_length())
        self.table = [list(successor)]
        self.sums = [list(values)] if values is not None else None
        for _ in range(1, levels):
            previous = self.table[-1]
            self.table.append([previous[previous[v]] for v in range(len(previous))])
            if values is not None:
                old = self.sums[-1]
                self.sums.append(
                    [old[v] + old[previous[v]] for v in range(len(previous))]
                )

    def jump(self, vertex, steps):
        level = 0
        while steps:
            if steps & 1:
                vertex = self.table[level][vertex]
            steps >>= 1
            level += 1
        return vertex

    def jump_with_sum(self, vertex, steps):
        if self.sums is None:
            raise ValueError("values were not supplied")
        total = 0
        level = 0
        while steps:
            if steps & 1:
                total += self.sums[level][vertex]
                vertex = self.table[level][vertex]
            steps >>= 1
            level += 1
        return vertex, total
