from functools import reduce as r
q=[set(input() for __ in range(int(input()))) for _ in range(int(input()))]
print(*sorted(r(lambda a,c:a.intersection(c),q)),sep='\n')