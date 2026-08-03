"""histogramまたは0/1行列に含まれる最大長方形を求める。"""

def maximal_rectangle(heights):
    stack = []
    best = 0
    for index in range(len(heights) + 1):
        height = heights[index] if index < len(heights) else 0
        start = index
        while stack and stack[-1][0] >= height:
            previous, start = stack.pop()
            best = max(best, previous * (index - start))
        stack.append((height, start))
    return best

def maximal_rectangle_binary(matrix, truthy=True):
    if not matrix:
        return 0
    width = len(matrix[0])
    heights = [0] * width
    result = 0
    for row in matrix:
        if len(row) != width:
            raise ValueError("matrix rows must have equal length")
        for column, value in enumerate(row):
            if bool(value) == truthy:
                heights[column] += 1
            else:
                heights[column] = 0
        result = max(result, maximal_rectangle(heights))
    return result

