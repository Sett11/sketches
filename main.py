a=list(map(int,input().split()))
print(len([i for i in range(1,len(a)) if a[i]>a[i-1]]))