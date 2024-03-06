a,b=map(int,input().split())
i,j,k,q=5,1,0,a
while b+i<=240 and a:
    b+=i
    j+=1
    i=j*5
    k+=1
    a-=1
print(q if not a else k)