from math import gcd
from fractions import Fraction
n=int(input())
r=[]
for i in range(1,n+1):
    for j in range(1,n+1):
        if gcd(i,j)==1 and (i/j<1 or j/i<1) and i<j:
            r.append((i,j))
print(*sorted(filter(lambda y:y%1!=0,set(map(lambda x:Fraction(x[0],x[1]),r)))),sep='\n')
