n=int(input())
a=[['0']*n for _ in range(n)]
for i in range(n):
    a[i][i]=a[i][n-1-i]='1'
    a[i]=' '.join(a[i])
print(*a,sep='\n')