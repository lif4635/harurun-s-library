"""固定幅の各連続部分列の最小値を線形時間で列挙する。"""

def sliding_window_minimum(values, width):
    values = list(values)
    if width <= 0 or width > len(values):
        return []
    queue = []
    head = 0
    result = []
    for index, value in enumerate(values):
        while len(queue) > head and values[queue[-1]] >= value:
            queue.pop()
        queue.append(index)
        if queue[head] <= index - width:
            head += 1
        if index + 1 >= width:
            result.append(values[queue[head]])
        if head > 1024 and head * 2 > len(queue):
            queue = queue[head:]
            head = 0
    return result
