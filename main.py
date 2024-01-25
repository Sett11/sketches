a=[int(input()) for _ in range(int(input()))]
del a[a.index(max(a))]
del a[a.index(min(a))]
print(*a,sep='\n')