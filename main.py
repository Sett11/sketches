n,m=map(int,input().split())
r=list(range(1,n*m+1))
print(*[' '.join(map(lambda x:str(x).ljust(3),r[i:i+m])) for i in range(0,len(r),m)],sep='\n')