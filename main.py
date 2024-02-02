n=int(input())
a=b=[list(map(int,input().split())) for _ in range(n)]
m=int(input())
while m>1:
    a=[[sum(a[i][j]*b[j][k] for j in range(n)) for k in range(n)] for i in range(n)]
    m-=1
for i in a:
    print(*i)