"""値の変更をsnapshot時点まで巻き戻せる配列。"""


class RollbackArray:
    """point assignmentを履歴へ保存するrollback可能な配列。"""

    __slots__ = ("values", "history")

    def __init__(self, values):
        self.values = list(values)
        self.history = []

    def get(self, index):
        return self.values[index]

    def set(self, index, value):
        self.history.append((index, self.values[index]))
        self.values[index] = value

    def snapshot(self):
        return len(self.history)

    def undo(self):
        if not self.history:
            raise IndexError("no update to undo")
        index, value = self.history.pop()
        self.values[index] = value

    def rollback(self, state):
        if not 0 <= state <= len(self.history):
            raise ValueError("invalid rollback state")
        while len(self.history) > state:
            index, value = self.history.pop()
            self.values[index] = value

    def tolist(self):
        return self.values[:]

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        return self.values[index]

    def __str__(self):
        return str(self.values)

    def __repr__(self):
        return "RollbackArray(%r)" % self.values
