dfactorial=f=lambda n:1 if n<=1 else n*f(n-2)

print(dfactorial(5))