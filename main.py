def super_L(n):
    a,b=2,1
    while n:
        a,b=b,a+b
        n-=1
    return a

print(super_L(180))