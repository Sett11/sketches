a,b=int(input()),int(input())
print(*[i for i in range(a-(0 if a&1 else 1),b-(1 if b&1 else 0),-2)],sep='\n')