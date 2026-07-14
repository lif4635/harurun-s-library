from array import array


class SuffixAutomaton:
    __slots__ = (
        "alphabet", "symbol_index", "sigma", "dense", "transitions",
        "length", "link", "first_pos", "origin", "key", "is_clone",
        "base_occurrence", "prefix_states", "sequence", "last", "ord",
        "_kind", "_distinct", "_order_cache", "_occurrence_cache",
        "_euler_cache", "_path_count_cache", "_terminal_cache",
    )

    def __init__(self, sequence=None, alphabet=None):
        if alphabet is None:
            self.alphabet = None
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
        self.length = [0]
        self.link = [-1]
        self.first_pos = [-1]
        self.origin = [0]
        self.key = [None]
        self.is_clone = bytearray(1)
        self.base_occurrence = bytearray(1)
        self.prefix_states = []
        self.sequence = []
        self.last = 0
        self.ord = []
        self._kind = 0
        self._distinct = 0
        self._order_cache = None
        self._occurrence_cache = None
        self._euler_cache = None
        self._path_count_cache = None
        self._terminal_cache = None
        if sequence is not None:
            self._set_kind(sequence)
            self.build(sequence)

    def __len__(self):
        return len(self.length)

    @property
    def state_count(self):
        return len(self.length)

    @property
    def node_count(self):
        return len(self.length)

    def size(self):
        return len(self.length)

    @property
    def max_length(self):
        return self.length

    @property
    def distinct_count(self):
        return self._distinct

    def _set_kind(self, sequence):
        if isinstance(sequence, str):
            self._kind = 1
        elif isinstance(sequence, (bytes, bytearray)):
            self._kind = 2
        else:
            self._kind = 0

    def _invalidate(self):
        self.ord = []
        self._order_cache = None
        self._occurrence_cache = None
        self._euler_cache = None
        self._path_count_cache = None
        self._terminal_cache = None

    def _new_state(self, state_length, position, symbol, clone_from=-1):
        state = len(self.length)
        if self.dense:
            sigma = self.sigma
            if clone_from == -1:
                self.transitions.extend([-1] * sigma)
            else:
                left = clone_from * sigma
                self.transitions.extend(self.transitions[left:left + sigma])
        else:
            if clone_from == -1:
                self.transitions.append({})
            else:
                self.transitions.append(self.transitions[clone_from].copy())
        self.length.append(state_length)
        if clone_from == -1:
            self.link.append(-1)
            self.first_pos.append(position)
            self.origin.append(state)
            self.key.append(symbol)
            self.is_clone.append(0)
            self.base_occurrence.append(1)
        else:
            self.link.append(self.link[clone_from])
            self.first_pos.append(self.first_pos[clone_from])
            self.origin.append(clone_from)
            self.key.append(self.key[clone_from])
            self.is_clone.append(1)
            self.base_occurrence.append(0)
        return state

    def _symbol(self, symbol):
        index = self.symbol_index.get(symbol)
        if index is None:
            raise ValueError("symbol is outside the fixed alphabet")
        return index

    def _get(self, state, symbol):
        if self.dense:
            index = self.symbol_index.get(symbol)
            if index is None:
                return -1
            return self.transitions[state * self.sigma + index]
        return self.transitions[state].get(symbol, -1)

    def transition(self, state, symbol):
        if state < 0 or state >= len(self):
            return -1
        return self._get(state, symbol)

    next = transition
    move = transition

    def children(self, state):
        if self.dense:
            result = []
            offset = state * self.sigma
            for index, symbol in enumerate(self.alphabet):
                child = self.transitions[offset + index]
                if child != -1:
                    result.append((symbol, child))
            return result
        return list(self.transitions[state].items())

    chd = children

    def extend(self, symbol):
        if self.dense:
            index = self._symbol(symbol)
        else:
            hash(symbol)
            index = -1
        self._invalidate()
        position = len(self.sequence)
        self.sequence.append(symbol)
        old_last = self.last
        current = self._new_state(
            self.length[old_last] + 1, position, symbol
        )
        self.prefix_states.append(current)
        p = old_last

        if self.dense:
            sigma = self.sigma
            transitions = self.transitions
            while p != -1:
                edge = p * sigma + index
                if transitions[edge] != -1:
                    break
                transitions[edge] = current
                p = self.link[p]
            if p == -1:
                self.link[current] = 0
            else:
                q = transitions[p * sigma + index]
                if self.length[p] + 1 == self.length[q]:
                    self.link[current] = q
                else:
                    clone = self._new_state(
                        self.length[p] + 1,
                        self.first_pos[q],
                        self.key[q],
                        q,
                    )
                    while p != -1:
                        edge = p * sigma + index
                        if transitions[edge] != q:
                            break
                        transitions[edge] = clone
                        p = self.link[p]
                    self.link[q] = clone
                    self.link[current] = clone
        else:
            transitions = self.transitions
            while p != -1 and symbol not in transitions[p]:
                transitions[p][symbol] = current
                p = self.link[p]
            if p == -1:
                self.link[current] = 0
            else:
                q = transitions[p][symbol]
                if self.length[p] + 1 == self.length[q]:
                    self.link[current] = q
                else:
                    clone = self._new_state(
                        self.length[p] + 1,
                        self.first_pos[q],
                        self.key[q],
                        q,
                    )
                    while (
                        p != -1
                        and transitions[p].get(symbol, -1) == q
                    ):
                        transitions[p][symbol] = clone
                        p = self.link[p]
                    self.link[q] = clone
                    self.link[current] = clone

        self.last = current
        self._distinct += self.length[current] - self.length[self.link[current]]
        return current

    push = extend

    def build(self, sequence):
        if not self.sequence:
            self._set_kind(sequence)
        for symbol in sequence:
            self.extend(symbol)
        return self

    def find(self, pattern):
        state = 0
        for symbol in pattern:
            state = self._get(state, symbol)
            if state == -1:
                return -1
        return state

    def contains(self, pattern):
        return self.find(pattern) != -1

    __contains__ = contains

    def state_interval(self, state):
        if state == 0:
            return 0, 0
        return self.length[self.link[state]] + 1, self.length[state]

    def topological_order(self, reverse=False):
        order = self._order_cache
        if order is None:
            n = len(self)
            maximum = len(self.sequence)
            count = [0] * (maximum + 1)
            for value in self.length:
                count[value] += 1
            for i in range(maximum):
                count[i + 1] += count[i]
            order = [0] * n
            for state in range(n - 1, -1, -1):
                value = self.length[state]
                count[value] -= 1
                order[count[value]] = state
            self._order_cache = order
        return order[::-1] if reverse else order

    def tsort(self):
        self.ord = self.topological_order(True)
        return self.ord

    def suffix_link_tree(self):
        tree = [[] for _ in range(len(self))]
        for state in range(1, len(self)):
            tree[self.link[state]].append(state)
        return tree

    link_tree = suffix_link_tree

    def terminal_states(self):
        terminal = self._terminal_cache
        if terminal is None:
            terminal = bytearray(len(self))
            state = self.last
            while state != -1:
                terminal[state] = 1
                state = self.link[state]
            self._terminal_cache = terminal
        return terminal

    def is_terminal_state(self, state):
        return bool(self.terminal_states()[state])

    def occurrence_counts(self):
        occurrence = self._occurrence_cache
        if occurrence is None:
            occurrence = list(self.base_occurrence)
            for state in self.topological_order(True):
                parent = self.link[state]
                if parent != -1:
                    occurrence[parent] += occurrence[state]
            self._occurrence_cache = occurrence
        return occurrence

    endpos_sizes = occurrence_counts

    def count(self, pattern):
        if len(pattern) == 0:
            return len(self.sequence) + 1
        state = self.find(pattern)
        if state == -1:
            return 0
        return self.occurrence_counts()[state]

    def first_occurrence(self, pattern):
        size = len(pattern)
        if size == 0:
            return 0
        state = self.find(pattern)
        if state == -1:
            return -1
        return self.first_pos[state] - size + 1

    def _euler_order(self):
        cache = self._euler_cache
        if cache is not None:
            return cache
        n = len(self)
        head = [-1] * n
        next_edge = [-1] * n
        for state in range(1, n):
            parent = self.link[state]
            next_edge[state] = head[parent]
            head[parent] = state
        tin = [0] * n
        tout = [0] * n
        euler = []
        stack = [0]
        while stack:
            item = stack.pop()
            if item >= 0:
                state = item
                tin[state] = len(euler)
                euler.append(state)
                stack.append(~state)
                child = head[state]
                while child != -1:
                    stack.append(child)
                    child = next_edge[child]
            else:
                state = ~item
                tout[state] = len(euler)
        cache = tin, tout, euler
        self._euler_cache = cache
        return cache

    def occurrences(self, pattern, sort_positions=False):
        size = len(pattern)
        if size == 0:
            return list(range(len(self.sequence) + 1))
        state = self.find(pattern)
        if state == -1:
            return []
        tin, tout, euler = self._euler_order()
        result = []
        first_pos = self.first_pos
        base_occurrence = self.base_occurrence
        for index in range(tin[state], tout[state]):
            node = euler[index]
            if base_occurrence[node]:
                result.append(first_pos[node] - size + 1)
        if sort_positions:
            result.sort()
        return result

    occurrence_positions = occurrences

    def distinct_substrings(self):
        return self._distinct

    number_of_substrings = distinct_substrings

    def sum_distinct_substring_lengths(self):
        result = 0
        length = self.length
        link = self.link
        for state in range(1, len(self)):
            high = length[state]
            low = length[link[state]]
            result += (
                high * (high + 1) - low * (low + 1)
            ) >> 1
        return result

    def _path_counts(self):
        counts = self._path_count_cache
        if counts is not None:
            return counts
        counts = [0] * len(self)
        if self.dense:
            sigma = self.sigma
            transitions = self.transitions
            for state in self.topological_order(True):
                total = 0
                offset = state * sigma
                for index in range(sigma):
                    child = transitions[offset + index]
                    if child != -1:
                        total += 1 + counts[child]
                counts[state] = total
        else:
            transitions = self.transitions
            for state in self.topological_order(True):
                total = 0
                for child in transitions[state].values():
                    total += 1 + counts[child]
                counts[state] = total
        self._path_count_cache = counts
        return counts

    def _pack(self, symbols):
        if self._kind == 1:
            return "".join(symbols)
        if self._kind == 2:
            return bytes(symbols)
        return tuple(symbols)

    def _slice(self, left, right):
        symbols = self.sequence[left:right]
        return self._pack(symbols)

    def text(self):
        return self._pack(self.sequence)

    def kth_substring(self, k, one_indexed=False):
        if one_indexed:
            k -= 1
        if k < 0:
            raise IndexError("substring index is out of range")
        path_count = self._path_counts()
        if k >= path_count[0]:
            raise IndexError("substring index is out of range")
        state = 0
        result = []
        while True:
            children = self.children(state)
            try:
                children.sort(key=lambda edge: edge[0])
            except TypeError as error:
                raise TypeError(
                    "alphabet symbols must be mutually comparable"
                ) from error
            for symbol, child in children:
                block = 1 + path_count[child]
                if k >= block:
                    k -= block
                    continue
                result.append(symbol)
                if k == 0:
                    return self._pack(result)
                k -= 1
                state = child
                break

    def longest_repeated_substring_info(self, min_occurrences=2):
        if min_occurrences <= 0:
            raise ValueError("min_occurrences must be positive")
        occurrence = self.occurrence_counts()
        best_state = 0
        best_length = 0
        for state in range(1, len(self)):
            state_length = self.length[state]
            if (
                occurrence[state] >= min_occurrences
                and state_length > best_length
            ):
                best_state = state
                best_length = state_length
        if best_state == 0:
            return 0, 0, 0
        start = self.first_pos[best_state] - best_length + 1
        return best_length, start, best_state

    def longest_repeated_substring(self, min_occurrences=2):
        length, start, _ = self.longest_repeated_substring_info(
            min_occurrences
        )
        return self._slice(start, start + length)

    def longest_common_substring(self, other):
        state = 0
        matched = 0
        best_length = 0
        best_state = 0
        best_end = -1
        length = self.length
        link = self.link
        for end, symbol in enumerate(other):
            child = self._get(state, symbol)
            while state and child == -1:
                state = link[state]
                if matched > length[state]:
                    matched = length[state]
                child = self._get(state, symbol)
            if child == -1:
                state = 0
                matched = 0
                continue
            state = child
            matched += 1
            if matched > best_length:
                best_length = matched
                best_state = state
                best_end = end
        if best_length == 0:
            return 0, 0, 0
        base_start = self.first_pos[best_state] - best_length + 1
        other_start = best_end - best_length + 1
        return best_length, base_start, other_start

    lcs = longest_common_substring


DenseSuffixAutomaton = SuffixAutomaton
