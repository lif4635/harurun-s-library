"""両側に厳密な希望順位がある二部集合の、提案側最適な安定マッチングを求める。"""


def stable_matching(first_preferences, second_preferences):
    """first側から提案するGale--Shapley法で安定マッチングを返す。"""
    first_preferences = [list(order) for order in first_preferences]
    second_preferences = [list(order) for order in second_preferences]
    first_count = len(first_preferences)
    second_count = len(second_preferences)

    for order in first_preferences:
        if len(order) != len(set(order)):
            raise ValueError("a preference list contains a duplicate")
        if any(not 0 <= second < second_count for second in order):
            raise IndexError("a preference refers to an unknown second vertex")

    rank = []
    for order in second_preferences:
        if len(order) != len(set(order)):
            raise ValueError("a preference list contains a duplicate")
        if any(not 0 <= first < first_count for first in order):
            raise IndexError("a preference refers to an unknown first vertex")
        rank.append({first: position for position, first in enumerate(order)})

    match_first = [-1] * first_count
    match_second = [-1] * second_count
    next_choice = [0] * first_count
    free = list(range(first_count - 1, -1, -1))
    while free:
        first = free.pop()
        choices = first_preferences[first]
        while next_choice[first] < len(choices):
            second = choices[next_choice[first]]
            next_choice[first] += 1
            second_rank = rank[second]
            if first not in second_rank:
                continue
            current = match_second[second]
            if current == -1 or second_rank[first] < second_rank[current]:
                match_first[first] = second
                match_second[second] = first
                if current != -1:
                    match_first[current] = -1
                    free.append(current)
                break
    return match_first, match_second
