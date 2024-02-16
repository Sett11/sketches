from math import gcd
n=int(input())
r=[]
for i in range(1,n):
    for j in range(i+1,n):
        if gcd(i,j)==1 and i+j==n:
            r.append((i,j))
print(f'{r[-1][0]}/{r[-1][1]}')