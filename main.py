f=lambda x:sum([[i,x//i] for i in range(2,int(x**.5+1)) if x%i==0],[])

print(*sorted([[i,1+sum(set(f(i)))+i] for i in range (int(input()),int(input())+1)],key=lambda x:(x[1],x[0]))[-1])