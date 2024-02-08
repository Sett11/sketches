d={}
for i in range(int(input())):
    a,*b=input().lower().split()
    d[a]=b
for i in range(int(input())):
    a,b=input().lower().split()
    print(['Access denied','OK'][('x' if a[0]=='e' else a[0]) in d[b]])