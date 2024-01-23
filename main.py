from functools import reduce as r
from operator import mul
from statistics import mean

l=list(map(int,input()))
print(sum(l),len(l),r(mul,l),mean(l),l[0],l[0]+l[-1],sep='\n')