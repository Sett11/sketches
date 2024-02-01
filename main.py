n=int(input())
a=[['0']*n for _ in range(n)]
for i in range(n):
    for j in range(n):
        if (i<=j and i<=n-1-j) or (i>=j and i>=n-1-j):
            a[i][j]='1'
print(*[' '.join(map(lambda x:x.ljust(3),i)) for i in a],sep='\n')