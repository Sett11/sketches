n,m=int(input()),int(input())
r=[['0']*m for _ in range(n)]
r[0]=' '.join(r[0]).ljust(m*3)
for i in range(1,n):
    for j in range(1,m):
        r[i][j]=str(i*j)
    r[i]=' '.join(r[i]).ljust(m*3)
print(*r,sep='\n')