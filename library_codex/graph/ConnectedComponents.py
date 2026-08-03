"""無向グラフの連結成分番号と成分ごとの頂点を求める。"""

def connected_components(graph):
    n = len(graph)
    component = [-1] * n
    groups = []
    for start in range(n):
        if component[start] >= 0:
            continue
        component[start] = len(groups)
        group = []
        stack = [start]
        while stack:
            node = stack.pop()
            group.append(node)
            for entry in graph[node]:
                other = entry if isinstance(entry, int) else entry[0]
                if component[other] < 0:
                    component[other] = component[start]
                    stack.append(other)
        groups.append(group)
    return component, groups

