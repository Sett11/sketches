a,b,c=[set(input().split()) for _ in range(3)]
print(*sorted(c-b-a,key=int,reverse=True))