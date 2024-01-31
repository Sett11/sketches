n,m=int(input()),int(input())
r=list(zip(*[list(map(int,input().split())) for _ in range(n)]))
i,j=map(int,input().split())
r[i],r[j]=r[j],r[i]
[print(*i) for i in list(zip(*r))]