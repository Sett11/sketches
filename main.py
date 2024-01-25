s=input()
n=len(s)
print(s[-n//2+(1 if n&1 else 0):]+s[:-n//2+(1 if n&1 else 0)])