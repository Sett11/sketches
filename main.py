n,k=map(int,input().split())

def f(a,b):
    if b==0:
        return 1
    if a<b:
        return 0
    return f(a-1,b)+f(a-1,b-1)

print(f(n,k))