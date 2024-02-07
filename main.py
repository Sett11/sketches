a,b=set(input().split()),set(input().split())
c=' '.join(sorted(a&b,key=int,reverse=True))
print(c if c else 'BAD DAY')