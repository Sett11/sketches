a=[input() for _ in range(int(input()))]
b,n=a[::-1],len(a)
if n>2:b[n//2],b[0]=b[0],b[n//2]
print(*[f'{a[i]} - {b[i]}' for i in range(n)],sep='\n')