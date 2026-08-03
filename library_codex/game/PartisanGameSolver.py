"""左右で合法手が異なる有限ゲームの勝敗を求める。"""

from library_codex.game.SurrealNumber import SurrealNumber

class PartisanGameSolver:
    """Iterative solver for short numeric partisan games."""

    __slots__ = ("options", "memo", "transitions")

    def __init__(self, options):
        self.options = options
        self.memo = {}
        self.transitions = {}

    def get(self, game):
        if game in self.memo:
            return self.memo[game]
        stack = [(game, 0)]
        active = set()
        while stack:
            current, phase = stack.pop()
            if current in self.memo:
                continue
            if phase == 0:
                if current in active:
                    raise ValueError("game graph must be acyclic")
                active.add(current)
                left, right = self.options(current)
                left, right = list(left), list(right)
                self.transitions[current] = left, right
                stack.append((current, 1))
                for child in reversed(left + right):
                    if child not in self.memo:
                        stack.append((child, 0))
            else:
                left, right = self.transitions[current]
                if not left and not right:
                    value = SurrealNumber()
                elif not right:
                    value = max(self.memo[child] for child in left).larger()
                elif not left:
                    value = min(self.memo[child] for child in right).smaller()
                else:
                    lower = max(self.memo[child] for child in left)
                    upper = min(self.memo[child] for child in right)
                    value = SurrealNumber.between(lower, upper)
                self.memo[current] = value
                active.remove(current)
        return self.memo[game]

