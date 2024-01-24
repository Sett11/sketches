from functools import reduce as r
from operator import mul
from collections import Counter

s=input()
c=Counter(s)
a=list(map(int,s))
b=list(filter(lambda x:x>7,a))
print(c['3'],c[s[-1]],sum(map(lambda e:e[1],(filter(lambda x:int(x[0])%2==0,c.items())))),sum(filter(lambda x:x>5,a)),r(mul,b) if len(b)>1 else 1 if not b else b[0],c.get('0',0)+c.get('5',0),sep='\n')