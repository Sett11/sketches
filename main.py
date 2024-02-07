a,b,c=[set(input().split()) for _ in range(3)]
print(*sorted(set(map(str,range(11)))-c-b-a,key=int))