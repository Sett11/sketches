m,n=map(int,input().split())
a=list(range(1,n*m+1))
r=[' '.join(map(lambda x:str(x).ljust(3),j)) for j in zip(*[a[i:i+m] for i in range(0,len(a),m)])]
print(*r,sep='\n')