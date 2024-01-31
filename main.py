a,m=[list(map(int,input().split())) for _ in range(int(input()))],float('-inf')
for i in range(len(a)):
    for j in range(i+1):
        m=max(a[i][j],m)
print(m)