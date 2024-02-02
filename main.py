a=[input().split() for _ in range(int(input()))][::-1]
b=[list(i) for i in zip(*a)]
print(['NO','YES'][a==b])