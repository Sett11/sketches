from time import time
import sys
sys.setrecursionlimit(2000)

d={0:0,1:1}

def fib_memoisation(n):
    if n in d:
        return d[n]
    r=fib_memoisation(n-1)+fib_memoisation(n-2)
    d[n]=r
    return r

def fib(n):
    def f(x):
        if x==0:
            return [0,0]
        if x==1:
            return [1,1]
        a,b=f(x//2)
        p,q=a*(2*b-a),a*a+b*b
        return [p,q] if x%2==0 else [q,p+q]
    return f(n)[0] if n>=0 else -f(-n)[0] if n%2==0 else f(-n)[0]

start1=time()
fib_memoisation(2000)
end1=time()-start1
print(end1)

start2=time()
fib(2000)
end2=time()-start2
print(end2)