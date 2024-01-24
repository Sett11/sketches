f=lambda x:sum([[i,x//i] for i in range(2,int(x**.5+1)) if x%i==0],[])

print(*[f"{i}{'+'*(len(set(f(i)))+(1 if i==1 else 2))}" for i in range(1,int(input())+1)],sep='\n')