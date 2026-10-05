from array import array

class Trie:
    __slots__ = ('alphabet', 'symbol_index', 'sigma', 'dense', 'transitions', 'terminal_count', 'subtree_count', 'terminal_ids', 'parent', 'parent_symbol', 'word_count')

    def __init__(self, alphabet=None):
        self.alphabet = alphabet
        if alphabet is None:
            self.symbol_index = None
            self.sigma = 0
            self.dense = False
            self.transitions = [{}]
        else:
            alphabet = tuple(alphabet)
            if len(set(alphabet)) != len(alphabet):
                raise ValueError('alphabet symbols must be unique')
            self.alphabet = alphabet
            self.symbol_index = {symbol: i for (i, symbol) in enumerate(alphabet)}
            self.sigma = len(alphabet)
            self.dense = True
            self.transitions = array('i', [-1]) * self.sigma
        self.terminal_count = [0]
        self.subtree_count = [0]
        self.terminal_ids = [None]
        self.parent = [-1]
        self.parent_symbol = [None]
        self.word_count = 0

    def __len__(self):
        return len(self.terminal_count)

    @property
    def node_count(self):
        return len(self.terminal_count)

    def _new_node(self, parent, symbol):
        node = len(self.terminal_count)
        if self.dense:
            self.transitions.extend([-1] * self.sigma)
        else:
            self.transitions.append({})
        self.terminal_count.append(0)
        self.subtree_count.append(0)
        self.terminal_ids.append(None)
        self.parent.append(parent)
        self.parent_symbol.append(symbol)
        return node

    def _symbol(self, symbol):
        index = self.symbol_index.get(symbol)
        if index is None:
            raise ValueError('symbol is outside the fixed alphabet')
        return index

    def move(self, node, symbol):
        if node < 0:
            return -1
        if self.dense:
            index = self.symbol_index.get(symbol)
            if index is None:
                return -1
            return self.transitions[node * self.sigma + index]
        return self.transitions[node].get(symbol, -1)

    def add(self, word, word_id=None, count=1):
        assert count > 0
        node = 0
        path = [0]
        if self.dense:
            sigma = self.sigma
            transitions = self.transitions
            for symbol in word:
                index = self._symbol(symbol)
                position = node * sigma + index
                next_node = transitions[position]
                if next_node == -1:
                    next_node = self._new_node(node, symbol)
                    transitions[position] = next_node
                node = next_node
                path.append(node)
        else:
            transitions = self.transitions
            for symbol in word:
                next_node = transitions[node].get(symbol)
                if next_node is None:
                    next_node = self._new_node(node, symbol)
                    transitions[node][symbol] = next_node
                node = next_node
                path.append(node)
        self.terminal_count[node] += count
        self.word_count += count
        for vertex in path:
            self.subtree_count[vertex] += count
        if word_id is not None:
            ids = self.terminal_ids[node]
            if ids is None:
                self.terminal_ids[node] = [word_id]
            else:
                ids.append(word_id)
        return node
    insert = add

    def find(self, word):
        node = 0
        for symbol in word:
            node = self.move(node, symbol)
            if node == -1:
                return -1
        return node

    def count(self, word):
        node = self.find(word)
        return 0 if node == -1 else self.terminal_count[node]

    def contains(self, word):
        return self.count(word) > 0
    __contains__ = contains

    def prefix_count(self, prefix):
        node = self.find(prefix)
        return 0 if node == -1 else self.subtree_count[node]
    count_prefix = prefix_count

    def ids(self, node):
        if node < 0:
            return []
        ids = self.terminal_ids[node]
        return [] if ids is None else ids

    def iter_prefixes(self, sequence):
        node = 0
        if self.terminal_count[0]:
            yield (0, 0)
        for (end, symbol) in enumerate(sequence, 1):
            node = self.move(node, symbol)
            if node == -1:
                return
            if self.terminal_count[node]:
                yield (end, node)

    def longest_prefix(self, sequence):
        result = (0, 0) if self.terminal_count[0] else (-1, -1)
        for (end, node) in self.iter_prefixes(sequence):
            result = (end, node)
        return result

    def erase(self, word, count=1):
        assert count > 0
        node = 0
        path = [0]
        for symbol in word:
            node = self.move(node, symbol)
            if node == -1:
                return False
            path.append(node)
        if self.terminal_count[node] < count:
            return False
        self.terminal_count[node] -= count
        self.word_count -= count
        for vertex in path:
            self.subtree_count[vertex] -= count
        return True
    remove = erase

    def words(self):
        result = []
        stack = [(0, ())]
        while stack:
            (node, prefix) = stack.pop()
            count = self.terminal_count[node]
            if count:
                result.append((prefix, count))
            if self.dense:
                offset = node * self.sigma
                for index in range(self.sigma - 1, -1, -1):
                    child = self.transitions[offset + index]
                    if child != -1:
                        stack.append((child, prefix + (self.alphabet[index],)))
            else:
                for (symbol, child) in self.transitions[node].items():
                    stack.append((child, prefix + (symbol,)))
        return result
DenseTrie = Trie

class AhoCorasick(Trie):
    __slots__ = ('failure', 'output_link', 'output_count', 'bfs_order', 'pattern_nodes', 'pattern_lengths', 'pattern_ids', '_built')

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
        output_count = [0 if ids is None else len(ids) for ids in self.terminal_ids]
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
                    while next_fail and transitions[next_fail * sigma + symbol] == -1:
                        next_fail = failure[next_fail]
                    next_fail = transitions[next_fail * sigma + symbol]
                    if next_fail == -1:
                        next_fail = 0
                    failure[child] = next_fail
                    output_count[child] += output_count[next_fail]
                    output_link[child] = next_fail if self.terminal_ids[next_fail] is not None else output_link[next_fail]
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
                for (symbol, child) in transitions[node].items():
                    fail = failure[node]
                    while fail and symbol not in transitions[fail]:
                        fail = failure[fail]
                    next_fail = transitions[fail].get(symbol, 0)
                    failure[child] = next_fail
                    output_count[child] += output_count[next_fail]
                    output_link[child] = next_fail if self.terminal_ids[next_fail] is not None else output_link[next_fail]
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
        for (pattern_id, count) in zip(self.pattern_ids, counts):
            result[pattern_id] = result.get(pattern_id, 0) + count
        return result

    def match(self, text, heavy=False):
        return self.count_by_id(text) if heavy else self.count_matches(text)

    def finditer(self, text, internal=False):
        self.build()
        ids = self.terminal_ids[0]
        if ids is not None:
            for pattern in ids:
                yield (0, pattern if internal else self.pattern_ids[pattern])
        state = 0
        for (end, symbol) in enumerate(text, 1):
            state = self.step(state, symbol)
            node = state
            while node != -1:
                ids = self.terminal_ids[node]
                if ids is not None:
                    for pattern in ids:
                        yield (end, pattern if internal else self.pattern_ids[pattern])
                node = self.output_link[node]

    def match_positions(self, text):
        result = [[] for _ in range(self.pattern_count)]
        for (end, pattern) in self.finditer(text, True):
            result[pattern].append(end - self.pattern_lengths[pattern])
        return result

    def failure_tree(self):
        self.build()
        tree = [[] for _ in range(len(self))]
        for node in range(1, len(self)):
            tree[self.failure[node]].append(node)
        return tree
DenseAhoCorasick = AhoCorasick
import sys

def main():
    read = sys.stdin.buffer.readline
    count = int(read())
    tree = AhoCorasick()
    for _ in range(count):
        tree.add(read().strip())
    tree.build()
    answer = [str(len(tree))]
    answer.extend((f'{tree.parent[v]} {tree.failure[v]}' for v in range(1, len(tree))))
    answer.append(' '.join(map(str, tree.pattern_nodes)))
    sys.stdout.write('\n'.join(answer))
if __name__ == '__main__':
    main()
