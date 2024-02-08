d={}
for _ in range(int(input())):
    a,b=input().lower().split()
    if b in d:
        d[b].append(a)
    else:
        d[b]=[a]
for _ in range(int(input())):
    print(*d.get(input().lower(),['абонент не найден']))