n=int(input())
a,k=[list(map(int,input().split())) for _ in range(n)],int(-1e9)
m=len(a[0])
for i in range(n):
    for j in range(m):
        if i>=n-j-1:
            k=max(a[i][j],k)
print(k)