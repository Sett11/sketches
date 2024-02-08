d={}
for i in range(int(input())):
    a,*b=input().split()
    d[a]=b
for i in range(int(input())):
    p=input()
    for j in d:
        if p in d[j]:
            print(j)
            break