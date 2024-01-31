a=[list(map(int,input().split())) for _ in range(int(input()))]
n=len(a)
b=c=d=e=0
for i in range(n):
    for j in range(n):
        t=a[i][j]
        if i<j and i<n-1-j:
            b+=t
        if i<j and i>n-1-j:
            c+=t
        if i>j and i>n-1-j:
            d+=t
        if i>j and i<n-1-j:
            e+=t
print(f"""Верхняя четверть: {b}
Правая четверть: {c}
Нижняя четверть: {d}
Левая четверть: {e}""")