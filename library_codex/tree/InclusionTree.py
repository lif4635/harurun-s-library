"""包含関係から親子木を構築する。"""

def inclusion_tree(intervals, universe_size=None):
    intervals = list(intervals)
    if universe_size is None:
        universe_size = max((right for _, right in intervals), default=0)
    indexed = [(-1, universe_size + 1, -1)]
    indexed.extend(
        (left, right, index)
        for index, (left, right) in enumerate(intervals)
    )
    indexed[1:] = sorted(indexed[1:], key=lambda item: (item[0], -item[1]))
    graph = [[] for _ in indexed]
    parent = [-1] * len(indexed)
    stack = [0]
    for index in range(1, len(indexed)):
        left, right, _ = indexed[index]
        while stack and indexed[stack[-1]][1] < right:
            previous = stack.pop()
            if left < indexed[previous][1]:
                raise ValueError("intervals cross")
        if not stack or not (
            indexed[stack[-1]][0] <= left
            and right <= indexed[stack[-1]][1]
        ):
            raise ValueError("interval is outside the universe")
        parent[index] = stack[-1]
        graph[stack[-1]].append(index)
        stack.append(index)
    return graph, [(left, right) for left, right, _ in indexed], [
        original for _, _, original in indexed
    ]

