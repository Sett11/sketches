n=int(input())
print(*list(zip(*[[''.join([str(k) for k in j[:k]+j[:k][::-1][1:]]) for j in sum([[[i for i in range(1,n+1)]]]*n,[])] for k in range(1,n+1)]))[0],sep='\n')