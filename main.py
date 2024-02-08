d={}
for _ in range(int(input())):
    a,b=input().split()
    d[a]=b
    d[b]=a
print(d[input()])