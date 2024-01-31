a=[input().split() for _ in range(int(input()))]
n,f=len(a),lambda x:[list(i) for i in zip(*x)]
a=f(a)
for i in range(n):
    a[i][i],a[i][n-1-i]=a[i][n-1-i],a[i][i]
print(*[' '.join(i) for i in f(a)],sep='\n')