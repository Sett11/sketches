def trib(n):
    a=[1,1,1]
    while n:
        a.append(sum(a[-3:]))
        n-=1
    return a

print(trib(10))