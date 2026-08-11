"""指定alphabetの全長order列を1回ずつ含む巡回列を作る。"""


def de_bruijn(order, alphabet=(0, 1)):
    """alphabet上のorder次de Bruijn列を巡回部分だけ返す。"""
    if order <= 0:
        raise ValueError("order must be positive")
    alphabet = tuple(alphabet)
    if not alphabet or len(set(alphabet)) != len(alphabet):
        raise ValueError("alphabet must contain distinct symbols")
    size = len(alphabet)
    if order == 1:
        return list(alphabet)
    vertices = size ** (order - 1)
    next_symbol = [0] * vertices
    vertex_stack = [0]
    symbol_stack = []
    circuit = []
    while vertex_stack:
        vertex = vertex_stack[-1]
        symbol = next_symbol[vertex]
        if symbol < size:
            next_symbol[vertex] += 1
            vertex_stack.append((vertex * size + symbol) % vertices)
            symbol_stack.append(symbol)
        else:
            vertex_stack.pop()
            if symbol_stack:
                circuit.append(symbol_stack.pop())
    circuit.reverse()
    return [alphabet[index] for index in circuit]
