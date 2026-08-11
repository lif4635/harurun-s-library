"""1つの集団をblocking pairのないpairへ分ける。"""


def stable_roommates(preferences):
    """完全で厳密な希望順に対するstable roommate matchingを返す。"""
    preferences = [list(row) for row in preferences]
    n = len(preferences)
    if n == 0:
        return []
    if n & 1:
        return None
    expected = set(range(n))
    for person, row in enumerate(preferences):
        if len(row) != n - 1 or set(row) != expected - {person}:
            raise ValueError("each preference row must rank every other person once")

    rank = [[0] * n for _ in range(n)]
    for person, row in enumerate(preferences):
        for position, other in enumerate(row):
            rank[person][other] = position
    exists = [bytearray(b"\x01") * n for _ in range(n)]
    for person in range(n):
        exists[person][person] = 0
    left = [0] * n
    right = [n - 1] * n
    proposed_to = [-1] * n
    proposal_from = [-1] * n

    def clip(person):
        row = preferences[person]
        while left[person] < right[person] and not exists[person][row[left[person]]]:
            left[person] += 1
        while left[person] < right[person] and not exists[person][row[right[person] - 1]]:
            right[person] -= 1

    queue = list(range(n))
    while True:
        while queue:
            person = queue.pop()
            while True:
                clip(person)
                if left[person] == right[person]:
                    return None
                other = preferences[person][left[person]]
                current = proposal_from[other]
                if current >= 0 and rank[other][person] > rank[other][current]:
                    exists[person][other] = exists[other][person] = 0
                    left[person] += 1
                    continue
                if current >= 0:
                    exists[current][other] = exists[other][current] = 0
                    proposed_to[current] = -1
                    proposal_from[other] = -1
                    queue.append(current)
                proposed_to[person] = other
                proposal_from[other] = person
                while preferences[other][right[other] - 1] != person:
                    right[other] -= 1
                    rejected = preferences[other][right[other]]
                    exists[other][rejected] = exists[rejected][other] = 0
                break

        start = -1
        for person in range(n):
            clip(person)
            if right[person] - left[person] > 1:
                start = person
                break
        if start < 0:
            break

        def next_rotation(person):
            clip(person)
            first = preferences[person][left[person]]
            left[person] += 1
            clip(person)
            left[person] -= 1
            preferences[person][left[person]] = first
            return proposal_from[preferences[person][left[person] + 1]]

        slow = next_rotation(start)
        fast = next_rotation(next_rotation(start))
        while slow != fast:
            slow = next_rotation(slow)
            fast = next_rotation(next_rotation(fast))
        cycle = [slow]
        person = next_rotation(slow)
        while person != slow:
            cycle.append(person)
            person = next_rotation(person)
        for person in cycle:
            other = proposed_to[person]
            proposal_from[other] = -1
            proposed_to[person] = -1
            exists[person][other] = exists[other][person] = 0
            queue.append(person)

    if any(other < 0 or proposed_to[other] != person
           for person, other in enumerate(proposed_to)):
        return None
    return proposed_to
