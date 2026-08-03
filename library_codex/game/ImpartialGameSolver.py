"""有限不偏ゲームのGrundy数と勝敗をmemo化探索で求める。"""

class ImpartialGameSolver:
    """Iterative Grundy solver for a DAG of hashable board states."""

    __slots__ = ("options", "splittable", "with_moves", "memo", "transitions")

    def __init__(self, options, splittable=False, with_moves=False):
        self.options = options
        self.splittable = splittable
        self.with_moves = with_moves
        self.memo = {}
        self.transitions = {}

    def _game_and_move(self, transition):
        if self.with_moves:
            return transition[0], transition[1]
        return transition, None

    def _boards(self, game):
        return tuple(game) if self.splittable else (game,)

    def get(self, board):
        if board in self.memo:
            return self.memo[board]
        stack = [(board, 0)]
        active = set()
        while stack:
            current, phase = stack.pop()
            if current in self.memo:
                continue
            if phase == 0:
                if current in active:
                    raise ValueError("game graph must be acyclic")
                active.add(current)
                transitions = list(self.options(current))
                self.transitions[current] = transitions
                stack.append((current, 1))
                dependencies = []
                for transition in transitions:
                    game, _ = self._game_and_move(transition)
                    dependencies.extend(self._boards(game))
                for dependency in reversed(dependencies):
                    if dependency not in self.memo:
                        stack.append((dependency, 0))
            else:
                reachable = set()
                for transition in self.transitions[current]:
                    game, _ = self._game_and_move(transition)
                    value = 0
                    for dependency in self._boards(game):
                        value ^= self.memo[dependency]
                    reachable.add(value)
                grundy = 0
                while grundy in reachable:
                    grundy += 1
                self.memo[current] = grundy
                active.remove(current)
        return self.memo[board]

    grundy = get

    def get_sum(self, boards):
        result = 0
        for board in boards:
            result ^= self.get(board)
        return result

    def get_best_move(self, game):
        if not self.with_moves:
            raise ValueError("with_moves=True is required")
        if self.splittable:
            total = self.get_sum(game)
            if total == 0:
                return None
            for index, board in enumerate(game):
                current = self.get(board)
                for transition in self.options(board):
                    next_game, move = self._game_and_move(transition)
                    next_value = self.get_sum(self._boards(next_game))
                    if total ^ current ^ next_value == 0:
                        return index, move
            return None
        if self.get(game) == 0:
            return None
        for transition in self.options(game):
            next_game, move = self._game_and_move(transition)
            next_value = 0
            for board in self._boards(next_game):
                next_value ^= self.get(board)
            if next_value == 0:
                return move
        return None

