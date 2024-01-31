a=[list(map(int,input().split())) for _ in range(int(input()))]
print(sum([a[i][i] for i in range(len(a))]))