d={}
for _ in range(int(input())):
    a,*b=input().split()
    if a in d:
        if b[0] in d[a]:
            d[a][b[0]]+=int(b[1])
        else:
            d[a][b[0]]=int(b[1])
    else:
        d[a]={b[0]:int(b[1])}
for i in sorted(d):
    t=sorted(d[i])
    print(f'{i}:')
    for j in t:
        print(j,d[i][j])