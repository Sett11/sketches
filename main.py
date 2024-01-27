f=lambda n:n>1 and all(n%i for i in range(2,int(n**.5)+1))
print(f(int(input())))