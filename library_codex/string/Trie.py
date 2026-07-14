from array import array


class Trie:
    __slots__ = (
        "alphabet", "symbol_index", "sigma", "dense", "transitions",
        "terminal_count", "subtree_count", "terminal_ids", "parent",
        "parent_symbol", "word_count",
    )

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
                raise ValueError("alphabet symbols must be unique")
            self.alphabet = alphabet
            self.symbol_index = {
                symbol: i for i, symbol in enumerate(alphabet)
            }
            self.sigma = len(alphabet)
            self.dense = True
            self.transitions = array("i", [-1]) * self.sigma
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
            raise ValueError("symbol is outside the fixed alphabet")
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
            yield 0, 0
        for end, symbol in enumerate(sequence, 1):
            node = self.move(node, symbol)
            if node == -1:
                return
            if self.terminal_count[node]:
                yield end, node

    def longest_prefix(self, sequence):
        result = (0, 0) if self.terminal_count[0] else (-1, -1)
        for end, node in self.iter_prefixes(sequence):
            result = end, node
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
            node, prefix = stack.pop()
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
                for symbol, child in self.transitions[node].items():
                    stack.append((child, prefix + (symbol,)))
        return result


DenseTrie = Trie
