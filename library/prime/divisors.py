def divisors(n:int) -> list[int]:
    divs_small, divs_big = [], []
    i = 1
    while i*i <= n:
        if n % i == 0:
            divs_small.append(i)
            if i != n//i:
                divs_big.append(n//i)
        i += 1
    return divs_small + divs_big[::-1]