factorial=f=lambda n:1 if n<=1 else n*f(n-1)
sf=lambda n:1 if n<=1 else f(n)*sf(n-1)

print(f(3))
print(sf(3))