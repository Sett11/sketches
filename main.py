n=int(input())
a,k=[['.']*n for _ in range(n)],n//2
a[k]=['*']*n
for i in range(n):
    a[i][i]=a[i][n-1-i]=a[i][k]='*'
for i in a:
    print(*i)