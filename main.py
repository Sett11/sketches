n,m=map(int,input().split())
r=list(range(1,m+1))
for i in range(n):
    print(*r)
    r.append(r.pop(0))