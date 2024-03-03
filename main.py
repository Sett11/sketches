from decimal import *
getcontext().prec = 50

def fi(a,b,n):
    while n>1:
        a,b=b,a+b
        n-=1
    return Decimal(b)/Decimal(a)

print(fi(0,1,11))