def josef(n,k):
    k-=1
    a,i=list(range(1,n+1)),k
    while len(a)>1:
        a.pop(i)
        i=(i+k)%len(a)
    return a[0]

print(josef(int(input()),int(input())))