"""無向グラフの橋を縮約した森で、頂点間の橋に関するqueryを処理する。"""

from library_codex.graph_connectivity.TwoEdgeConnectedComponents import (
    TwoEdgeConnectedComponents,
)


class BridgeForest:
    """2-edge-connected componentを縮約した森とbinary liftingを構築する。"""

    __slots__ = (
        "n", "decomposition", "component", "forest", "depth", "root",
        "parent_bridge", "up", "tin", "tout", "_bridge_child",
    )

    def __init__(self, n, edges):
        edges = list(edges)
        decomposition = TwoEdgeConnectedComponents(n, edges)
        component = decomposition.component
        forest = decomposition.bridge_forest(True)
        count = decomposition.num_components
        depth = [0] * count
        root = [-1] * count
        parent = [-1] * count
        parent_bridge = [-1] * count
        tin = [0] * count
        tout = [0] * count
        bridge_child = [-1] * len(edges)
        timer = 0

        for start in range(count):
            if root[start] != -1:
                continue
            root[start] = start
            stack = [(start, -1, -1, 0)]
            while stack:
                vertex, par, edge_id, phase = stack.pop()
                if phase == 0:
                    parent[vertex] = par
                    parent_bridge[vertex] = edge_id
                    tin[vertex] = timer
                    timer += 1
                    if edge_id != -1:
                        bridge_child[edge_id] = vertex
                    stack.append((vertex, par, edge_id, 1))
                    for target, next_edge in reversed(forest[vertex]):
                        if target == par:
                            continue
                        root[target] = start
                        depth[target] = depth[vertex] + 1
                        stack.append((target, vertex, next_edge, 0))
                else:
                    tout[vertex] = timer

        levels = max(1, count.bit_length())
        first = [vertex if par == -1 else par
                 for vertex, par in enumerate(parent)]
        up = [first]
        for _ in range(1, levels):
            previous = up[-1]
            up.append([previous[previous[vertex]] for vertex in range(count)])

        self.n = n
        self.decomposition = decomposition
        self.component = component
        self.forest = forest
        self.depth = depth
        self.root = root
        self.parent_bridge = parent_bridge
        self.up = up
        self.tin = tin
        self.tout = tout
        self._bridge_child = bridge_child

    def _jump(self, vertex, distance):
        level = 0
        while distance:
            if distance & 1:
                vertex = self.up[level][vertex]
            distance >>= 1
            level += 1
        return vertex

    def _lca(self, first, second):
        if self.root[first] != self.root[second]:
            return -1
        if self.depth[first] < self.depth[second]:
            first, second = second, first
        first = self._jump(first, self.depth[first] - self.depth[second])
        if first == second:
            return first
        for level in range(len(self.up) - 1, -1, -1):
            if self.up[level][first] != self.up[level][second]:
                first = self.up[level][first]
                second = self.up[level][second]
        return self.up[0][first]

    def bridge_distance(self, first, second):
        """二頂点を結ぶpathに含まれる橋の本数を返す。"""
        if not 0 <= first < self.n or not 0 <= second < self.n:
            raise IndexError("vertex is outside the graph")
        first = self.component[first]
        second = self.component[second]
        ancestor = self._lca(first, second)
        if ancestor == -1:
            return -1
        return (
            self.depth[first] + self.depth[second]
            - (self.depth[ancestor] << 1)
        )

    def bridge_path(self, first, second):
        """firstからsecondへ進む順にpath上のbridge edge IDを返す。"""
        if not 0 <= first < self.n or not 0 <= second < self.n:
            raise IndexError("vertex is outside the graph")
        first = self.component[first]
        second = self.component[second]
        ancestor = self._lca(first, second)
        if ancestor == -1:
            return None
        prefix = []
        current = first
        while current != ancestor:
            prefix.append(self.parent_bridge[current])
            current = self.up[0][current]
        suffix = []
        current = second
        while current != ancestor:
            suffix.append(self.parent_bridge[current])
            current = self.up[0][current]
        prefix.extend(reversed(suffix))
        return prefix

    def kth_bridge(self, first, second, k):
        """firstからsecondへのpathで0始まりk番目のbridge edge IDを返す。"""
        if not 0 <= first < self.n or not 0 <= second < self.n:
            raise IndexError("vertex is outside the graph")
        first = self.component[first]
        second = self.component[second]
        ancestor = self._lca(first, second)
        if ancestor == -1:
            raise ValueError("vertices are disconnected")
        first_length = self.depth[first] - self.depth[ancestor]
        second_length = self.depth[second] - self.depth[ancestor]
        if not 0 <= k < first_length + second_length:
            raise IndexError("bridge index is outside the path")
        if k < first_length:
            return self.parent_bridge[self._jump(first, k)]
        offset = k - first_length
        child = self._jump(second, second_length - offset - 1)
        return self.parent_bridge[child]

    def is_bridge_separator(self, edge_id, first, second):
        """edge_idを削除するとfirstとsecondが別成分になるか判定する。"""
        if not 0 <= edge_id < len(self._bridge_child):
            raise IndexError("edge ID is outside the graph")
        if not 0 <= first < self.n or not 0 <= second < self.n:
            raise IndexError("vertex is outside the graph")
        child = self._bridge_child[edge_id]
        if child == -1:
            return False
        first = self.component[first]
        second = self.component[second]
        if self.root[first] != self.root[second]:
            return False
        tin = self.tin
        tout = self.tout
        first_inside = tin[child] <= tin[first] < tout[child]
        second_inside = tin[child] <= tin[second] < tout[child]
        return first_inside != second_inside

