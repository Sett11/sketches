n,m=map(int,input().split())
a=list(range(1,n*m+1))
r=[a[i:i+m] for i in range(0,n*m,m)]
for i in range(n):
    r[i]=' '.join(map(lambda x:str(x).ljust(3),r[i][::-1] if i&1 else r[i]))
    print(r[i])