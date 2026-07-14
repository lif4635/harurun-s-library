def simplify_permutation_subgroup(n, permutations, force_size_n=True):
    """Return a stabilizer-chain transversal for a generated subgroup."""
    if n < 1:
        raise ValueError("n must be positive")
    identity = list(range(n))
    for permutation in permutations:
        if len(permutation) != n or sorted(permutation) != identity:
            raise ValueError("every generator must be a permutation of range(n)")

    elimination = [[None] * index for index in range(n)]

    def insert(permutation, size, table):
        next_permutation = permutation[:]
        for pivot in range(size - 1, 0, -1):
            image = permutation[pivot]
            if image == pivot:
                continue
            target = table[pivot][image]
            if target is None:
                table[pivot][image] = permutation
                return
            for index in range(size):
                next_permutation[target[index]] = index
            for index in range(size):
                permutation[index] = next_permutation[permutation[index]]

    for permutation in permutations:
        insert(list(permutation), n, elimination)

    result = [[] for _ in range(n)]
    for fixed in range(n - 1, 0, -1):
        orbit = [None] * (fixed + 1)
        bfs = [fixed]
        orbit[fixed] = list(range(fixed + 1))
        scan = 0
        while scan < len(bfs):
            source = bfs[scan]
            scan += 1
            for pivot in range(source, fixed + 1):
                for permutation in elimination[pivot]:
                    if permutation is None:
                        continue
                    destination = permutation[source]
                    if orbit[destination] is None:
                        orbit[destination] = [
                            permutation[orbit[source][index]]
                            for index in range(fixed + 1)
                        ]
                        bfs.append(destination)

        inverse_orbit = [None] * (fixed + 1)
        for image in range(fixed + 1):
            permutation = orbit[image]
            if permutation is not None:
                inverse = [0] * (fixed + 1)
                for index, value in enumerate(permutation):
                    inverse[value] = index
                inverse_orbit[image] = inverse

        old = elimination
        elimination = [[None] * (index + 1) for index in range(fixed + 1)]
        for pivot in range(1, fixed + 1):
            for permutation in old[pivot]:
                if permutation is None:
                    continue
                for image in bfs:
                    inverse = inverse_orbit[permutation[image]]
                    transported = [
                        inverse[permutation[orbit[image][index]]]
                        for index in range(fixed)
                    ]
                    insert(transported, fixed, elimination)

        for image in bfs:
            permutation = orbit[image]
            if force_size_n:
                extended = list(range(n))
                extended[:fixed + 1] = permutation
                result[fixed].append(extended)
            else:
                result[fixed].append(permutation)
    return result


SimplifyPermutationSubgroup = simplify_permutation_subgroup

