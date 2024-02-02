n,m=map(int,input().split())
a=[list(map(int,input().split())) for _ in range(n)]
input()
p,t=map(int,input().split())
b=[list(map(int,input().split())) for _ in range(p)]
c=[[sum(a[i][j]*b[j][k] for j in range(p)) for k in range(t)] for i in range(n)]
for i in c:
    print(*i)