from fractions import Fraction as f
from math import factorial as a
n,t=int(input()),f(1,a(1))
for i in range(2,n+1):
    t+=f(1,a(i))
print(t)