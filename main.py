n,m=map(int,input().split())
a,s,b=[list(map(int,input().split())) for _ in range(n)],input(),[list(map(int,input().split())) for _ in range(n)]
for i in range(n):
    for j in range(m):
        a[i][j]+=b[i][j]
    print(*a[i])