from itertools import permutations as p

n=input()
print(*list(map(lambda x:''.join(x),p(n))),sep='\n')