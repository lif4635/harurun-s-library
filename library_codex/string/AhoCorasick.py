from library_codex.string.Trie import Trie


class AhoCorasick(Trie):
    __slots__ = (
        "failure", "output_link", "output_count", "bfs_order",
        "pattern_nodes", "pattern_lengths", "pattern_ids", "_built",
    )

    def __init__(self, alphabet=None):
        super().__init__(alphabet)
        self.failure = []
        self.output_link = []
        self.output_count = []
        self.bfs_order = []
        self.pattern_nodes = []
        self.pattern_lengths = []
        self.pattern_ids = []
        self._built = False

    def add(self, pattern, pattern_id=None):
        assert not self._built
        internal_id = len(self.pattern_nodes)
        if pattern_id is None:
            pattern_id = internal_id
        node = super().add(pattern, internal_id)
        self.pattern_nodes.append(node)
        self.pattern_lengths.append(len(pattern))
        self.pattern_ids.append(pattern_id)
        return internal_id

    insert = add

    @property
    def pattern_count(self):
        return len(self.pattern_nodes)

    def build(self, complete_transitions=True):
        if self._built:
            return self
        self._built = True
        n = len(self)
        failure = [0] * n
        output_link = [-1] * n
        output_count = [
            0 if ids is None else len(ids) for ids in self.terminal_ids
        ]
        order = [0]
        queue = []

        if self.dense:
            sigma = self.sigma
            transitions = self.transitions
            for symbol in range(sigma):
                child = transitions[symbol]
                if child == -1:
                    if complete_transitions:
                        transitions[symbol] = 0
                else:
                    failure[child] = 0
                    output_count[child] += output_count[0]
                    if self.terminal_ids[0] is not None:
                        output_link[child] = 0
                    queue.append(child)
            for node in queue:
                order.append(node)
                fail = failure[node]
                offset = node * sigma
                fail_offset = fail * sigma
                for symbol in range(sigma):
                    position = offset + symbol
                    child = transitions[position]
                    if child == -1:
                        if complete_transitions:
                            transitions[position] = transitions[fail_offset + symbol]
                        continue
                    next_fail = fail
                    while (
                        next_fail
                        and transitions[next_fail * sigma + symbol] == -1
                    ):
                        next_fail = failure[next_fail]
                    next_fail = transitions[next_fail * sigma + symbol]
                    if next_fail == -1:
                        next_fail = 0
                    failure[child] = next_fail
                    output_count[child] += output_count[next_fail]
                    output_link[child] = (
                        next_fail
                        if self.terminal_ids[next_fail] is not None
                        else output_link[next_fail]
                    )
                    queue.append(child)
        else:
            transitions = self.transitions
            for child in transitions[0].values():
                failure[child] = 0
                output_count[child] += output_count[0]
                if self.terminal_ids[0] is not None:
                    output_link[child] = 0
                queue.append(child)
            for node in queue:
                order.append(node)
                for symbol, child in transitions[node].items():
                    fail = failure[node]
                    while fail and symbol not in transitions[fail]:
                        fail = failure[fail]
                    next_fail = transitions[fail].get(symbol, 0)
                    failure[child] = next_fail
                    output_count[child] += output_count[next_fail]
                    output_link[child] = (
                        next_fail
                        if self.terminal_ids[next_fail] is not None
                        else output_link[next_fail]
                    )
                    queue.append(child)

        self.failure = failure
        self.output_link = output_link
        self.output_count = output_count
        self.bfs_order = order
        return self

    make_failure = build

    def step(self, state, symbol):
        self.build()
        if self.dense:
            index = self.symbol_index.get(symbol)
            if index is None:
                return 0
            next_state = self.transitions[state * self.sigma + index]
            if next_state != -1:
                return next_state
            while state and next_state == -1:
                state = self.failure[state]
                next_state = self.transitions[state * self.sigma + index]
            return 0 if next_state == -1 else next_state
        transitions = self.transitions
        while state and symbol not in transitions[state]:
            state = self.failure[state]
        return transitions[state].get(symbol, 0)

    move = step

    def count_matches(self, text):
        self.build()
        state = 0
        result = self.output_count[0]
        for symbol in text:
            state = self.step(state, symbol)
            result += self.output_count[state]
        return result

    def count_by_pattern(self, text):
        self.build()
        visits = [0] * len(self)
        visits[0] = 1
        state = 0
        for symbol in text:
            state = self.step(state, symbol)
            visits[state] += 1
        failure = self.failure
        for node in reversed(self.bfs_order[1:]):
            visits[failure[node]] += visits[node]
        return [visits[node] for node in self.pattern_nodes]

    def count_by_id(self, text):
        counts = self.count_by_pattern(text)
        result = {}
        for pattern_id, count in zip(self.pattern_ids, counts):
            result[pattern_id] = result.get(pattern_id, 0) + count
        return result

    def match(self, text, heavy=False):
        return self.count_by_id(text) if heavy else self.count_matches(text)

    def finditer(self, text, internal=False):
        self.build()
        ids = self.terminal_ids[0]
        if ids is not None:
            for pattern in ids:
                yield 0, pattern if internal else self.pattern_ids[pattern]
        state = 0
        for end, symbol in enumerate(text, 1):
            state = self.step(state, symbol)
            node = state
            while node != -1:
                ids = self.terminal_ids[node]
                if ids is not None:
                    for pattern in ids:
                        yield (
                            end,
                            pattern if internal else self.pattern_ids[pattern],
                        )
                node = self.output_link[node]

    def match_positions(self, text):
        result = [[] for _ in range(self.pattern_count)]
        for end, pattern in self.finditer(text, True):
            result[pattern].append(end - self.pattern_lengths[pattern])
        return result

    def failure_tree(self):
        self.build()
        tree = [[] for _ in range(len(self))]
        for node in range(1, len(self)):
            tree[self.failure[node]].append(node)
        return tree


DenseAhoCorasick = AhoCorasick
