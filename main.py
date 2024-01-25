from itertools import zip_longest
print(*list(zip_longest(*[input() for _ in range(int(input()))],fillvalue=''))[int(input())-1],sep='')