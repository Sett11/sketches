a,b=input().split(),input().split()
print(*sorted(set(a)-set(b),key=int))