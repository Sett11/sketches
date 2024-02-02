a=[input().split() for _ in range(int(input()))]
b=[tuple(sorted(i)) for i in zip(*a)]
c=[tuple(sorted(i)) for i in a]+b
print(['NO','YES'][len(set(c))==1 and all(len(i)==len(set(i)) for i in c)])