n,i,j=int(input()),1,0
while n>=1:
    n-=i
    j+=1
    i+=j
print(j-1 or 1)

from bisect import insort
r,f=[],lambda:[insort(r,int(i)) for i in input().split()]
input() and f() and f()
print(*r)