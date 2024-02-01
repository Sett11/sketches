n=int(input())
a=[['&']*n for _ in range(n)]
for i in range(n):
    h=n-1-i
    a[i][h]=1
    for j in range(h):
        a[i][j]=0
    for k in range(h+1,n):
        a[i][k]=2
    a[i]=' '.join(map(str,a[i]))
print(*a,sep='\n')