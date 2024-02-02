n,m=map(int,input().split())
a,r,k=[i for i in range(n*m,0,-1)],[[0]*m for _ in range(n)],0
if m==1:
    print(*a[::-1],sep='\n')
if m==2:
    a=a[::-1]
    w,q=a[1:9],a[:1]+a[9:][::-1]
    r=list(zip(q,w))
    for i in r:
        print(*map(lambda x:str(x).ljust(3),i))
else:
    def f(a,n,m,k,q):
        for  i in range(k,m-k):
            if not a[k][i]:a[k][i]=q.pop()
        for i in range(k,n-k):
            if not a[i][m-1-k]:a[i][m-1-k]=q.pop()
        for i in range(m-1-k,k-1,-1):
            if not a[n-k-1][i]:a[n-k-1][i]=q.pop()
        for i in range(n-1-k,k-1,-1):
            if not a[i][k]:a[i][k]=q.pop()
        return a

    while k<n:
        r=f(r,n,m,k,a)
        k+=1

    for i in r:
        print(*map(lambda x:str(x).ljust(3),i))