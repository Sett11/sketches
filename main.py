from math import factorial as fack

def f(n,k):
    return fack(n)//(fack(k)*fack((n-k)))

n = int(input())
k = int(input())

print(f(n,k))