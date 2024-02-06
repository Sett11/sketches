a=[]
for i in map(int,input().split()):
    if i not in a:
        a.append(i)
        print('NO')
    else:
        print('YES')