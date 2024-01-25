from string import ascii_lowercase as a

n=int(input())
print(*[a[a.index(i)-n] for i in input()],sep='')