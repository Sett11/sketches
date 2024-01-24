n,s=int(input()),['*'*19]
print(*(s+['*'+' '*17+'*' for _ in range(n-2)]+s),sep='\n')