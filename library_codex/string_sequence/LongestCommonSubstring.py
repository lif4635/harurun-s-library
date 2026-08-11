"""2列の最長共通substringをsuffix automatonで求める。"""


def longest_common_substring(first, second):
    """最長共通substringの長さと両方の半開区間を返す。"""
    transitions = [{}]
    link = [-1]
    length = [0]
    first_end = [-1]
    last = 0
    for position, value in enumerate(first):
        current = len(transitions)
        transitions.append({})
        length.append(length[last] + 1)
        link.append(0)
        first_end.append(position)
        state = last
        while state >= 0 and value not in transitions[state]:
            transitions[state][value] = current
            state = link[state]
        if state >= 0:
            target = transitions[state][value]
            if length[state] + 1 == length[target]:
                link[current] = target
            else:
                clone = len(transitions)
                transitions.append(transitions[target].copy())
                length.append(length[state] + 1)
                link.append(link[target])
                first_end.append(first_end[target])
                while state >= 0 and transitions[state].get(value) == target:
                    transitions[state][value] = clone
                    state = link[state]
                link[target] = link[current] = clone
        last = current

    state = matched = 0
    best = (0, (0, 0), (0, 0))
    for position, value in enumerate(second):
        while state and value not in transitions[state]:
            state = link[state]
            matched = min(matched, length[state])
        target = transitions[state].get(value)
        if target is None:
            state = matched = 0
            continue
        state = target
        matched += 1
        first_right = first_end[state] + 1
        candidate = (
            matched,
            (first_right - matched, first_right),
            (position - matched + 1, position + 1),
        )
        if candidate[0] > best[0] or (
                candidate[0] == best[0] and candidate[1:] < best[1:]):
            best = candidate
    return best
