a=list(map(int,input().split()))
i_min,i_max=a.index(min(a)),a.index(max(a))
a[i_min],a[i_max]=a[i_max],a[i_min]
print(*a)