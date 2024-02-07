a=[input() for _ in range(int(input()))]
t=set(a.pop(0))
for i in a:
    t&=set(i)
print(*sorted(t,key=int) if t else '')