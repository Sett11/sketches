def luka(a,b,n):
    while n:
        a,b=b,a+b
        n-=1
    return a

print(luka(12345,67890,5))