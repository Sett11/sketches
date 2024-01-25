a=[input() for _ in range(int(input()))]
c=input().lower()
print(*filter(lambda x:c in x.lower(),a),sep='\n')