from math import log

total,n=1,int(input())

for i in range(2,n+1):
    total+=1/i

print(total-log(n))