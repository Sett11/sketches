f=lambda x:all(x%i for i in range(2,int(x**.5+1))) and x>=2

print(*[i for i in range(int(input()),int(input())+1) if f(i)],sep='\n')