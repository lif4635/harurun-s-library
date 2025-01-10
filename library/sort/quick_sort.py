def quick_sort(lst, comparision, left = 0, right = -1):
    if len(lst) == 0: return
    if right == -1: right %= len(lst)
    i = left
    j = right
    pivot = (i+j)//2
    dpivot = lst[pivot]

    while True:
        while comparision(lst[i],dpivot) < 0: i += 1
        while comparision(dpivot,lst[j]) < 0: j -= 1
        if i >= j: break

        lst[i],lst[j] = lst[j],lst[i]
        i += 1
        j -= 1
    
    if left < i-1: quick_sort(lst, comparision, left, i-1)
    if right > j+1: quick_sort(lst, comparision, j+1, right)
