from array import array


class PalindromicTree:
    __slots__ = (
        "alphabet", "symbol_index", "sigma", "dense", "transitions",
        "length", "link", "first_pos", "parent", "parent_symbol",
        "direct_count", "suffix_depth", "sequence", "suffix_states",
        "last", "longest", "total_count", "_kind",
        "_occurrence_cache", "_position_cache",
    )

    def __init__(self, sequence=None, alphabet=None):
        if alphabet is None:
            self.alphabet = None
            self.symbol_index = None
            self.sigma = 0
            self.dense = False
            self.transitions = [{}, {}]
        else:
            alphabet = tuple(alphabet)
            if len(set(alphabet)) != len(alphabet):
                raise ValueError("alphabet symbols must be unique")
            self.alphabet = alphabet
            self.symbol_index = {
                symbol: index for index, symbol in enumerate(alphabet)
            }
            self.sigma = len(alphabet)
            self.dense = True
            self.transitions = array("i", [-1]) * (2 * self.sigma)
        self.length = [-1, 0]
        self.link = [0, 0]
        self.first_pos = [-1, -1]
        self.parent = [-1, -1]
        self.parent_symbol = [None, None]
        self.direct_count = [0, 0]
        self.suffix_depth = [0, 0]
        self.sequence = []
        self.suffix_states = []
        self.last = 1
        self.longest = 1
        self.total_count = 0
        self._kind = 0
        self._occurrence_cache = None
        self._position_cache = None
        if sequence is not None:
            self._set_kind(sequence)
            self.build(sequence)

    def __len__(self):
        return len(self.length)

    @property
    def node_count(self):
        return len(self.length)

    @property
    def state_count(self):
        return len(self.length)

    @property
    def distinct_count(self):
        return len(self.length) - 2

    def size(self):
        return len(self.length)

    def _set_kind(self, sequence):
        if isinstance(sequence, str):
            self._kind = 1
        elif isinstance(sequence, (bytes, bytearray)):
            self._kind = 2
        else:
            self._kind = 0

    def _pack(self, symbols):
        if self._kind == 1:
            return "".join(symbols)
        if self._kind == 2:
            return bytes(symbols)
        return tuple(symbols)

    def _slice(self, left, right):
        return self._pack(self.sequence[left:right])

    def text(self):
        return self._pack(self.sequence)

    def _new_node(self, node_length, position, parent, symbol):
        node = len(self.length)
        if self.dense:
            self.transitions.extend([-1] * self.sigma)
        else:
            self.transitions.append({})
        self.length.append(node_length)
        self.link.append(0)
        self.first_pos.append(position - node_length + 1)
        self.parent.append(parent)
        self.parent_symbol.append(symbol)
        self.direct_count.append(0)
        self.suffix_depth.append(0)
        return node

    def _get(self, node, symbol):
        if self.dense:
            index = self.symbol_index.get(symbol)
            if index is None:
                return -1
            return self.transitions[node * self.sigma + index]
        return self.transitions[node].get(symbol, -1)

    def transition(self, node, symbol):
        if node < 0 or node >= len(self):
            return -1
        return self._get(node, symbol)

    next = transition
    move = transition

    def children(self, node):
        if self.dense:
            result = []
            offset = node * self.sigma
            for index, symbol in enumerate(self.alphabet):
                child = self.transitions[offset + index]
                if child != -1:
                    result.append((symbol, child))
            return result
        return list(self.transitions[node].items())

    def _find_suffix(self, node, position, symbol):
        sequence = self.sequence
        length = self.length
        link = self.link
        while True:
            left = position - length[node] - 1
            if left >= 0 and sequence[left] == symbol:
                return node
            node = link[node]

    def extend(self, symbol):
        if self.dense:
            index = self.symbol_index.get(symbol)
            if index is None:
                raise ValueError("symbol is outside the fixed alphabet")
        else:
            hash(symbol)
            index = -1
        self._occurrence_cache = None
        self._position_cache = None
        position = len(self.sequence)
        self.sequence.append(symbol)
        parent = self._find_suffix(self.last, position, symbol)

        if self.dense:
            edge = parent * self.sigma + index
            node = self.transitions[edge]
        else:
            node = self.transitions[parent].get(symbol, -1)
        if node == -1:
            node_length = self.length[parent] + 2
            node = self._new_node(node_length, position, parent, symbol)
            if self.dense:
                self.transitions[edge] = node
            else:
                self.transitions[parent][symbol] = node
            if node_length == 1:
                suffix = 1
            else:
                suffix_parent = self._find_suffix(
                    self.link[parent], position, symbol
                )
                suffix = self._get(suffix_parent, symbol)
            self.link[node] = suffix
            self.suffix_depth[node] = self.suffix_depth[suffix] + 1
            if node_length > self.length[self.longest]:
                self.longest = node

        self.direct_count[node] += 1
        self.last = node
        self.suffix_states.append(node)
        self.total_count += self.suffix_depth[node]
        return node

    push = extend

    def build(self, sequence):
        if not self.sequence:
            self._set_kind(sequence)
        for symbol in sequence:
            self.extend(symbol)
        return self

    def find(self, palindrome):
        size = len(palindrome)
        if size == 0:
            return 1
        node = 0 if size & 1 else 1
        left = (size - 1) >> 1
        while left >= 0:
            if palindrome[left] != palindrome[size - 1 - left]:
                return -1
            node = self._get(node, palindrome[left])
            if node == -1:
                return -1
            left -= 1
        return node

    def contains(self, palindrome):
        return self.find(palindrome) != -1

    __contains__ = contains

    def palindrome(self, node):
        if node < 2:
            return self._slice(0, 0)
        left = self.first_pos[node]
        return self._slice(left, left + self.length[node])

    get_palindrome = palindrome

    def distinct_palindromes(self):
        return [self.palindrome(node) for node in range(2, len(self))]

    def longest_palindrome(self):
        return self.palindrome(self.longest)

    def occurrence_counts(self):
        occurrence = self._occurrence_cache
        if occurrence is None:
            occurrence = self.direct_count.copy()
            for node in range(len(self) - 1, 1, -1):
                occurrence[self.link[node]] += occurrence[node]
            self._occurrence_cache = occurrence
        return occurrence

    def count(self, palindrome):
        if len(palindrome) == 0:
            return len(self.sequence) + 1
        node = self.find(palindrome)
        if node == -1:
            return 0
        return self.occurrence_counts()[node]

    def first_occurrence(self, palindrome):
        if len(palindrome) == 0:
            return 0
        node = self.find(palindrome)
        return -1 if node == -1 else self.first_pos[node]

    def suffix_link_tree(self):
        tree = [[] for _ in range(len(self))]
        for node in range(1, len(self)):
            tree[self.link[node]].append(node)
        return tree

    link_tree = suffix_link_tree

    def _position_order(self):
        cache = self._position_cache
        if cache is not None:
            return cache
        n = len(self)
        head = [-1] * n
        next_edge = [-1] * n
        for node in range(1, n):
            parent = self.link[node]
            next_edge[node] = head[parent]
            head[parent] = node
        tin = [0] * n
        tout = [0] * n
        euler = []
        stack = [0]
        while stack:
            item = stack.pop()
            if item >= 0:
                node = item
                tin[node] = len(euler)
                euler.append(node)
                stack.append(~node)
                child = head[node]
                while child != -1:
                    stack.append(child)
                    child = next_edge[child]
            else:
                node = ~item
                tout[node] = len(euler)

        prefix = [0] * (n + 1)
        for index, node in enumerate(euler):
            prefix[index + 1] = prefix[index] + self.direct_count[node]
        ordered_ends = [0] * len(self.sequence)
        cursor = prefix[:-1]
        for end, node in enumerate(self.suffix_states):
            index = cursor[tin[node]]
            ordered_ends[index] = end
            cursor[tin[node]] = index + 1
        cache = tin, tout, prefix, ordered_ends
        self._position_cache = cache
        return cache

    def occurrences(self, palindrome, sort_positions=False):
        size = len(palindrome)
        if size == 0:
            return list(range(len(self.sequence) + 1))
        node = self.find(palindrome)
        if node == -1:
            return []
        tin, tout, prefix, ordered_ends = self._position_order()
        left = prefix[tin[node]]
        right = prefix[tout[node]]
        result = [
            ordered_ends[index] - size + 1
            for index in range(left, right)
        ]
        if sort_positions:
            result.sort()
        return result

    occurrence_positions = occurrences

    def longest_suffix_state(self, position=None):
        if position is None:
            return self.last
        return self.suffix_states[position]

    def palindromic_suffixes(self, position=None, include_empty=False):
        node = self.longest_suffix_state(position)
        result = []
        while node > 1:
            result.append(node)
            node = self.link[node]
        if include_empty:
            result.append(1)
        return result

    def frequencies(self):
        occurrence = self.occurrence_counts()
        return [
            (self.length[node], self.first_pos[node], occurrence[node])
            for node in range(len(self) - 1, 1, -1)
        ]

    get_freq = frequencies


Eertree = PalindromicTree
eertree = PalindromicTree
DensePalindromicTree = PalindromicTree
