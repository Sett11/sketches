from collections import Counter
s=input()
d,c={},Counter(s)
for _ in range(int(input())):
    a,b=input().split(': ')
    d[int(b)]=a
print(''.join(d[c[i]] for i in s))