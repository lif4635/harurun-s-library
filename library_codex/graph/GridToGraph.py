"""通行可能なgridを隣接listへ変換する。"""

def grid_to_graph(grid, passable=lambda value: value != "#"):
    """Return a 4-neighbor adjacency list and coordinate/ID helpers."""
    height = len(grid)
    width = len(grid[0]) if height else 0
    graph = [[] for _ in range(height * width)]
    for row in range(height):
        for column in range(width):
            if not passable(grid[row][column]):
                continue
            vertex = row * width + column
            if row and passable(grid[row - 1][column]):
                graph[vertex].append(vertex - width)
            if row + 1 < height and passable(grid[row + 1][column]):
                graph[vertex].append(vertex + width)
            if column and passable(grid[row][column - 1]):
                graph[vertex].append(vertex - 1)
            if column + 1 < width and passable(grid[row][column + 1]):
                graph[vertex].append(vertex + 1)
    return (graph, (lambda row, column: row * width + column),
            (lambda vertex: divmod(vertex, width)))

