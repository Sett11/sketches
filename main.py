n,m=int(input()),int(input())
a=[input() for _ in range(n)]
for _ in range(m):
    if input() in a:
        print('YES')
    else:
        print('NO')