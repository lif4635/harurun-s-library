"""指定頂点集合とLCAだけからvirtual treeを構築する。"""

from library_codex.tree.HeavyLightDecomposition import HeavyLightDecomposition

class AuxiliaryTree:
    __slots__ = ("tree", "hld")

    def __init__(self, tree, root=0):
        self.tree = tree
        self.hld = HeavyLightDecomposition(tree, root)

    def get(self, vertices, with_distance=False):
        vertices = list(set(vertices))
        if not vertices:
            return ([], [])
        hld = self.hld
        tin = hld.tin
        vertices.sort(key=tin.__getitem__)
        original_size = len(vertices)
        for index in range(original_size - 1):
            vertices.append(hld.lca(vertices[index], vertices[index + 1]))
        vertices = sorted(set(vertices), key=tin.__getitem__)
        index_of = {vertex: index for index, vertex in enumerate(vertices)}
        auxiliary = [[] for _ in vertices]
        stack = [vertices[0]]
        tout = hld.tout
        depth = hld.depth
        for vertex in vertices[1:]:
            while not (tin[stack[-1]] <= tin[vertex] < tout[stack[-1]]):
                stack.pop()
            parent = stack[-1]
            if with_distance:
                auxiliary[index_of[parent]].append(
                    (index_of[vertex], depth[vertex] - depth[parent])
                )
            else:
                auxiliary[index_of[parent]].append(index_of[vertex])
            stack.append(vertex)
        return auxiliary, vertices

    build = get
    query = get

