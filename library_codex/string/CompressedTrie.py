class CompressedTrie:
    __slots__ = (
        "words", "parent", "depth", "edge_word", "edge_left", "edge_right",
        "children", "terminal_count", "subtree_count", "word_count",
    )

    def __init__(self, words=()):
        self.words = []
        self.parent = [-1]
        self.depth = [0]
        self.edge_word = [-1]
        self.edge_left = [0]
        self.edge_right = [0]
        self.children = [{}]
        self.terminal_count = [0]
        self.subtree_count = [0]
        self.word_count = 0
        for word in words:
            self.add(word)

    def __len__(self):
        return len(self.parent)

    @property
    def node_count(self):
        return len(self.parent)

    def _new_node(self, parent, word_id, left, right):
        node = len(self.parent)
        self.parent.append(parent)
        self.depth.append(self.depth[parent] + right - left)
        self.edge_word.append(word_id)
        self.edge_left.append(left)
        self.edge_right.append(right)
        self.children.append({})
        self.terminal_count.append(0)
        self.subtree_count.append(0)
        return node

    def add(self, word, count=1):
        assert count > 0
        word_id = len(self.words)
        self.words.append(word)
        node = 0
        position = 0
        length = len(word)
        while position < length:
            symbol = word[position]
            child = self.children[node].get(symbol)
            if child is None:
                child = self._new_node(node, word_id, position, length)
                self.children[node][symbol] = child
                node = child
                position = length
                break
            old_word = self.words[self.edge_word[child]]
            old_left = self.edge_left[child]
            old_right = self.edge_right[child]
            common = 0
            limit = min(length - position, old_right - old_left)
            while common < limit and word[position + common] == old_word[old_left + common]:
                common += 1
            if common == old_right - old_left:
                node = child
                position += common
                continue

            middle = self._new_node(
                node, self.edge_word[child], old_left, old_left + common
            )
            self.subtree_count[middle] = self.subtree_count[child]
            self.children[node][symbol] = middle
            self.parent[child] = middle
            self.edge_left[child] = old_left + common
            old_symbol = old_word[old_left + common]
            self.children[middle][old_symbol] = child
            position += common
            if position == length:
                node = middle
            else:
                new_child = self._new_node(
                    middle, word_id, position, length
                )
                self.children[middle][word[position]] = new_child
                node = new_child
                position = length
            break

        self.terminal_count[node] += count
        self.word_count += count
        while node != -1:
            self.subtree_count[node] += count
            node = self.parent[node]
        return word_id

    insert = add

    def _walk(self, sequence):
        node = 0
        position = 0
        length = len(sequence)
        while position < length:
            child = self.children[node].get(sequence[position])
            if child is None:
                return -1, 0, False
            word = self.words[self.edge_word[child]]
            left = self.edge_left[child]
            right = self.edge_right[child]
            offset = 0
            while (
                position < length
                and left + offset < right
                and sequence[position] == word[left + offset]
            ):
                position += 1
                offset += 1
            if position == length:
                return child, offset, offset == right - left
            if left + offset != right:
                return -1, 0, False
            node = child
        return node, 0, True

    def find(self, word):
        node, _, exact = self._walk(word)
        return node if exact else -1

    def count(self, word):
        node = self.find(word)
        return 0 if node == -1 else self.terminal_count[node]

    def contains(self, word):
        return self.count(word) > 0

    __contains__ = contains

    def prefix_count(self, prefix):
        node, _, _ = self._walk(prefix)
        return 0 if node == -1 else self.subtree_count[node]

    count_prefix = prefix_count

    def edge_label(self, node):
        if node == 0:
            return self.words[0][0:0] if self.words else ()
        word = self.words[self.edge_word[node]]
        return word[self.edge_left[node]:self.edge_right[node]]

    def to_graph(self):
        graph = [[] for _ in range(len(self))]
        for node in range(1, len(self)):
            graph[self.parent[node]].append((node, self.edge_label(node)))
        return graph
