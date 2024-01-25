a,b=[input() for _ in range(int(input()))],[input() for _ in range(int(input()))]
print(*filter(lambda x:all(i.lower() in x.lower() for i in b),a),sep='\n')