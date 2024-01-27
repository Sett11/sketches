def f(a,b):
    return sorted(a+b)

a = [int(c) for c in input().split()]
b = [int(c) for c in input().split()]

print(f(a, b))