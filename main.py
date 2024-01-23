n=int(input())

def f(n):
    a=[1,n]
    a+=sum([[i,n//i] for i in range(2,int(n**.5+1)) if n%i==0],[])
    return sum(set(a))

print(f(n))