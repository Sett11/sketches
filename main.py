a=[input().split() for _ in range(int(input()))]
print(['NO','YES'][[list(i) for i in zip(*a)]==a])