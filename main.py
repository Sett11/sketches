f=lambda n:n>1 and all(n%i for i in range(2,int(n**.5)+1))
try:
    a,b,c=input().split(':')
    print(a==a[::-1] and f(int(b)) and int(c)%2==0)
except:
    print(False)