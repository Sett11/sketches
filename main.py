n=int(input())
a=[1]*3
while len(a)<n:
    a.append(a[-1]+a[-2]+a[-3])
a=a[:n]
print(*a)