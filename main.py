a=sorted(int(input()) for _ in range(3))
b=max(a[0]*a[1],a[0]+a[1])
print(max(b*a[2],b+a[2]))