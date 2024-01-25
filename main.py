n=int(input())
a=[int(input()) for i in range(n)]
print([a[i]+a[i+1] for i in range(len(a)-1)])