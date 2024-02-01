n,m=map(int,input().split())
r=[['.']*m for _ in range(n)]
k=1
for i in range(n):
    for j in range(k,m,2):
        r[i][j]='*'
    k=0 if k else 1
    r[i]=' '.join(r[i])
print(*r,sep='\n')