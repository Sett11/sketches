from fractions import Fraction as f
n,t=int(input()),f(1,1**2)
for i in range(2,n+1):
    t+=f(1,i**2)
print(t)