n=int(input())
c=0
a=b=1
r=[1,]
while c<n-1:
    r.append(b)
    a,b=b,a+b
    c+=1
print(*r)