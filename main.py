a,r=input().split(),[[]]
n=len(a)
for i in range(n):
    for j in range(i,n+1):
        t=a[i:j]
        r.append(t) if t else None
print(sorted(r,key=len))