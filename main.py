matrix=lambda n=1,m=None,v=0:[[v]*(m or n) for _ in range(n)]

print(matrix(3,5))