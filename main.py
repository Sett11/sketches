Kfactorial=f=lambda n,k=1:max(n,1) if n<=k or n<=1 else n*f(n-k,k)

print(Kfactorial(10,1))