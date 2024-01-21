a,b,n=int(input()),int(input()),int(input())
def f(a,b,n):
    if n==1:
        return a
    return f(a+b,b,n-1)
print(f(a,b,n))