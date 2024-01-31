a=[list(map(int,input().split())) for _ in range(int(input()))]
print(*[len([j for j in i if j>sum(i)/len(i)]) for i in a],sep='\n')