d={}
for i in range(int(input())):
    a,b=input().split(': ')
    d[a.lower()]=b
for i in range(int(input())):
    print(d.get(input().lower(),'Не найдено'))