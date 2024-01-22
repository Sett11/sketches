n=int(input())
print(['NO','YES'][len(str(n))==4 and any(n%i==0 for i in [7,17])])