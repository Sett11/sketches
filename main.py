a,m=[[-3, 1, 4, -3],
     [-9, -3, -3, -10],
     [-4, -3, -3, -2],
     [-3, 0, 0, -3]],-100#[list(map(int,input().split())) for _ in range(int(input()))],-100
n,k=len(a),1
r,q=[],[]
for i in range(n):
    t,w=[],[]
    for j in range(k):
        #m=max(a[i][j],a[i][::-1][j],m)
        t.append(a[i][j])
        w.append(a[i][::-1][j])
    k=1 if i==n-2 else k+1 if i<n//2 and i!=n-1 else k-1
    r.append(t)
    q.append(w)
print(r,q)