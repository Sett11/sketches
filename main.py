a,b=set(),set()
for i in range(int(input())):
    a.add(input().lower())
for i in range(int(input())):
    b.update([j for j in input().lower().split() if j not in a])
print(*list(b),sep='\n')