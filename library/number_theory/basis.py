def calc_base(a):
    basis = []
    for bit in a:
        for base in basis:
            if bit^base < bit:
                bit ^= base
        if bit:
            """
            for i in range(len(basis)):
                if basis[i]^bit < basis[i]:
                    basis[i] ^= bit
            """
            basis.append(bit)
    return basis