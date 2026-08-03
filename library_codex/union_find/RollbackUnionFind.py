class RollbackUnionFind:
    __slots__ = (
        "n", "parent", "par", "data", "history", "snapshot_state",
        "component_count", "values",
    )

    def __init__(self, n, values=None):
        assert n >= 0
        self.n = n
        parent = [-1] * n
        self.parent = parent
        self.par = parent
        self.data = parent
        self.history = []
        self.snapshot_state = 0
        self.component_count = n
        if values is None:
            self.values = None
        else:
            values = list(values)
            assert len(values) == n
            self.values = values

    def leader(self, x):
        parent = self.parent
        while parent[x] >= 0:
            x = parent[x]
        return x

    find = leader
    root = leader

    def same(self, x, y):
        return self.leader(x) == self.leader(y)

    connected = same

    def size(self, x):
        return -self.parent[self.leader(x)]

    def merge(self, x, y):
        parent = self.parent
        x = self.leader(x)
        y = self.leader(y)
        if x == y:
            self.history.append(None)
            return False
        if parent[x] > parent[y]:
            x, y = y, x
        values = self.values
        old_value = None if values is None else values[x]
        self.history.append((x, parent[x], y, parent[y], old_value))
        parent[x] += parent[y]
        parent[y] = x
        if values is not None:
            values[x] = old_value + values[y]
        self.component_count -= 1
        return True

    unite = merge
    union = merge

    def add_value(self, x, delta):
        values = self.values
        assert values is not None
        x = self.leader(x)
        old_value = values[x]
        self.history.append((x, old_value))
        values[x] = old_value + delta
        return values[x]

    def component_value(self, x):
        values = self.values
        assert values is not None
        return values[self.leader(x)]

    component_sum = component_value

    def get_state(self):
        return len(self.history)

    state = get_state

    def snapshot(self):
        state = len(self.history)
        self.snapshot_state = state
        return state

    def clear_snapshot(self):
        self.snapshot_state = 0

    def undo(self):
        assert self.history
        record = self.history.pop()
        if self.snapshot_state > len(self.history):
            self.snapshot_state = 0
        if record is None:
            return False
        if len(record) == 2:
            x, old_value = record
            self.values[x] = old_value
            return True
        x, parent_x, y, parent_y, old_value = record
        parent = self.parent
        parent[x] = parent_x
        parent[y] = parent_y
        if self.values is not None:
            self.values[x] = old_value
        self.component_count += 1
        return True

    def rollback(self, state=None):
        if state is None or state == -1:
            state = self.snapshot_state
        assert 0 <= state <= len(self.history)
        while len(self.history) > state:
            self.undo()

    def count(self):
        return self.component_count

    connect = count

    def groups(self):
        result = {}
        for v in range(self.n):
            root = self.leader(v)
            if root in result:
                result[root].append(v)
            else:
                result[root] = [v]
        return list(result.values())
