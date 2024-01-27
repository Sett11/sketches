f1=lambda n:n>1 and all(n%i for i in range(2,int(n**.5)+1))
f2=lambda n:next(i for i in range(n+1,n+100) if f1(i))
print(f2(int(input())))