n=int(input())
a=[[int(j) for j in input().split()] for _ in range(n)]
print(['NO','YES'][len(set([sum(i) for i in a]+[sum(i) for i in list(zip(*a))]+[sum([a[i][i] for i in range(n)])]+[sum([a[i][n-1-i] for i in range(n)])]))==1 and len(set(sum(a,[])))==n*n and all(i for i in sum(a,[]))])