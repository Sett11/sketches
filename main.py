n,m=int(input()),int(input())
r=[list(map(int,input().split())) for _ in range(n)]
k,v=max(sum(r,[])),False
for i in range(n):
    if v:
        break
    for j in range(m):
        if r[i][j]==k:
            print(i,j)
            v=True
            break