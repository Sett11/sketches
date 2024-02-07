a=[input() for _ in range(int(input())+int(input()))]
print(len(set(a))-(len(a)-len(set(a))) or 'NO')