a,b,c=[set(input().split()) for _ in range(3)]
print(*sorted(a&b-c,key=int,reverse=True))